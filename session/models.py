from django.db import models
from django.utils.text import slugify

class Session(models.Model):
    title = models.CharField(max_length=400)
    location = models.CharField(max_length=255)
    date_range = models.CharField(max_length=100)
    tagline = models.CharField(max_length=255)
    session_name = models.CharField(max_length=400)

    html_file = models.FileField(upload_to='html/', blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True, max_length=100)  # limit to prevent DB errors

    def save(self, *args, **kwargs):
        if not self.slug and self.session_name:
            base_slug = slugify(self.session_name)[:90]  # reserve space for suffix
            unique_slug = base_slug
            count = 1
            while Session.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug[:85]}-{count}"
                count += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.session_name

    def get_html_url(self):
        return self.html_file.url if self.html_file else "#"
