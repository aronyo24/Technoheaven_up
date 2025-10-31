from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction
from django.db.models import Sum
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from message.models import Blog, Comment, News
from publication_project.models import Publication, Project, Resource, Client, Service
from session.models import Session
from team_gallary.models import Team, Gallery
from visitors_details.models import Visitor

from .forms import RegisterForm, BlogSubmissionForm
from .models import UserProfile


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

def services(request):
    # load services and group them by category (preserves defined order)
    services_qs = Service.objects.all()
    categories = []
    for value, label in Service.SERVICE_CATEGORIES:
        categories.append({
            'value': value,
            'label': label,
            'services': services_qs.filter(category=value)
        })

    return render(request, 'services.html', {'categories': categories})

def service_detail(request, slug):
    service = get_object_or_404(Service, slug=slug)
    return render(request, 'services_de.html', {'service': service})

def contact(request):
    return render(request, 'contact.html')


def clients(request):
    clients = Client.objects.all()
    return render(request, 'clients.html', {'clients': clients})


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
def submit_blog(request):
    if request.method == 'POST':
        form = BlogSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.submitted_by = request.user
            blog.status = 'pending'
            if not blog.author:
                full_name = request.user.get_full_name()
                blog.author = full_name if full_name else request.user.username
            blog.date = timezone.now().date()
            blog.save()
            messages.success(request, 'Thanks for your submission! Our team will review it shortly.')
            return redirect('user_dashboard')
    else:
        form = BlogSubmissionForm()

    return render(request, 'blog_submit.html', {'form': form})


@login_required
def user_dashboard(request):
    user_blogs = Blog.objects.filter(submitted_by=request.user).order_by('-submitted_at')
    counts = {
        'published': user_blogs.filter(status='published').count(),
        'pending': user_blogs.filter(status='pending').count(),
        'rejected': user_blogs.filter(status='rejected').count(),
    }

    context = {
        'user_blogs': user_blogs,
        'counts': counts,
    }
    return render(request, 'dashboard.html', context)


@login_required
def delete_blog(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    if not (request.user.is_staff or blog.submitted_by_id == request.user.id):
        raise Http404

    if request.method == 'POST':
        blog.delete()
        messages.success(request, 'Blog removed successfully.')
        redirect_target = 'pending_blogs' if request.user.is_staff else 'user_dashboard'
        return redirect(redirect_target)

    return render(request, 'blog_confirm_delete.html', {'blog': blog})


@login_required
def pending_blogs(request):
    if not request.user.is_staff:
        raise Http404

    pending = Blog.objects.filter(status='pending').order_by('-submitted_at')
    rejected = Blog.objects.filter(status='rejected').order_by('-submitted_at')
    context = {
        'pending_blogs': pending,
        'rejected_blogs': rejected,
    }
    return render(request, 'blog_moderation.html', context)


@login_required
def approve_blog(request, pk):
    if not request.user.is_staff:
        raise Http404

    blog = get_object_or_404(Blog, pk=pk)
    blog.status = 'published'
    blog.date = timezone.now().date()
    blog.save()
    messages.success(request, f"'{blog.title}' is now live!")
    return redirect('pending_blogs')


@login_required
def reject_blog(request, pk):
    if not request.user.is_staff:
        raise Http404

    blog = get_object_or_404(Blog, pk=pk)
    blog.status = 'rejected'
    blog.save()
    messages.warning(request, f"'{blog.title}' has been marked as rejected.")
    return redirect('pending_blogs')
