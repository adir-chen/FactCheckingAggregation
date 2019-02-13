from django.db import models
from django.urls import reverse

from claims.models import Claim
from django.contrib.auth.models import User
from vote.models import VoteModel


class Comment(VoteModel, models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    claim = models.ForeignKey(Claim, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    url = models.CharField(max_length=200)
    verdict_date = models.CharField(max_length=10)
    label = models.CharField(max_length=50)
    # neg_votes = models.IntegerField(default=0)
    # pos_votes = models.IntegerField(default=0)
    # neg_votes = VoteModel(models.IntegerField(default=0))
    # pos_votes = VoteModel(models.IntegerField(default=0))
    up_votes = models.ManyToManyField(User, related_name='up_votes', blank=True)
    down_votes = models.ManyToManyField(User, related_name='down_votes', blank=True)

    def __str__(self):
        return self.user.username + ' - ' + self.title
