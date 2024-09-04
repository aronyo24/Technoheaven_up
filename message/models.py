from django.db import models


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
