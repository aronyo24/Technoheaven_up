from django.db import models
from django.utils.text import slugify


class Publication(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")
    title = models.CharField(max_length=300)
    author = models.TextField()
    pages = models.CharField(max_length=255, blank=True, null=True)
    journal = models.TextField()
    cited_by = models.CharField(max_length=50)
    year = models.IntegerField()
    link = models.URLField()

    def __str__(self):
        return self.title


class Project(models.Model):
    project_title = models.CharField(max_length=400)
    durations = models.CharField(max_length=200,blank=True, null=True)
    funded_by = models.CharField(max_length=100 ,blank=True, null=True)
    funding_amount = models.CharField(max_length=200,blank=True, null=True)
    role = models.CharField(max_length=200,blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='logos/',blank=True, null=True)
    url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.project_title


class Resource(models.Model):
    resource_name = models.CharField(max_length=400)
    resource_description = models.TextField()
    resource_img = models.ImageField(upload_to='resource_img/')
    pdf_file = models.FileField(upload_to='pdf/')

    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug or not self.resource_name:

            self.slug = slugify(self.resource_name) if self.resource_name else None


            unique_slug = self.slug
            count = 1
            while Resource.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{self.slug}-{count}"
                count += 1

            self.slug = unique_slug

        super().save(*args, **kwargs)
    def __str__(self):
        return self.resource_name

class Client(models.Model):
    client_name = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='client_logos/')
    client_description = models.TextField()
    website = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.client_name


class Service(models.Model):
    SERVICE_CATEGORIES = [
        ('Data Science', 'Data Science'),
        ('Software Development', 'Software Development'),
        ('Cybersecurity', 'Cybersecurity'),
        ('Blockchain', 'Blockchain'),
        ('Consulting', 'Consulting'),
        ('Other Services', 'Other Services'),

    ]
    category = models.CharField(max_length=50, choices=SERVICE_CATEGORIES)
    service_name = models.CharField(max_length=200)
    description = models.TextField()
    icon = models.CharField(blank=True, max_length=100, help_text="Enter the CSS class for the icon, e.g., 'bi bi-laptop'")
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        # generate slug from service_name if not present
        if not self.slug and self.service_name:
            base = slugify(self.service_name)
            unique_slug = base
            count = 1
            while Service.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base}-{count}"
                count += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.service_name
