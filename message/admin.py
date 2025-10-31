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
    actions = ("publish_selected", "mark_pending", "reject_selected",)

    def content_preview(self, obj):
        """Render live HTML preview + Quill editor for writing content"""
        if not obj:
            return ""

        quill_loader = """
        <link href="https://cdn.quilljs.com/1.3.7/quill.snow.css" rel="stylesheet">
        <script src="https://cdn.quilljs.com/1.3.7/quill.min.js"></script>
        <style>
        #quill-admin-editor {
            width:100%;
            min-height:420px;
            border:1px solid #ddd;
            border-radius:6px;
            background:gray;
            padding:14px;
            margin-top:8px;
        }
        /* Wrapper for better stacking and full-width behavior */
        .quill-admin-wrapper{width:100%;}

        /* toolbar styling to look like blog editors (white, separated) */
        .ql-toolbar{background:#0cf50c;border:1px solid #ddd;border-bottom:none;border-radius:6px 6px 0 0;box-sizing:border-box;padding:6px}
        #quill-toolbar-bottom{background:#0cf50c;border:1px solid #ddd;border-top:none;border-radius:0 0 6px 6px;margin-top:6px}

        /* container/editor styling to match toolbars */
        .ql-container{border-left:1px solid #ddd;border-right:1px solid #ddd;border-bottom:1px solid #ddd;border-radius:0 0 6px 6px;background:#fff}
        .ql-editor{min-height:360px;padding:14px}

        /* ensure toolbar icons contrast on dark admin themes */
        .ql-toolbar button, .ql-toolbar .ql-picker{
            color:#222!important; background:transparent!important;border:none!important;
        }
        </style>
        <script>
        (function(){
            function initQuillAdmin(){
                var textarea = document.querySelector('textarea[name="content"]');
                if(!textarea) return;
                if(document.getElementById('quill-admin-editor')) return;

                textarea.style.display = 'none';

                // create a wrapper so toolbars and editor stack cleanly
                var wrapper = document.createElement('div');
                wrapper.className = 'quill-admin-wrapper';
                var editorDiv = document.createElement('div');
                editorDiv.id = 'quill-admin-editor';
                wrapper.appendChild(editorDiv);
                textarea.parentNode.insertBefore(wrapper, textarea.nextSibling);

                var quill = new Quill('#quill-admin-editor', {
                    theme: 'snow',
                    modules: {
                        toolbar: [
                            [{ 'header': [1, 2, 3, false] }],
                            ['bold','italic','underline','strike'],
                            ['blockquote','code-block'],
                            [{ 'list': 'ordered'}, { 'list': 'bullet' }],
                            ['link','image'],
                            [{ 'align': [] }],
                            [{ 'color': [] }, { 'background': [] }]
                        ]
                    }
                });

                // create a second (bottom) toolbar by moving the top toolbar into our wrapper
                // then cloning it; wire events so the bottom toolbar forwards actions to the original
                (function(){
                    try{
                        var editor = document.getElementById('quill-admin-editor');
                        var parent = editor && editor.parentNode;
                        var toolbarTop = parent && parent.querySelector('.ql-toolbar');
                        if(toolbarTop){
                            // move toolbarTop into our wrapper (so it sits above editor)
                            wrapper.insertBefore(toolbarTop, editor);

                            // clone and insert a bottom toolbar after the wrapper
                            var toolbarBottom = toolbarTop.cloneNode(true);
                            toolbarBottom.id = 'quill-toolbar-bottom';
                            wrapper.appendChild(toolbarBottom);

                            // when clicking bottom buttons, forward to the corresponding top button
                            toolbarBottom.addEventListener('click', function(e){
                                var btn = e.target.closest('button');
                                if(!btn) return;
                                var classes = Array.from(btn.classList).filter(function(c){ return c.indexOf('ql-')===0; });
                                if(classes.length){
                                    var selector = classes.map(function(c){ return 'button.'+c; }).join(',');
                                    var orig = toolbarTop.querySelector(selector);
                                    if(orig) orig.click();
                                }
                            });

                            // forward select/picker changes
                            var bottomSelects = toolbarBottom.querySelectorAll('select');
                            bottomSelects.forEach(function(sel){
                                sel.addEventListener('change', function(){
                                    try{
                                        var cls = Array.from(sel.classList).filter(function(c){ return c.indexOf('ql-')===0; })[0];
                                        var origSel = cls && toolbarTop.querySelector('select.'+cls);
                                        if(origSel){ origSel.value = sel.value; origSel.dispatchEvent(new Event('change')) }
                                    }catch(err){}
                                });
                            });
                        }
                    }catch(err){ /* fail silently in admin if anything goes wrong */ }
                })();

                quill.root.innerHTML = textarea.value || '';

                var form = textarea.form;
                if(form){
                    form.addEventListener('submit', function(){
                        textarea.value = quill.root.innerHTML;
                    });
                }
            }
            if(document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', initQuillAdmin);
            } else {
                initQuillAdmin();
            }
        })();
        </script>
        """
        return mark_safe(quill_loader)
    content_preview.short_description = "Content Preview"

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
