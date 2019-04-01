from django.contrib.auth.models import User
from claims.models import Claim
from django.db import models
from django.utils import timezone


class Author(models.Model):
    author_name = models.CharField(max_length=100)
    author_rank = models.IntegerField()

    def __str__(self):
        return self.author + ' - ' + str(self.author_rank)


class Tweet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    claim = models.ForeignKey(Claim, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    tweet_link = models.CharField(max_length=200)
    label = models.CharField(default='', max_length=10)
    up_votes = models.ManyToManyField(User, related_name='%(class)s_up_votes', blank=True)
    down_votes = models.ManyToManyField(User, related_name='%(class)s_down_votes', blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user.username + ' - ' + self.tweet_link


