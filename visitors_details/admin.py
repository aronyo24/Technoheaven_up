
# Register your models here.
from django.contrib import admin
from .models import Visitor


@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = (
        'ip_address',
        'private_ip',
        'user_agent',
        'city',
        'country',
        'last_visit',
        'visit_count',
    )
    list_filter = ('country', 'city', 'last_visit')  
    search_fields = ('ip_address', 'user_agent', 'city', 'country')  # Search bar
    ordering = ('-last_visit',)  
    readonly_fields = ('last_visit', 'visit_count') 
    fieldsets = (
        (None, {
            'fields': ('ip_address', 'private_ip', 'user_agent')
        }),
        ('Location Information', {
            'fields': ('city', 'country'),
        }),
        ('Visit Details', {
            'fields': ('visit_count', 'last_visit'),
        }),
    )

