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

    def get_comments_for_claim(self):
        from comments.models import Comment
        return Comment.objects.filter(claim_id=self.id)

    def get_tweets_for_claim(self):
        from tweets.models import Tweet
        return Tweet.objects.filter(claim_id=self.id).order_by('-id')

    def users_commented_ids(self):
        from comments.models import Comment
        max_comments = 5
        users_with_num_of_comments = {}
        for comment in Comment.objects.filter(claim_id=self.id):
            if comment.user_id not in users_with_num_of_comments:
                users_with_num_of_comments[comment.user_id] = 1
            else:
                users_with_num_of_comments[comment.user_id] += 1
        user_ids = [user_id for user_id in users_with_num_of_comments if users_with_num_of_comments[user_id] >=
                    max_comments]
        return user_ids

    def num_of_true_comments(self):
        result = 0
        for comment in self.get_comments_for_claim():
            if comment.system_label == 'True':
                result += 1
        return result

    def num_of_false_comments(self):
        result = 0
        for comment in self.get_comments_for_claim():
            if comment.system_label == 'False':
                result += 1
        return result

    # def get_report_link(self):
    #     tap_url = ''
    #     report = Claims_Reports.objects.filter(claim_id=self.id)
    #     if len(report) > 0:
    #         return tap_url + '/' + str(report.first().id)
    #     else:
    #         return None


class Claims_Reports(models.Model):
    claim = models.ForeignKey(Claim, on_delete=models.CASCADE)
    report_id = models.IntegerField()

    def __str__(self):
        return str(self.claim.id) + ' - ' + str(self.report_id)


class Merging_Suggestions(models.Model):
    claim = models.ForeignKey(Claim, related_name='claim_suggestion', on_delete=models.CASCADE)
    claim_to_merge = models.ForeignKey(Claim, related_name='claim_to_merge_suggestion', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.claim.id) + ' - ' + str(self.claim_to_merge.id)
