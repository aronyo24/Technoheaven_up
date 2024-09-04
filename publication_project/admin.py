from django.contrib import admin
from .models import Publication, Project, Resource


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
