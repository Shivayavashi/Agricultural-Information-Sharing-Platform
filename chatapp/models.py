from django.db import models

# Create your models here.
class Profile(models.Model):
    username = models.CharField(max_length=255, default=None)
    password = models.CharField(max_length=255)
    name = models.CharField(max_length=255, default=None)
    number = models.CharField(max_length=255, default=None)
    dob = models.CharField(max_length=255, default=None)
    gender = models.CharField(max_length=255, default=None)
    country = models.CharField(max_length=255, default=None)
    state = models.CharField(max_length=255, default=None)
    district = models.CharField(max_length=255, default=None)
    taluk = models.CharField(max_length=255, default=None)

class Chatlogs(models.Model):
    username = models.CharField(max_length=255, default=None)
    question = models.CharField(max_length=255, default=None)
    reply = models.CharField(max_length=255, default=None)