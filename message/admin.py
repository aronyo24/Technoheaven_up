from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Message, News, Blog, Comment

# ✅ Custom site branding
admin.site.site_header = "Technoheven Admin"
admin.site.site_title = "Technoheven"
admin.site.index_title = "Site Administration"

# -------------------------
# Messages
# -------------------------
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "short_message")
    search_fields = ("name", "email", "subject")
    # Message model has no `date` field; removed from list_filter

    def short_message(self, obj):
        """Preview of message content in admin list view"""
        return (obj.message[:50] + "...") if len(obj.message) > 50 else obj.message
    short_message.short_description = "Message"


# -------------------------
# News
# -------------------------
@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ("date", "news_title", "link")
    search_fields = ("news_title",)
    list_filter = ("date",)


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'date', 'status', 'likes', 'category', 'submitted_by')
    search_fields = ('author', 'title', 'submitted_by__username')
    list_filter = ('category', 'date', 'status')
    exclude = ("slug",)
    readonly_fields = ("content_preview", "submitted_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("title", "author", "category", "image", "status")} ),
        ("Submission", {"fields": ("submitted_by", "submitted_at", "updated_at", "date")} ),
        ("Content", {"fields": ("content", "content_preview")} ),
        (None, {"fields": ("likes",)} ),
    )
    def content_preview(self, obj):
        """Preview of content in admin list view"""
        content = obj.content or ""
        if len(content) > 50:
            return mark_safe(f"{content[:50]}...")
        return mark_safe(content)
    content_preview.short_description = "Content Preview"
    actions = ("publish_selected", "mark_pending", "reject_selected",)

    @admin.action(description="Mark selected blogs as draft")
    def mark_draft(self, request, queryset):
        queryset.update(status='draft')

    @admin.action(description="Mark selected blogs as published")
    def publish_selected(self, request, queryset):
        queryset.update(status='published')

    @admin.action(description="Mark selected blogs as pending")
    def mark_pending(self, request, queryset):
        queryset.update(status='pending')

    @admin.action(description="Mark selected blogs as rejected")
    def reject_selected(self, request, queryset):
        queryset.update(status='rejected')


# -------------------------
# Comments
# -------------------------
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("blog", "name", "short_comment", "date")
    search_fields = ("name", "comment")
    list_filter = ("date", "blog")

    def short_comment(self, obj):
        """Show preview of comment in list display"""
        return (obj.comment[:60] + "...") if len(obj.comment) > 60 else obj.comment
    short_comment.short_description = "Comment"
