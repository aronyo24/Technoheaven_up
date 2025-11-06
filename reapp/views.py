from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.db import transaction
from django.db.models import Sum

from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from message import models
from message.models import Blog, Comment, News
from publication_project.models import Publication, Project, Resource, Client, Service
from django.contrib.auth.models import User


from visitors_details.models import Visitor

from authapp.forms import (
    BlogSubmissionForm,
    AccountIdentityForm,
    AccountProfileForm,
)
from authapp.models import UserProfile


BLOG_STATUS_DESCRIPTIONS = {
    'pending': 'Awaiting moderator review',
    'published': 'Live on the public blog',
    'rejected': 'Needs updates before it can go live',
}


def _format_timestamp(value, fmt):
    if not value:
        return None
    if timezone.is_naive(value):
        value = timezone.make_aware(value, timezone.get_current_timezone())
    return timezone.localtime(value).strftime(fmt)


def _format_form_errors(form):
    """Return a flat list of human readable form errors."""

    formatted = []
    for field, errors in form.errors.items():
        if field == "__all__":
            formatted.extend(errors)
            continue
        label = form.fields.get(field).label if field in form.fields else field.replace("_", " ").capitalize()
        for error in errors:
            formatted.append(f"{label}: {error}")
    return formatted

def home(request):
    # Get visitor's public and private IPs
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    public_ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
    private_ip = request.META.get('REMOTE_ADDR')

    # Get the user agent
    user_agent = request.META.get('HTTP_USER_AGENT', '')

    # Check if visitor already exists by user_agent
    visitor, created = Visitor.objects.get_or_create(user_agent=user_agent)

    if created:
        # If new, fetch the public IP, private IP, and update location
        visitor.ip_address = public_ip
        visitor.private_ip = private_ip
        visitor.update_location()
        visitor.visit_count = 1  # Set initial visit count to 1
        visitor.last_visit = timezone.now()  # Set the last visit time
    else:
        # If existing, update visit count and last visit time
        visitor.visit_count += 1
        visitor.last_visit = timezone.now()

    visitor.save()  # Save changes to the database

    # Total number of visitors
    total_visitors = Visitor.objects.count()

    # Total number of visits across all visitors
    total_visits = Visitor.objects.aggregate(total=Sum('visit_count'))['total']

    # Last month's visits
    one_month_ago = timezone.now() - timedelta(days=30)
    last_month_visits = Visitor.objects.filter(last_visit__gte=one_month_ago).aggregate(
        total=Sum('visit_count')
    )['total']

    publications = Publication.objects.all().order_by('-id')
    news = News.objects.all()

    # Data for rendering
    data = {
        'publications': publications,
        'news': news,
        'total_visitors': total_visitors,
        'total_visits': total_visits,
        'last_month_visits': last_month_visits,
    }

    return render(request, 'index.html', data)






def about(request):
    return render(request, 'about.html')


def contact(request):
    return render(request, 'contact.html')






@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been signed out.')
    return redirect('login')


@login_required
def user_dashboard(request):
    """Render the authenticated user's workspace overview."""

    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = None

    display_name = (
        (profile.full_name if profile and profile.full_name else None)
        or request.user.get_full_name()
        or request.user.username
    )

    if profile:
        profile_fields = [profile.country, profile.contact_number, profile.age, profile.gender]
        completed_fields = sum(1 for field in profile_fields if field not in (None, "", 0))
        profile_completion = int(round((completed_fields / len(profile_fields)) * 100)) if profile_fields else 0
    else:
        profile_completion = 0

    last_login_display = _format_timestamp(request.user.last_login, '%b %d, %Y %H:%M') or 'Not recorded yet'
    member_since_display = _format_timestamp(request.user.date_joined, '%b %d, %Y') or ''

    metrics = {
        'publications': Publication.objects.count(),
        'projects': Project.objects.count(),
        'resources': Resource.objects.count(),
        'clients': Client.objects.count(),
        'services': Service.objects.count(),
    }

    recent_publications = Publication.objects.order_by('-id')[:4]
    recent_news = News.objects.order_by('-date')[:3]

    user_blogs_qs = Blog.objects.filter(submitted_by=request.user).order_by('-updated_at')
    blog_counts = {
        'total': user_blogs_qs.count(),
        'pending': user_blogs_qs.filter(status='pending').count(),
        'published': user_blogs_qs.filter(status='published').count(),
        'rejected': user_blogs_qs.filter(status='rejected').count(),
    }

    user_blogs = []
    for blog in user_blogs_qs:
        blog.status_description = BLOG_STATUS_DESCRIPTIONS.get(blog.status, '')
        blog.can_edit = True
        blog.can_view_live = blog.status == 'published'
        user_blogs.append(blog)

    account_meta = [
        {
            'icon': 'fa-clock-rotate-left',
            'label': 'Last login',
            'value': last_login_display,
            'caption': 'Keep your credentials protected.',
            'progress': None,
        },
        {
            'icon': 'fa-calendar-check',
            'label': 'Member since',
            'value': member_since_display,
            'caption': 'Your Technoheaven journey so far.',
            'progress': None,
        },
        {
            'icon': 'fa-user-check',
            'label': 'Profile completion',
            'value': f"{profile_completion}%",
            'caption': 'Complete your profile for tailored insights.',
            'progress': profile_completion,
        },
    ]

    context = {
        'profile': profile,
        'display_name': display_name,
        'metrics': metrics,
        'recent_publications': recent_publications,
        'recent_news': recent_news,
        'user_blogs': user_blogs,
        'blog_counts': blog_counts,
        'status_descriptions': BLOG_STATUS_DESCRIPTIONS,
        'account_meta': account_meta,
        'profile_completion': profile_completion,
    }

    return render(request, 'dashboard.html', context)


@login_required
def submit_blog(request):
    form = BlogSubmissionForm(request.POST or None, request.FILES or None)

    if request.method == 'POST':
        if form.is_valid():
            blog = form.save(commit=False)
            blog.submitted_by = request.user
            blog.status = 'pending'
            blog.save()
            messages.success(request, 'Thanks for sharing! Your blog is queued for editorial review.')
            return redirect('user_dashboard')

        messages.error(request, 'We could not submit your blog. Please address the highlighted fields and try again.')

    context = {
        'form': form,
        'is_edit': False,
    }

    return render(request, 'blog_submission_form.html', context)


@login_required
def edit_blog(request, slug):
    blog = get_object_or_404(Blog, slug=slug, submitted_by=request.user)

    form = BlogSubmissionForm(request.POST or None, request.FILES or None, instance=blog)
    previous_status = blog.status
    blog.status_description = BLOG_STATUS_DESCRIPTIONS.get(blog.status, '')

    if request.method == 'POST':
        if form.is_valid():
            updated_blog = form.save(commit=False)
            # any edit triggers a fresh review cycle
            updated_blog.status = 'pending'
            updated_blog.submitted_at = timezone.now()
            updated_blog.save()

            if previous_status == 'published':
                messages.info(
                    request,
                    'Your updates were saved. The article is offline until the editorial team approves the new version.'
                )
            elif previous_status == 'rejected':
                messages.success(request, 'Great! The blog was resubmitted for review. We will notify you after approval.')
            else:
                messages.success(request, 'Changes saved. Your post remains in the review queue.')

            return redirect('user_dashboard')

        messages.error(request, 'Please resolve the issues below so we can resubmit your story.')

    context = {
        'form': form,
        'is_edit': True,
        'blog': blog,
        'previous_status': previous_status,
    }

    return render(request, 'blog_submission_form.html', context)


@login_required
def edit_profile(request):
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = None

    profile_instance = profile if profile else UserProfile(user=request.user)

    if request.method == 'POST':
        identity_form = AccountIdentityForm(request.POST, instance=request.user)
        profile_form = AccountProfileForm(request.POST, request.FILES, instance=profile_instance)

        if identity_form.is_valid() and profile_form.is_valid():
            with transaction.atomic():
                identity_form.save()
                profile_obj = profile_form.save(commit=False)
                profile_obj.user = request.user
                profile_obj.save()

            messages.success(request, 'Your profile details were updated successfully.')
            return redirect('user_dashboard')

        messages.error(request, 'Update failed. Please review the highlighted fields below.')
    else:
        identity_form = AccountIdentityForm(instance=request.user)
        initial_profile = {}
        if not profile:
            initial_profile['full_name'] = request.user.get_full_name() or request.user.username
        profile_form = AccountProfileForm(instance=profile_instance, initial=initial_profile)

    context = {
        'identity_form': identity_form,
        'profile_form': profile_form,
        'has_profile': profile is not None,
    }

    return render(request, 'profile_form.html', context)


@login_required
def change_password(request):
    form = PasswordChangeForm(user=request.user, data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password updated. You are still logged in on this device.')
            return redirect('user_dashboard')

        messages.error(request, 'We could not update your password. Please fix the issues below and try again.')

    context = {
        'form': form,
    }

    return render(request, 'password_change_form.html', context)
