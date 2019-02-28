from django.db import models
from django.contrib.auth.models import User
from django.contrib.staticfiles.templatetags.staticfiles import static


class Users_Images(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    user_img = models.CharField(max_length=250, default=static('claims/assets/images/profile_default_image.jpg'))

    def __str__(self):
        return self.user_id.username


class Users_Reputations(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    user_rep = models.IntegerField()

    def __str__(self):
        return self.user_id.username + ' - ' + str(self.user_rep)


class Scrapers(models.Model):
    scraper_name = models.CharField(max_length=50)
    scraper_id = models.ForeignKey(User, on_delete=models.CASCADE)
    true_labels = models.TextField(default='true')
    false_labels = models.TextField(default='false')

    def __str__(self):
        return self.scraper_name
