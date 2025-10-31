from django.contrib import admin
from team_gallary.models import Gallery,Team


class GalleryAdmin(admin.ModelAdmin):
    list_display = ('gallery_img', 'gallery_title', 'gallery_description')


admin.site.register(Gallery, GalleryAdmin)


class TeamAdmin(admin.ModelAdmin):
    list_display = ('member_name', 'member_title', 'department','institution','member_email','contact_number')


admin.site.register(Team, TeamAdmin)
