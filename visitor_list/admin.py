from django.contrib import admin

from .models import Visitor

@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    
    list_display = ('id', 'ip_address', 'private_ip', 'user_agent', 'city', 'country', 'visit_date')
    search_fields = ('ip_address', 'city', 'country')

    list_filter = ('country', 'visit_date')

    ordering = ('-visit_date',)
    

    list_per_page = 25
