from django.db import models

# Create your models here.


class Claim(models.Model):
    title = models.CharField(max_length=150)
    category = models.CharField(max_length=50)
    authentic_grade = models.IntegerField()
    image_src = models.CharField(max_length=1000)

    def __str__(self):
        return self.title + ' - ' + self.category

