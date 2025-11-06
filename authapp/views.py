from datetime import timedelta
import random

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.db import transaction

from .models import UserProfile

OTP_LENGTH = 6
OTP_EXPIRATION_MINUTES = 15
OTP_RESEND_WAIT_MINUTES = 5


def _format_form_errors(form):
    """Return a flat list of human readable form errors (local copy to avoid circular imports)."""
    formatted = []
    for field, errors in form.errors.items():
        if field == "__all__":
            formatted.extend(errors)
            continue
        label = form.fields.get(field).label if field in form.fields else field.replace("_", " ").capitalize()
        for error in errors:
            formatted.append(f"{label}: {error}")
    return formatted


def _issue_otp_and_send_email(request, user):
    """Generate a fresh OTP and email it along with an activation link; return (code, expires_at)."""

    otp_code = f"{random.randint(0, 10 ** OTP_LENGTH - 1):0{OTP_LENGTH}d}"
    expires_at = timezone.now() + timedelta(minutes=OTP_EXPIRATION_MINUTES)

    current_site = get_current_site(request)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    activate_link = request.build_absolute_uri(
        reverse('activate', kwargs={'uidb64': uid, 'token': token})
    )
    message = render_to_string(
        'activation_email.html',
        {
            'user': user,
            'activate_link': activate_link,
            'otp_code': otp_code,
            'domain': current_site.domain,
        },
    )
    email_msg = EmailMessage('Activate Your Account / OTP', message, to=[user.email])
    email_msg.content_subtype = 'html'
    email_msg.send()

    return otp_code, int(expires_at.timestamp())


def _issue_password_reset_otp(request, user):
    """Send a password reset OTP email and return (code, expires_at)."""

    otp_code = f"{random.randint(0, 10 ** OTP_LENGTH - 1):0{OTP_LENGTH}d}"
    expires_at = timezone.now() + timedelta(minutes=OTP_EXPIRATION_MINUTES)

    current_site = get_current_site(request)
    message = render_to_string(
        'password_reset_email.html',
        {
            'user': user,
            'otp_code': otp_code,
            'domain': current_site.domain,
            'expiry_minutes': OTP_EXPIRATION_MINUTES,
        },
    )

    email_msg = EmailMessage('Password Reset OTP', message, to=[user.email])
    email_msg.content_subtype = 'html'
    email_msg.send()

    return otp_code, int(expires_at.timestamp())






def register_view(request):
    if request.user.is_authenticated:
        return redirect('user_dashboard')

    errors = []
    form_data = {
        'name': '',
        'first_name': '',
        'last_name': '',
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
            'first_name': request.POST.get('first_name', '').strip(),
            'last_name': request.POST.get('last_name', '').strip(),
            'username': request.POST.get('username', '').strip(),
            'email': request.POST.get('email', '').strip(),
            'country': request.POST.get('country', '').strip(),
            'age': request.POST.get('age', '').strip(),
            'gender': request.POST.get('gender', '').strip(),
            'contact': request.POST.get('contact', '').strip(),
            'terms': request.POST.get('terms') is not None,
        })

        full_name = form_data['name'] or (form_data['first_name'] + (' ' + form_data['last_name'] if form_data['last_name'] else ''))
        if not full_name:
            errors.append('Full name is required.')
        if not form_data['username']:
            errors.append('Username is required.')
        if not form_data['email']:
            errors.append('Email is required.')
        if not form_data['country']:
            errors.append('Country is required.')
        if not form_data['terms']:
            errors.append('Please agree to the terms of collaboration to continue.')

        password = request.POST.get('password', '')
        password2 = request.POST.get('confirm_password', '')
        if not password or not password2:
            errors.append('Password and confirmation are required.')
        elif password != password2:
            errors.append('Passwords do not match.')
        elif len(password) < 8:
            errors.append('Password must be at least 8 characters long.')

        # Uniqueness checks
        if form_data['username'] and User.objects.filter(username__iexact=form_data['username']).exists():
            errors.append('An account with this username already exists.')
        if form_data['email'] and User.objects.filter(email__iexact=form_data['email']).exists():
            errors.append('An account with this email already exists.')

        # Age validation
        if form_data['age']:
            try:
                age_int = int(form_data['age'])
                if age_int < 0:
                    raise ValueError
            except (TypeError, ValueError):
                errors.append('Age must be a positive number.')
            else:
                form_data['age'] = str(age_int)

        allowed_genders = {g for g, _ in UserProfile.GENDER_CHOICES}
        if form_data['gender'] and form_data['gender'] not in allowed_genders:
            errors.append('Invalid gender selection.')

        if not errors:
            try:
                with transaction.atomic():
                    first_name = form_data['first_name'] or full_name.split(' ')[0]
                    last_name = form_data['last_name'] or ' '.join(full_name.split(' ')[1:])
                    user = User.objects.create_user(
                        username=form_data['username'],
                        email=form_data['email'],
                        password=password,
                        first_name=first_name,
                        last_name=last_name,
                    )
                    # Require email verification before login
                    user.is_active = False
                    user.save(update_fields=['is_active'])

                    age = int(form_data['age']) if form_data['age'] else None
                    UserProfile.objects.create(
                        user=user,
                        full_name=full_name or user.get_full_name() or user.username,
                        country=form_data['country'],
                        age=age,
                        gender=form_data['gender'] or '',
                        contact_number=form_data['contact'],
                        terms_accepted=form_data['terms'],
                    )
            except Exception:
                errors.append('We could not complete your registration. Please try again.')
            else:
                # Issue OTP and store in session
                code, expires_at = _issue_otp_and_send_email(request, user)
                request.session['pending_user_id'] = user.pk
                request.session['pending_otp'] = code
                request.session['pending_otp_expires'] = expires_at
                request.session['pending_otp_last_sent'] = int(timezone.now().timestamp())
                messages.success(request, 'Account created! Enter the OTP sent to your email to verify your account.')
                return redirect('verify_otp')

    context = {
        'form_data': form_data,
        'form_errors': errors,
    }
    return render(request, 'register.html', context)


def activate_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Your account has been activated! You can now log in.')
        return redirect('login')
    else:
        return render(request, 'activation_invalid.html')


def verify_otp_view(request):
    """Allow the user to submit the OTP code they received by email (session-based)."""
    pending_user_id = request.session.get('pending_user_id')
    if not pending_user_id:
        messages.error(request, 'No pending verification found. Please register first.')
        return redirect('register')

    try:
        user = User.objects.get(pk=pending_user_id)
    except User.DoesNotExist:
        messages.error(request, 'User not found. Please register again.')
        return redirect('register')

    # Prepare UI context
    last_sent_ts = int(request.session.get('pending_otp_last_sent') or 0)
    expires_ts = int(request.session.get('pending_otp_expires') or 0)
    now_ts = int(timezone.now().timestamp())
    wait_window = OTP_RESEND_WAIT_MINUTES * 60
    resend_remaining = max(0, (last_sent_ts + wait_window) - now_ts) if last_sent_ts else 0
    expires_in = max(0, expires_ts - now_ts) if expires_ts else 0

    if request.method == 'POST':
        code = request.POST.get('otp', '').strip()
        if not code:
            messages.error(request, 'Please enter the OTP code.')
            return redirect('verify_otp')

        expected = request.session.get('pending_otp')
        expires = request.session.get('pending_otp_expires', 0)

        if now_ts > int(expires or 0):
            messages.error(request, 'OTP has expired. Use the resend option below to get a fresh code.')
            return redirect('verify_otp')

        if code != expected:
            messages.error(request, 'Invalid OTP code.')
            return redirect('verify_otp')

        # Mark user active and clear pending session
        user.is_active = True
        user.save(update_fields=['is_active'])
        for key in ['pending_user_id', 'pending_otp', 'pending_otp_expires', 'pending_otp_last_sent']:
            request.session.pop(key, None)

        messages.success(request, 'Your account has been verified! You can now sign in.')
        return redirect('login')

    return render(
        request,
        'otp_verify.html',
        {
            'email': user.email,
            'resend_seconds_remaining': resend_remaining,
            'expires_seconds_remaining': expires_in,
        },
    )


def resend_otp_view(request):
    if request.method != 'POST':
        return redirect('verify_otp')

    pending_user_id = request.session.get('pending_user_id')
    if not pending_user_id:
        messages.error(request, 'No pending verification found. Please register first.')
        return redirect('register')

    try:
        user = User.objects.get(pk=pending_user_id)
    except User.DoesNotExist:
        messages.error(request, 'User not found. Please register again.')
        return redirect('register')

    if user.is_active:
        messages.info(request, 'Your account is already verified. You can log in.')
        return redirect('login')

    now_ts = int(timezone.now().timestamp())
    last_sent = int(request.session.get('pending_otp_last_sent') or 0)
    wait_window = OTP_RESEND_WAIT_MINUTES * 60
    if last_sent and (now_ts - last_sent) < wait_window:
        remaining = wait_window - (now_ts - last_sent)
        minutes = (remaining // 60) + (1 if remaining % 60 else 0)
        messages.error(request, f'Please wait about {minutes} minute(s) before requesting a new OTP.')
        return redirect('verify_otp')

    code, expires_at = _issue_otp_and_send_email(request, user)
    request.session['pending_otp'] = code
    request.session['pending_otp_expires'] = expires_at
    request.session['pending_otp_last_sent'] = now_ts
    messages.success(request, 'A new OTP has been sent to your email.')
    return redirect('verify_otp')


def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if not email:
            messages.error(request, 'Please enter the email address associated with your account.')
            return redirect('forgot_password')

        user = User.objects.filter(email__iexact=email).first()
        if not user:
            messages.error(request, 'No account found with that email address.')
            return redirect('forgot_password')

        now_ts = int(timezone.now().timestamp())
        last_sent = int(request.session.get('password_reset_last_sent') or 0)
        wait_window = OTP_RESEND_WAIT_MINUTES * 60
        if last_sent and (now_ts - last_sent) < wait_window:
            remaining = wait_window - (now_ts - last_sent)
            minutes = (remaining // 60) + (1 if remaining % 60 else 0)
            request.session['password_reset_user_id'] = user.pk
            messages.info(request, f'An OTP was recently sent. Please wait about {minutes} minute(s) before requesting a new one.')
            return redirect('password_reset_verify')

        code, expires_at = _issue_password_reset_otp(request, user)
        request.session['password_reset_user_id'] = user.pk
        request.session['password_reset_otp'] = code
        request.session['password_reset_expires'] = expires_at
        request.session['password_reset_last_sent'] = now_ts
        messages.success(request, 'We sent an OTP to your email. Enter it below to reset your password.')
        return redirect('password_reset_verify')

    return render(request, 'forgot_password.html')


def password_reset_verify_view(request):
    reset_user_id = request.session.get('password_reset_user_id')
    if not reset_user_id:
        messages.error(request, 'No password reset request in progress.')
        return redirect('forgot_password')

    try:
        user = User.objects.get(pk=reset_user_id)
    except User.DoesNotExist:
        request.session.pop('password_reset_user_id', None)
        messages.error(request, 'We could not find that account. Please try again.')
        return redirect('forgot_password')

    if request.method == 'POST':
        code = request.POST.get('otp', '').strip()
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if not code:
            messages.error(request, 'Please enter the OTP code sent to your email.')
            return redirect('password_reset_verify')

        if not password1 or not password2:
            messages.error(request, 'Please enter and confirm your new password.')
            return redirect('password_reset_verify')

        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return redirect('password_reset_verify')

        expected = request.session.get('password_reset_otp')
        expires = request.session.get('password_reset_expires', 0)
        now_ts = int(timezone.now().timestamp())
        if now_ts > int(expires or 0):
            request.session.pop('password_reset_user_id', None)
            messages.error(request, 'Your OTP has expired. Please request a new password reset OTP.')
            return redirect('forgot_password')

        if code != expected:
            messages.error(request, 'Invalid OTP code.')
            return redirect('password_reset_verify')

        user.set_password(password1)
        user.save(update_fields=['password'])
        for key in ['password_reset_user_id', 'password_reset_otp', 'password_reset_expires', 'password_reset_last_sent']:
            request.session.pop(key, None)
        messages.success(request, 'Your password has been reset. You can now log in.')
        return redirect('login')

    return render(
        request,
        'password_reset_verify.html',
        {
            'email': user.email,
        },
    )



def login_view(request):
    if request.user.is_authenticated:
        return redirect('user_dashboard')

    next_url = request.GET.get('next', '')
    form_errors = []
    form_data = {'username': request.POST.get('username', '').strip() if request.method == 'POST' else request.GET.get('username', '').strip()}

    if request.method == 'POST':
        username = form_data['username']
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            # Enforce email verification: block login when inactive
            if not user.is_active:
                code, expires_at = _issue_otp_and_send_email(request, user)
                request.session['pending_user_id'] = user.pk
                request.session['pending_otp'] = code
                request.session['pending_otp_expires'] = expires_at
                request.session['pending_otp_last_sent'] = int(timezone.now().timestamp())
                messages.info(request, 'Please verify your email. We just sent an OTP to your inbox.')
                return redirect('verify_otp')

            login(request, user)
            messages.success(request, 'Signed in successfully.')
            return redirect(next_url or 'user_dashboard')

        # If credentials are correct but user is inactive, start OTP flow
        user_lookup = User.objects.filter(username=username).first()
        if user_lookup and user_lookup.check_password(password or '') and not user_lookup.is_active:
            code, expires_at = _issue_otp_and_send_email(request, user_lookup)
            request.session['pending_user_id'] = user_lookup.pk
            request.session['pending_otp'] = code
            request.session['pending_otp_expires'] = expires_at
            request.session['pending_otp_last_sent'] = int(timezone.now().timestamp())
            messages.info(request, 'Please verify your email. We just sent an OTP to your inbox.')
            return redirect('verify_otp')

        # Otherwise wrong credentials or unknown user
        form_errors = ['We could not sign you in with those credentials.']

    context = {
        'next': next_url,
        'form_data': form_data,
        'form_errors': form_errors,
    }

    return render(request, 'login.html', context)


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')