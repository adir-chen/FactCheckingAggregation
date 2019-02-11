from django.db import models
from claims.models import Claim
from django.contrib.auth.models import User
from vote.models import VoteModel


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    claim = models.ForeignKey(Claim, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    url = models.CharField(max_length=200)
    verdict_date = models.CharField(max_length=10)
    label = models.CharField(max_length=50)
    pos_votes = models.IntegerField()
    neg_votes = models.IntegerField()

    def __str__(self):
        return self.user.username + ' - ' + self.title
