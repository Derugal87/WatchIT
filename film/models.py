from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Show(models.Model):
    showid = models.IntegerField()
    genres = models.TextField(default='')
    status = models.TextField(default=32)
    image = models.TextField(default='')
    name = models.TextField(default='')


class UserRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    show = models.ForeignKey(Show, on_delete=models.CASCADE)
    rating = models.IntegerField()
    position = models.IntegerField(default=0)
