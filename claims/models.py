from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User


class Claim(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    claim = models.CharField(max_length=150)
    category = models.CharField(max_length=50)
    tags = models.CharField(max_length=250)
    authenticity_grade = models.IntegerField()
    image_src = models.CharField(max_length=1000)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.claim + ' - ' + self.category

    def users_commented_ids(self):
        from comments.models import Comment
        user_ids = []
        for comment in Comment.objects.filter(claim_id=self.id):
            user_ids.append(comment.user_id)
        return user_ids
