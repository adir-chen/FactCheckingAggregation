from django.contrib.auth.models import User
from django.db import models


class Logger(models.Model):
    date = models.DateField()
    activity = models.TextField()
