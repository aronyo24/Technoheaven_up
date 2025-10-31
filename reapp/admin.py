from django.contrib import admin

from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
	list_display = ("user", "country", "gender", "created_at")
	search_fields = ("user__username", "full_name", "country")
	list_filter = ("gender", "country")
