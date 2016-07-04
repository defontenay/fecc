from django.db import models

# Create your models here.

class User(models.Model):
    slack = models.CharField(max_length=20)
    email = models.CharField(max_length=200)
    password = models.CharField(max_length=50)
    error = models.CharField(max_length=100)

class Global(models.Model):
    name = models.CharField(max_length=20)
    value = models.CharField(max_length=20)
