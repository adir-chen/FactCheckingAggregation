from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.contrib.staticfiles.templatetags.staticfiles import static


class Claim(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    claim = models.CharField(max_length=150)
    category = models.CharField(max_length=50)
    tags = models.CharField(max_length=250)
    authenticity_grade = models.IntegerField()
    image_src = models.CharField(max_length=1000, default=static('claims/assets/images/claim_default_image.jpg'))
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.claim + ' - ' + self.category

    def users_commented_ids(self):
        from comments.models import Comment
        user_ids = []
        for comment in Comment.objects.filter(claim_id=self.id):
            user_ids.append(comment.user_id)
        return user_ids

    def users_tweeted_ids(self):
        from tweets.models import Tweet
        user_ids = []
        for tweet in Tweet.objects.filter(claim_id=self.id):
            user_ids.append(tweet.user_id)
        return user_ids
