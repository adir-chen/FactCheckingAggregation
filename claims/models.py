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
        return self.user.username + ' - ' + self.claim

    def users_commented_ids(self):
        from comments.models import Comment
        max_comments = 5
        users_with_num_of_comments = {}
        for comment in Comment.objects.filter(claim_id=self.id):
            if comment.user_id not in users_with_num_of_comments:
                users_with_num_of_comments[comment.user_id] = 1
            else:
                users_with_num_of_comments[comment.user_id] += 1
        user_ids = [user_id for user_id in users_with_num_of_comments if users_with_num_of_comments[user_id] > max_comments]
        return user_ids

    def users_tweeted_ids(self):
        from tweets.models import Tweet
        user_ids = []
        for tweet in Tweet.objects.filter(claim_id=self.id):
            user_ids.append(tweet.user_id)
        return user_ids

    def get_report_link(self):
        tap_url = ''
        report = Claims_Reports.objects.filter(claim_id=self.id)
        if len(report) > 0:
            return tap_url + '/' + str(report.first().id)
        else:
            return None

    def max_comment_id(self):
        from comments.models import Comment
        max_comment_id = -1
        for comment in Comment.objects.filter(claim_id=self.id):
            if comment.id > max_comment_id:
                max_comment_id = comment.id
        return max_comment_id

    def get_claim_user_img(self):
        from users.models import Users_Images
        user_img = Users_Images.objects.filter(user_id=self.user_id)
        if len(user_img) == 0:
            new_user_img = Users_Images.objects.create(user_id=User.objects.filter(id=self.user_id).first())
            new_user_img.save()
            user_img = new_user_img.user_img
        else:
            user_img = user_img.first().user_img
        return user_img


class Claims_Reports(models.Model):
    claim = models.ForeignKey(Claim, on_delete=models.CASCADE)
    report_id = models.IntegerField()

    def __str__(self):
        return str(self.claim.id) + ' - ' + str(self.report_id)
