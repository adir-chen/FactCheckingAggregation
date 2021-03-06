from django.utils import timezone
from django.db import models
from comments.models import Comment
from django.contrib.auth.models import User


class Reply(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    content = models.CharField(max_length=300)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user.username + ' replied to comment ' + str(self.comment.id) \
               + ' in claim ' + str(self.comment.claim_id)
