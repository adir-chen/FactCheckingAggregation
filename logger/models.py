from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Logger(models.Model):
    date = models.DateTimeField(default=timezone.now)
    user_id = models.IntegerField()
    username = models.TextField()
    action = models.TextField()
    result = models.BooleanField(default=False)  # True for success and False for failure

    def __str__(self):
        return self.username
