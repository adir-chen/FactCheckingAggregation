from django.db import models
import datetime


class User(models.Model):
    username = models.CharField(max_length=20)
    email = models.EmailField(max_length=254)
    state = models.CharField(max_length=20)
    reputation = models.IntegerField()

    def __str__(self):
        return self.username + ' - ' + self.email


class Claim(models.Model):
    title = models.CharField(max_length=150)
    category = models.CharField(max_length=50)
    authentic_grade = models.IntegerField()

    def __str__(self):
        return self.title + ' - ' + self.category


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    claim = models.ForeignKey(Claim, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    url = models.CharField(max_length=200)
    verdict_date = models.DateField(default=datetime.date.today)
    tags = models.CharField(max_length=250)
    label = models.CharField(max_length=50)
    pos_votes = models.IntegerField()
    neg_votes = models.IntegerField()

    def __str__(self):
        return self.user.username + ' - ' + self.title
