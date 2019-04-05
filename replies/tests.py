from django.http import HttpRequest, Http404, QueryDict
from django.test import TestCase
from claims.models import Claim
from comments.models import Comment
from replies.models import Reply
from replies.views import add_reply, build_reply, check_if_reply_is_valid, edit_reply, \
    check_reply_new_fields, delete_reply, check_if_delete_reply_is_valid
from users.models import User
import datetime
import random


class CommentTests(TestCase):
    def setUp(self):
        self.user_1 = User(username="User1", email='user1@gmail.com')
        self.user_2 = User(username="User2", email='user2@gmail.com')
        self.user_1.save()
        self.user_2.save()
        self.num_of_saved_users = 2
        self.claim_1 = Claim(user_id=self.user_1.id,
                             claim='claim1',
                             category='category1',
                             tags='tag1,tag2',
                             authenticity_grade=0)
        self.claim_2 = Claim(user_id=self.user_2.id,
                             claim='claim2',
                             category='category2',
                             tags='tag3,tag4',
                             authenticity_grade=0)
        self.claim_1.save()
        self.claim_2.save()
        self.num_of_saved_claims = 2
        self.url = 'https://www.snopes.com/fact-check/page/'
        self.comment_1 = Comment(claim_id=self.claim_1.id,
                                 user_id=self.user_1.id,
                                 title=self.claim_1.claim,
                                 description='description1',
                                 url=self.url + str(random.randint(1, 10)),
                                 tags='tag1',
                                 verdict_date=datetime.date.today() - datetime.timedelta(days=random.randint(1, 10)),
                                 label='label1')
        self.comment_2 = Comment(claim_id=self.claim_2.id,
                                 user_id=self.user_2.id,
                                 title=self.claim_2.claim,
                                 description='description2',
                                 url=self.url + str(random.randint(1, 10)),
                                 tags='tag2,tag3',
                                 verdict_date=datetime.date.today() - datetime.timedelta(days=random.randint(1, 10)),
                                 label='label2')
        self.comment_1.save()
        self.comment_2.save()
        self.num_of_saved_comments = 2

        self.reply = Reply(comment_id=self.comment_1.id,
                           user_id=self.user_2.id,
                           content='replyContent')
        self.num_of_saved_replies = 0
        self.new_reply_details_user_1 = {'comment_id': self.comment_2.id,
                                         'content': 'content1'}
        self.new_reply_details_user_2 = {'comment_id': self.comment_1.id,
                                         'content': 'content2'}

        self.update_comment_details = {'reply_content': 'newContent'}

        self.post_request = HttpRequest()
        self.post_request.method = 'POST'

        self.get_request = HttpRequest()
        self.get_request.method = 'GET'

    def tearDown(self):
        pass

    def test_add_reply_by_user_1(self):
        len_replies = len(Reply.objects.filter(comment_id=self.comment_2.id))
        self.post_request.POST = self.new_reply_details_user_1
        self.post_request.user = self.user_1
        self.assertTrue(add_reply(self.post_request).status_code == 200)
        self.assertTrue(len(Reply.objects.filter(comment_id=self.comment_2.id)) == len_replies + 1)
        new_reply = Reply.objects.all().order_by('-id').first()
        self.assertTrue(new_reply.id == self.num_of_saved_replies + 1)
        self.assertTrue(new_reply.comment_id == self.new_reply_details_user_1['comment_id'])
        self.assertTrue(new_reply.user_id == self.user_1.id)
        self.assertTrue(new_reply.content == self.new_reply_details_user_1['content'])

    def test_add_reply_by_user_2(self):
        len_replies = len(Reply.objects.filter(comment_id=self.comment_1.id))
        self.post_request.POST = self.new_reply_details_user_2
        self.post_request.user = self.user_2
        self.assertTrue(add_reply(self.post_request).status_code == 200)
        self.assertTrue(len(Reply.objects.filter(comment_id=self.comment_1.id)) == len_replies + 1)
        new_reply = Reply.objects.all().order_by('-id').first()
        self.assertTrue(new_reply.id == self.num_of_saved_replies + 1)
        self.assertTrue(new_reply.comment_id == self.new_reply_details_user_2['comment_id'])
        self.assertTrue(new_reply.user_id == self.user_2.id)
        self.assertTrue(new_reply.content == self.new_reply_details_user_2['content'])

    def test_add_reply_by_user_not_authenticated(self):
        from django.contrib.auth.models import AnonymousUser
        self.post_request.POST = self.new_reply_details_user_1
        self.post_request.user = AnonymousUser()
        self.assertRaises(Http404, add_reply, self.post_request)

    def test_add_reply_by_invalid_user(self):
        guest = User(id=self.num_of_saved_users + random.randint(1, 10), username='guest')
        self.post_request.POST = self.new_reply_details_user_1
        self.post_request.user = guest
        self.assertRaises(Exception, add_reply, self.post_request)

    def test_add_reply_missing_comment_id(self):
        del self.new_reply_details_user_1['comment_id']
        self.post_request.POST = self.new_reply_details_user_1
        self.post_request.user = self.user_1
        self.assertRaises(Exception, add_reply, self.post_request)

        del self.new_reply_details_user_2['comment_id']
        self.post_request.POST = self.new_reply_details_user_2
        self.post_request.user = self.user_2
        self.assertRaises(Exception, add_reply, self.post_request)

    def test_add_reply_missing_content(self):
        del self.new_reply_details_user_1['content']
        self.post_request.POST = self.new_reply_details_user_1
        self.post_request.user = self.user_1
        self.assertRaises(Exception, add_reply, self.post_request)

        del self.new_reply_details_user_2['content']
        self.post_request.POST = self.new_reply_details_user_2
        self.post_request.user = self.user_2
        self.assertRaises(Exception, add_reply, self.post_request)

    def test_add_reply_missing_args(self):
        for i in range(10):
            dict_copy = self.new_reply_details_user_1.copy()
            args_to_remove = []
            for j in range(0, (random.randint(1, len(self.new_reply_details_user_1.keys()) - 1))):
                args_to_remove.append(list(self.new_reply_details_user_1.keys())[j])
            for j in range(len(args_to_remove)):
                del self.new_reply_details_user_1[args_to_remove[j]]
            len_replies = len(Reply.objects.filter(comment_id=self.comment_2.id))
            self.post_request.POST = self.new_reply_details_user_1
            self.post_request.user = self.user_1
            self.assertRaises(Exception, add_reply, self.post_request)
            self.assertTrue(len(Reply.objects.filter(comment_id=self.comment_2.id)) == len_replies)
            self.new_reply_details_user_1 = dict_copy.copy()

    def test_add_reply_invalid_request(self):
        len_replies = len(Reply.objects.filter(comment_id=self.comment_2.id))
        self.get_request.POST = self.new_reply_details_user_1
        self.get_request.user = self.user_1
        self.assertRaises(Http404, add_reply, self.get_request)
        self.assertTrue(len(Reply.objects.filter(comment_id=self.comment_2.id)) == len_replies)

    def test_build_reply_by_user(self):
        len_replies = len(Reply.objects.all())
        build_reply(self.reply.comment_id,
                    self.reply.user_id,
                    self.reply.content)
        self.assertTrue(len(Reply.objects.all()) == len_replies + 1)
        new_reply = Reply.objects.all().order_by('-id').first()
        self.assertTrue(new_reply.id == self.num_of_saved_replies + 1)
        self.assertTrue(new_reply.comment_id == self.reply.comment_id)
        self.assertTrue(new_reply.user_id == self.reply.user_id)
        self.assertTrue(new_reply.content == self.reply.content)

    def test_build_reply_by_added_user(self):
        len_replies = len(Reply.objects.all())
        user_3 = User(username="User3", email='user3@gmail.com')
        user_3.save()
        self.reply.user_id = user_3.id
        build_reply(self.reply.comment_id,
                    self.reply.user_id,
                    self.reply.content)
        self.assertTrue(len(Reply.objects.all()) == len_replies + 1)
        new_reply = Reply.objects.all().order_by('-id').first()
        self.assertTrue(new_reply.id == self.num_of_saved_replies + 1)
        self.assertTrue(new_reply.comment_id == self.reply.comment_id)
        self.assertTrue(new_reply.user_id == self.reply.user_id)
        self.assertTrue(new_reply.content == self.reply.content)
