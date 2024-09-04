from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify


def validate_image_size(image):
    width, height = image.width, image.height
    if width != 300 or height != 210:  # Corrected image size
        raise ValidationError(f'The image must be exactly 300x211 pixels. Current size is {width}x{height} pixels.')


# Create your models here.
class Gallery(models.Model):
    gallery_img = models.ImageField(upload_to='gallery/', validators=[validate_image_size])
    gallery_title = models.CharField(max_length=50)
    gallery_description = models.TextField()

    def __str__(self):
        return self.gallery_title


def team_validate_image_size(image):
    width, height = image.width, image.height
    if width != 265 or height != 265:  # Corrected image size
        raise ValidationError(f'The image must be exactly 265x265 pixels. Current size is {width}x{height} pixels.')


class Team(models.Model):
    member_img = models.ImageField(upload_to='team/')
    member_name = models.CharField(max_length=200)
    member_title = models.CharField(max_length=200)
    department = models.CharField(max_length=200, blank=True)
    institution = models.CharField(max_length=200, blank=True)
    contact_number = models.CharField(max_length=200)
    member_email = models.EmailField()
    member_location = models.CharField(max_length=200)
    short_bio = models.TextField(blank=True)
    academic_background = models.TextField(blank=True)
    professional_experience = models.TextField(blank=True)
    professional_membership = models.TextField(blank=True)
    professional_collaborations = models.TextField(blank=True)

    researchgate_url = models.URLField(blank=True)
    googlescholar_url = models.URLField(blank=True)

    linkedin_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    website_url = models.URLField(blank=True)

    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug or not self.member_name:
            self.slug = slugify(self.member_name) if self.member_name else None

            # Ensure the slug is unique
            base_slug = self.slug
            counter = 1
            while Team.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1

        super().save(*args, **kwargs)

    def __str__(self):
        return self.member_name
