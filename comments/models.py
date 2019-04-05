from django.db import models
from django.utils import timezone
from claims.models import Claim
from django.contrib.auth.models import User


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    claim = models.ForeignKey(Claim, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    url = models.CharField(max_length=200)
    tags = models.CharField(max_length=250)
    verdict_date = models.DateField()
    label = models.CharField(max_length=50)
    system_label = models.CharField(max_length=10)
    up_votes = models.ManyToManyField(User, related_name='%(class)s_up_votes', blank=True)
    down_votes = models.ManyToManyField(User, related_name='%(class)s_down_votes', blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user.username + ' - ' + self.title

    def tags_as_list(self):
        return self.tags.split(',')

    def users_replied_ids(self):
        from replies.models import Reply
        max_replies = 5
        users_with_num_of_replies = {}
        for reply in Reply.objects.filter(comment_id=self.id):
            if reply.user_id not in users_with_num_of_replies:
                users_with_num_of_replies[reply.user_id] = 1
            else:
                users_with_num_of_replies[reply.user_id] += 1
        user_ids = [user_id for user_id in users_with_num_of_replies if users_with_num_of_replies[user_id] > max_replies]
        return user_ids

    def get_replies(self):
        from replies.models import Reply
        return Reply.objects.filter(comment_id=self.id)

    def get_replies_with_images(self):
        from users.models import Users_Images
        reply_objects = self.get_replies()
        replies = {}
        for reply in reply_objects:
            user_img = Users_Images.objects.filter(user_id=reply.user_id)
            if len(user_img) == 0:
                new_user_img = Users_Images.objects.create(user_id=User.objects.filter(id=reply.user_id).first())
                new_user_img.save()
                user_img = new_user_img
            else:
                user_img = user_img.first()
            replies[reply] = {'user': User.objects.filter(id=reply.user_id).first(),
                              'user_img': user_img}
        return replies



