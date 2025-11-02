from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from message.models import Blog
from .models import UserProfile


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data.get("first_name", "")
        user.last_name = self.cleaned_data.get("last_name", "")
        if commit:
            user.save()
        return user


class BlogSubmissionForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ["title", "category", "image", "content"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Give your post an engaging title"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 10, "placeholder": "Share your thoughts..."}),
        }

    def clean_content(self):
        content = self.cleaned_data.get("content", "").strip()
        if not content:
            raise forms.ValidationError("Please provide some content for your blog post.")
        return content


class AccountIdentityForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "First name"}),
            "last_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Last name"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "you@example.com"}),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip()
        if not email:
            raise forms.ValidationError("Email address is required.")

        qs = User.objects.filter(email__iexact=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("This email address is already linked to another account.")
        return email


class AccountProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["full_name", "country", "age", "gender", "contact_number"]
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Full name"}),
            "country": forms.TextInput(attrs={"class": "form-control", "placeholder": "Country"}),
            "age": forms.NumberInput(attrs={"class": "form-control", "min": 0, "placeholder": "Age"}),
            "gender": forms.Select(attrs={"class": "form-select"}),
            "contact_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "Contact number"}),
        }

    def clean_full_name(self):
        full_name = self.cleaned_data.get("full_name", "").strip()
        if not full_name:
            raise forms.ValidationError("Please supply your full name.")
        return full_name

    def clean_country(self):
        return self.cleaned_data.get("country", "").strip()

    def clean_contact_number(self):
        return self.cleaned_data.get("contact_number", "").strip()

    def clean_age(self):
        age = self.cleaned_data.get("age")
        if age is not None and age < 0:
            raise forms.ValidationError("Age cannot be negative.")
        return age
