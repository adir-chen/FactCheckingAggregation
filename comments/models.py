from django.db import models
from django.utils import timezone
from claims.models import Claim
from django.contrib.auth.models import User


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    claim = models.ForeignKey(Claim, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    url = models.CharField(max_length=200)
    tags = models.CharField(max_length=250)
    verdict_date = models.DateField()
    label = models.CharField(max_length=50)
    system_label = models.CharField(max_length=10)
    up_votes = models.ManyToManyField(User, related_name='up_votes', blank=True)
    down_votes = models.ManyToManyField(User, related_name='down_votes', blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user.username + ' - ' + self.title
