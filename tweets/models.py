from django.contrib.auth.models import User
from django.utils import timezone
from claims.models import Claim
from django.db import models


class Tweet(models.Model):
    claim = models.ForeignKey(Claim, on_delete=models.CASCADE)
    tweet_link = models.CharField(max_length=200)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.claim.id) + ' - ' + self.tweet_link


