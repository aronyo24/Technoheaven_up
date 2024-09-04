from django.contrib import admin
from .models import Message, News


class MessageAdmin(admin.ModelAdmin):
    list_display = ("name", 'email', 'subject', 'message')


admin.site.register(Message, MessageAdmin)


class NewsAdmin(admin.ModelAdmin):
    list_display = ("date", 'news_title', 'link')

admin.site.register(News,NewsAdmin)