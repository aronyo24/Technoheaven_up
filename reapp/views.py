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

from message.models import Blog, Comment, News
from publication_project.models import Publication, Project, Resource, Client, Service


from visitors_details.models import Visitor

from .forms import (
    RegisterForm,
    BlogSubmissionForm,
    AccountIdentityForm,
    AccountProfileForm,
)
from .models import UserProfile


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



def register_view(request):
    if request.user.is_authenticated:
        return redirect('user_dashboard')

    form_errors = []
    form = RegisterForm()
    form_data = {
        'name': '',
        'username': '',
        'email': '',
        'country': '',
        'age': '',
        'gender': '',
        'contact': '',
        'terms': False,
    }

    if request.method == 'POST':
        form_data.update({
            'name': request.POST.get('name', '').strip(),
            'username': request.POST.get('username', '').strip(),
            'email': request.POST.get('email', '').strip(),
            'country': request.POST.get('country', '').strip(),
            'age': request.POST.get('age', '').strip(),
            'gender': request.POST.get('gender', '').strip(),
            'contact': request.POST.get('contact', '').strip(),
            'terms': request.POST.get('terms') is not None,
        })

        full_name = form_data['name']
        name_parts = full_name.split()
        first_name = name_parts[0] if name_parts else ''
        last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''

        form_payload = {
            'username': form_data['username'],
            'first_name': first_name,
            'last_name': last_name,
            'email': form_data['email'],
            'password1': request.POST.get('password', ''),
            'password2': request.POST.get('confirm_password', ''),
        }
        form = RegisterForm(form_payload)

        if not full_name:
            form.add_error(None, 'Full name is required.')
        if not form_data['country']:
            form.add_error(None, 'Country is required.')
        if not request.POST.get('terms'):
            form.add_error(None, 'Please agree to the terms of collaboration to continue.')

        if form_data['email']:
            user_model = form._meta.model
            if user_model.objects.filter(email__iexact=form_data['email']).exists():
                form.add_error('email', 'An account with this email already exists.')

        age_value = form_data['age']
        if age_value:
            try:
                age_int = int(age_value)
                if age_int < 0:
                    raise ValueError
            except (TypeError, ValueError):
                form.add_error(None, 'Age must be a positive number.')
            else:
                form_data['age'] = str(age_int)

        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save()
                    if first_name or last_name:
                        user.first_name = first_name
                        user.last_name = last_name
                        user.save(update_fields=['first_name', 'last_name'])

                    age = int(form_data['age']) if form_data['age'] else None
                    gender_value = form_data['gender'] if form_data['gender'] in dict(UserProfile.GENDER_CHOICES) else ''

                    UserProfile.objects.create(
                        user=user,
                        full_name=full_name or user.get_full_name() or user.username,
                        country=form_data['country'],
                        age=age,
                        gender=gender_value,
                        contact_number=form_data['contact'],
                        terms_accepted=form_data['terms'],
                    )
                login(request, user)
                messages.success(request, 'Welcome aboard! Your Technoheaven workspace is ready.')
                return redirect('user_dashboard')
            except Exception:
                form.add_error(None, 'We could not complete your registration. Please try again.')

        form_errors = _format_form_errors(form)

    context = {
        'form': form,
        'form_data': form_data,
        'form_errors': form_errors,
    }

    return render(request, 'auth/register.html', context)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('user_dashboard')

    next_url = request.GET.get('next', '')
    form = AuthenticationForm(request, data=request.POST or None)
    form_errors = []
    form_data = {'username': ''}

    if request.method == 'POST':
        form_data['username'] = request.POST.get('username', '').strip()

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Signed in successfully.')
            return redirect(next_url or 'user_dashboard')

        form_errors = _format_form_errors(form)
        messages.error(request, 'We could not sign you in with those credentials.')
    else:
        form_data['username'] = request.GET.get('username', '').strip()

    context = {
        'form': form,
        'next': next_url,
        'form_data': form_data,
        'form_errors': form_errors,
    }

    return render(request, 'auth/login.html', context)


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
