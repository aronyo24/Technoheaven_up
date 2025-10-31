from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

class Message(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()

    def __str__(self):
        return str(self.name)


# Create your models here.
class News(models.Model):
    date = models.CharField(max_length=200)
    news_title = models.TextField(max_length=200)
    link = models.URLField()

    def __str__(self):
        return self.news_title
    
# Blog model for blog posts

CATEGORY_CHOICES = [
    ('web_development', 'Web Development'),
    ('ai_ml', 'AI & Machine Learning'),
    ('cybersecurity', 'Cybersecurity'),
    ('data_science', 'Data Science'),
    ('blockchain', 'Blockchain'),
    ('cloud_computing', 'Cloud Computing'),
    ('others', 'Others'),
]

STATUS_CHOICES = [
    ('pending', 'Pending Review'),
    ('published', 'Published'),
    ('rejected', 'Rejected'),
]


class Blog(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    author = models.CharField(max_length=100, blank=True)
    date = models.DateField(default=timezone.now)
    content = models.TextField(blank=True)
    image = models.ImageField(
        upload_to='blog_images/', blank=True, null=True, default='blog_images/default.jpg'
    )
    likes = models.PositiveIntegerField(default=0)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='published')
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='submitted_blogs'
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """Auto-generate a unique slug from title. If slug already exists, append a counter."""
        if not self.slug:
            base_slug = slugify(self.title) or "post"
            slug = base_slug
            counter = 1
            # exclude self when updating
            while Blog.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        if not self.author and self.submitted_by:
            full_name = self.submitted_by.get_full_name()
            self.author = full_name if full_name else self.submitted_by.username

        if not self.date:
            self.date = timezone.now().date()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


# Comment model for blog comments
class Comment(models.Model):
    blog = models.ForeignKey('Blog', related_name='comments', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    comment = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.name} on {self.blog.title}"