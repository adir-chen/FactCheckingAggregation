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
        user_ids = [user_id for user_id in users_with_num_of_replies if users_with_num_of_replies[user_id] >= max_replies]
        return user_ids

    def get_replies(self):
        from replies.models import Reply
        return Reply.objects.filter(comment_id=self.id)

    def get_first_two_replies(self):
        return self.get_replies()[:2]

    def get_more_replies(self):
        return self.get_replies()[2:]

    def has_more_replies(self):
        return len(self.get_replies()) > 2

    def get_preview(self):
        import requests
        import json
        from bs4 import BeautifulSoup
        try:
            response = requests.get(self.url)
            encoding = response.encoding if 'charset' in response.headers.get('content-type', '').lower() else None
            metas = BeautifulSoup(response.content, from_encoding=encoding, features="html.parser")
            # metas = BeautifulSoup(response.text, features="html.parser")
            title = metas.find("meta", property="og:title")
            if title:
                title = title['content']
            description = metas.find("meta", property="og:description")
            if description:
                description = description['content']
            src = metas.find("meta", property="og:image")
            if src:
                src = src['content']
            result = {'title': title, 'description': description, 'src': src}
            return json.dumps(result)
        except:
            return False

    def vote_on_comment(self):
        max_minutes_to_vote_comment = 10
        return (timezone.now() - self.timestamp).total_seconds() / 60 > max_minutes_to_vote_comment



