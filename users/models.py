from django.db import models


class User(models.Model):
    username = models.CharField(max_length=20)
    email = models.EmailField(max_length=254)
    state = models.CharField(max_length=20)
    reputation = models.IntegerField()
    user_img = models.CharField(max_length=500)

    def __str__(self):
        return self.username + ' - ' + self.email
