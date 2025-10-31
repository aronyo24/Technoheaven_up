from django import forms
from .models import Blog

from django import forms
from .models import Blog

class BlogUploadForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea(attrs={'rows': 8, 'placeholder': 'Write your blog content here...'}), required=False)
    docx_file = forms.FileField(required=False)

    class Meta:
        model = Blog
        fields = ['title', 'author', 'date', 'content', 'docx_file']
