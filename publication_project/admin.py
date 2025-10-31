from django.contrib import admin
from .models import Publication, Project, Resource, Client, Service
from django.utils.html import format_html



class PublicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'journal', 'pages', 'cited_by', 'year')
    search_fields = ('title', 'author', 'journal', 'pages')
    list_filter = ('year',)


admin.site.register(Publication, PublicationAdmin)


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('project_title', 'durations', 'funded_by', 'funding_amount', 'role', 'logo')


admin.site.register(Project, ProjectAdmin)


class ResourceAdmin(admin.ModelAdmin):
    list_display = ('resource_name', 'resource_description', 'pdf_file', 'resource_img')


admin.site.register(Resource, ResourceAdmin)

class ClientAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'client_description', 'website')
    search_fields = ('client_name',)
    list_filter = ('website',)


admin.site.register(Client, ClientAdmin)


class ServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'service_name', 'category', 'icon_preview')
    search_fields = ('service_name', 'description', 'category')
    list_filter = ('category',)

    def icon_preview(self, obj):
        if obj.icon:
            return format_html('<i class="{}" style="font-size:1.25rem; margin-right:6px;"></i> <span>{}</span>', obj.icon, obj.icon)
        return ''
    icon_preview.short_description = 'Icon'


admin.site.register(Service, ServiceAdmin)