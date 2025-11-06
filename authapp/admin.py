"""
This app does not register models in the admin site.
The canonical UserProfile is already registered in reapp.admin.
"""

from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
	list_display = ("user", "country", "gender", "created_at")
	search_fields = ("user__username", "full_name", "country")
	list_filter = ("gender", "country")