from django.db import models
from django.contrib.auth.models import User


class Users_Images(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    user_img = models.CharField(max_length=250)


class Users_Reputations(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    user_rep = models.IntegerField()


class Scrapers(models.Model):
    scraper_name = models.CharField(max_length=50)
    scraper_id = models.ForeignKey(User, on_delete=models.CASCADE)
