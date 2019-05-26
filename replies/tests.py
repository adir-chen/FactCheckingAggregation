from django.http import HttpRequest, QueryDict
from django.core.exceptions import PermissionDenied
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

        self.reply_1 = Reply(comment_id=self.comment_1.id,
                             user_id=self.user_1.id,
                             content='replyContent1')
        self.reply_1.save()
        self.reply_2 = Reply(comment_id=self.comment_1.id,
                             user_id=self.user_2.id,
                             content='replyContent2')
        self.num_of_saved_replies = 1
        self.new_reply_details_user_1 = {'comment_id': self.comment_2.id,
                                         'content': 'content1',
                                         'is_superuser': True}
        self.new_reply_details_user_2 = {'comment_id': self.comment_1.id,
                                         'content': 'content2',
                                         'is_superuser': False}

        self.update_reply_details = {'reply_content': 'newContent'}

        self.post_request = HttpRequest()
        self.post_request.method = 'POST'

        self.get_request = HttpRequest()
        self.get_request.method = 'GET'

        self.error_code = 404

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
        self.assertRaises(PermissionDenied, add_reply, self.post_request)

    def test_add_reply_by_invalid_user(self):
        guest = User(id=self.num_of_saved_users + random.randint(1, 10), username='guest')
        self.post_request.POST = self.new_reply_details_user_1
        self.post_request.user = guest
        response = add_reply(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_add_reply_missing_comment_id(self):
        del self.new_reply_details_user_1['comment_id']
        self.post_request.POST = self.new_reply_details_user_1
        self.post_request.user = self.user_1
        response = add_reply(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

        del self.new_reply_details_user_2['comment_id']
        self.post_request.POST = self.new_reply_details_user_2
        self.post_request.user = self.user_2
        response = add_reply(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_add_reply_missing_content(self):
        del self.new_reply_details_user_1['content']
        self.post_request.POST = self.new_reply_details_user_1
        self.post_request.user = self.user_1
        response = add_reply(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

        del self.new_reply_details_user_2['content']
        self.post_request.POST = self.new_reply_details_user_2
        self.post_request.user = self.user_2
        response = add_reply(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

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
            response = add_reply(self.post_request)
            self.assertTrue(response.status_code == self.error_code)
            self.assertTrue(len(Reply.objects.filter(comment_id=self.comment_2.id)) == len_replies)
            self.new_reply_details_user_1 = dict_copy.copy()

    def test_add_reply_invalid_request(self):
        len_replies = len(Reply.objects.filter(comment_id=self.comment_2.id))
        self.get_request.POST = self.new_reply_details_user_1
        self.get_request.user = self.user_1
        self.assertRaises(PermissionDenied, add_reply, self.get_request)
        self.assertTrue(len(Reply.objects.filter(comment_id=self.comment_2.id)) == len_replies)

    def test_build_reply_by_user(self):
        len_replies = len(Reply.objects.all())
        build_reply(self.reply_2.comment_id,
                    self.reply_2.user_id,
                    self.reply_2.content)
        self.assertTrue(len(Reply.objects.all()) == len_replies + 1)
        new_reply = Reply.objects.all().order_by('-id').first()
        self.assertTrue(new_reply.id == self.num_of_saved_replies + 1)
        self.assertTrue(new_reply.comment_id == self.reply_2.comment_id)
        self.assertTrue(new_reply.user_id == self.reply_2.user_id)
        self.assertTrue(new_reply.content == self.reply_2.content)

    def test_build_reply_by_added_user(self):
        len_replies = len(Reply.objects.all())
        user_3 = User(username="User3", email='user3@gmail.com')
        user_3.save()
        self.reply_2.user_id = user_3.id
        build_reply(self.reply_2.comment_id,
                    self.reply_2.user_id,
                    self.reply_2.content)
        self.assertTrue(len(Reply.objects.all()) == len_replies + 1)
        new_reply = Reply.objects.all().order_by('-id').first()
        self.assertTrue(new_reply.id == self.num_of_saved_replies + 1)
        self.assertTrue(new_reply.comment_id == self.reply_2.comment_id)
        self.assertTrue(new_reply.user_id == self.reply_2.user_id)
        self.assertTrue(new_reply.content == self.reply_2.content)

    def test_check_if_reply_is_valid(self):
        self.new_reply_details_user_1['user_id'] = str(self.user_1.id)
        self.new_reply_details_user_2['user_id'] = str(self.user_2.id)
        self.assertTrue(check_if_reply_is_valid(self.new_reply_details_user_1))
        self.assertTrue(check_if_reply_is_valid(self.new_reply_details_user_2))

    def test_check_if_reply_is_valid_missing_user_id(self):
        self.assertFalse(check_if_reply_is_valid(self.new_reply_details_user_1)[0])
        self.assertFalse(check_if_reply_is_valid(self.new_reply_details_user_2)[0])

    def test_check_if_reply_is_valid_invalid_user_id(self):
        self.new_reply_details_user_1['user_id'] = self.num_of_saved_users + random.randint(1, 10)
        self.new_reply_details_user_2['user_id'] = self.num_of_saved_users + random.randint(1, 10)
        self.assertFalse(check_if_reply_is_valid(self.new_reply_details_user_1)[0])
        self.assertFalse(check_if_reply_is_valid(self.new_reply_details_user_2)[0])

    def test_check_if_reply_is_valid_missing_user_type(self):
        self.new_reply_details_user_1['user_id'] = str(self.user_1.id)
        self.new_reply_details_user_2['user_id'] = str(self.user_2.id)
        del self.new_reply_details_user_1['is_superuser']
        del self.new_reply_details_user_2['is_superuser']
        self.assertFalse(check_if_reply_is_valid(self.new_reply_details_user_1)[0])
        self.assertFalse(check_if_reply_is_valid(self.new_reply_details_user_2)[0])

    def test_check_if_reply_is_valid_missing_comment_id(self):
        self.new_reply_details_user_1['user_id'] = str(self.user_1.id)
        self.new_reply_details_user_2['user_id'] = str(self.user_2.id)
        del self.new_reply_details_user_1['comment_id']
        del self.new_reply_details_user_2['comment_id']
        self.assertFalse(check_if_reply_is_valid(self.new_reply_details_user_1)[0])
        self.assertFalse(check_if_reply_is_valid(self.new_reply_details_user_2)[0])

    def test_check_if_reply_is_valid_invalid_comment_id(self):
        self.new_reply_details_user_1['user_id'] = str(self.user_1.id)
        self.new_reply_details_user_2['user_id'] = str(self.user_2.id)
        self.new_reply_details_user_1['comment_id'] = self.num_of_saved_comments + random.randint(1, 10)
        self.new_reply_details_user_2['comment_id'] = self.num_of_saved_comments + random.randint(1, 10)
        self.assertFalse(check_if_reply_is_valid(self.new_reply_details_user_1)[0])
        self.assertFalse(check_if_reply_is_valid(self.new_reply_details_user_2)[0])

    def test_check_if_reply_is_valid_missing_content(self):
        self.new_reply_details_user_1['user_id'] = str(self.user_1.id)
        self.new_reply_details_user_2['user_id'] = str(self.user_2.id)
        del self.new_reply_details_user_1['content']
        del self.new_reply_details_user_2['content']
        self.assertFalse(check_if_reply_is_valid(self.new_reply_details_user_1)[0])
        self.assertFalse(check_if_reply_is_valid(self.new_reply_details_user_2)[0])

    def test_check_if_reply_is_valid_invalid_content(self):
        self.new_reply_details_user_1['user_id'] = str(self.user_1.id)
        self.new_reply_details_user_2['user_id'] = str(self.user_2.id)
        self.new_reply_details_user_1['content'] = "קלט שאיננו בשפה האנגלית"
        self.new_reply_details_user_2['content'] = "文字无效"
        self.assertFalse(check_if_reply_is_valid(self.new_reply_details_user_1)[0])
        self.assertFalse(check_if_reply_is_valid(self.new_reply_details_user_2)[0])

    def test_check_if_reply_is_valid_another_user(self):
        self.new_reply_details_user_1['is_superuser'] = False
        self.new_reply_details_user_1['user_id'] = str(self.user_1.id)
        self.new_reply_details_user_2['user_id'] = str(self.user_2.id)
        for i in range(5):
            self.assertTrue(check_if_reply_is_valid(self.new_reply_details_user_1)[0])
            self.assertTrue(check_if_reply_is_valid(self.new_reply_details_user_2)[0])
            self.post_request.POST = self.new_reply_details_user_1
            self.post_request.user = self.user_1
            self.assertTrue(add_reply(self.post_request).status_code == 200)
            self.post_request.POST = self.new_reply_details_user_2
            self.post_request.user = self.user_2
            self.assertTrue(add_reply(self.post_request).status_code == 200)
        self.assertFalse(check_if_reply_is_valid(self.new_reply_details_user_1)[0])
        self.assertFalse(check_if_reply_is_valid(self.new_reply_details_user_2)[0])

    def test_edit_reply(self):
        self.update_reply_details['reply_id'] = str(self.reply_1.id)
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.update_reply_details)
        self.post_request.POST = query_dict
        self.post_request.user = self.user_1
        self.assertTrue(edit_reply(self.post_request).status_code == 200)
        new_reply = Reply.objects.filter(id=self.reply_1.id).first()
        self.assertTrue(new_reply.id == int(self.update_reply_details['reply_id']))
        self.assertTrue(new_reply.comment_id == self.comment_1.id)
        self.assertTrue(new_reply.user_id == self.user_1.id)
        self.assertTrue(new_reply.content == self.update_reply_details['reply_content'])

    def test_edit_reply_by_user_not_his_reply(self):
        self.update_reply_details['reply_id'] = str(self.reply_1.id)
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.update_reply_details)
        self.post_request.POST = query_dict
        self.post_request.user = self.user_2
        response = edit_reply(self.post_request)
        self.assertTrue(response.status_code == self.error_code)
        reply = Reply.objects.filter(id=self.reply_1.id).first()
        self.assertTrue(reply.id == self.reply_1.id)
        self.assertTrue(reply.comment_id == self.reply_1.comment_id)
        self.assertTrue(reply.user_id == self.reply_1.user_id)
        self.assertTrue(reply.content == self.reply_1.content)

    def test_edit_reply_by_invalid_user_id(self):
        user = User(id=self.num_of_saved_users + random.randint(1, 10), email='user@gmail.com')
        self.update_reply_details['reply_id'] = str(self.reply_1.id)
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.update_reply_details)
        self.post_request.POST = query_dict
        self.post_request.user = user
        response = edit_reply(self.post_request)
        self.assertTrue(response.status_code == self.error_code)
        reply = Reply.objects.filter(id=self.reply_1.id).first()
        self.assertTrue(reply.id == self.reply_1.id)
        self.assertTrue(reply.comment_id == self.reply_1.comment_id)
        self.assertTrue(reply.user_id == self.reply_1.user_id)
        self.assertTrue(reply.content == self.reply_1.content)

    def test_edit_reply_by_invalid_reply_id(self):
        self.update_reply_details['reply_id'] = self.num_of_saved_replies + random.randint(1, 10)
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.update_reply_details)
        self.post_request.POST = query_dict
        self.post_request.user = self.user_1
        response = edit_reply(self.post_request)
        self.assertTrue(response.status_code == self.error_code)
        reply = Reply.objects.filter(id=self.reply_1.id).first()
        self.assertTrue(reply.id == self.reply_1.id)
        self.assertTrue(reply.comment_id == self.reply_1.comment_id)
        self.assertTrue(reply.user_id == self.reply_1.user_id)
        self.assertTrue(reply.content == self.reply_1.content)

    def test_edit_reply_missing_args(self):
        self.update_reply_details['reply_id'] = str(self.reply_1.id)
        for i in range(10):
            dict_copy = self.update_reply_details.copy()
            args_to_remove = []
            for j in range(0, (random.randint(1, len(self.update_reply_details.keys()) - 1))):
                args_to_remove.append(list(self.update_reply_details.keys())[j])
            for j in range(len(args_to_remove)):
                del self.update_reply_details[args_to_remove[j]]
            query_dict = QueryDict('', mutable=True)
            query_dict.update(self.update_reply_details)
            self.post_request.POST = query_dict
            self.post_request.user = self.user_1
            response = edit_reply(self.post_request)
            self.assertTrue(response.status_code == self.error_code)
            self.update_reply_details = dict_copy.copy()

    def test_edit_reply_invalid_request(self):
        self.update_reply_details['reply_id'] = str(self.reply_1.id)
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.update_reply_details)
        self.get_request.POST = query_dict
        self.get_request.user = self.user_1
        self.assertRaises(PermissionDenied, edit_reply, self.get_request)

    def test_check_reply_new_fields(self):
        self.update_reply_details['reply_id'] = str(self.reply_1.id)
        self.update_reply_details['user_id'] = str(self.user_1.id)
        self.update_reply_details['is_superuser'] = False
        self.assertTrue(check_reply_new_fields(self.update_reply_details)[0])
        self.update_reply_details['is_superuser'] = True
        self.assertTrue(check_reply_new_fields(self.update_reply_details)[0])

    def test_check_reply_new_fields_missing_user_id(self):
        self.update_reply_details['reply_id'] = str(self.reply_1.id)
        self.update_reply_details['is_superuser'] = False
        self.assertFalse(check_reply_new_fields(self.update_reply_details)[0])
        self.update_reply_details['is_superuser'] = True
        self.assertFalse(check_reply_new_fields(self.update_reply_details)[0])

    def test_check_comment_new_fields_invalid_user_id(self):
        self.update_reply_details['reply_id'] = str(self.reply_1.id)
        self.update_reply_details['user_id'] = str(self.num_of_saved_users + random.randint(1, 10))
        self.update_reply_details['is_superuser'] = False
        self.assertFalse(check_reply_new_fields(self.update_reply_details)[0])
        self.update_reply_details['is_superuser'] = True
        self.assertFalse(check_reply_new_fields(self.update_reply_details)[0])

    def test_check_reply_new_fields_missing_user_type(self):
        self.update_reply_details['reply_id'] = str(self.reply_1.id)
        self.update_reply_details['user_id'] = str(self.user_1.id)
        self.assertFalse(check_reply_new_fields(self.update_reply_details)[0])

    def test_check_reply_new_fields_missing_reply_id(self):
        self.update_reply_details['user_id'] = str(self.user_1.id)
        self.update_reply_details['is_superuser'] = False
        self.assertFalse(check_reply_new_fields(self.update_reply_details)[0])
        self.update_reply_details['is_superuser'] = True
        self.assertFalse(check_reply_new_fields(self.update_reply_details)[0])

    def test_check_comment_new_fields_invalid_reply_id(self):
        self.update_reply_details['reply_id'] = str(self.num_of_saved_replies + random.randint(1, 10))
        self.update_reply_details['user_id'] = str(self.user_1.id)
        self.update_reply_details['is_superuser'] = False
        self.assertFalse(check_reply_new_fields(self.update_reply_details)[0])
        self.update_reply_details['is_superuser'] = True
        self.assertFalse(check_reply_new_fields(self.update_reply_details)[0])

    def test_check_reply_new_fields_missing_content(self):
        self.update_reply_details['reply_id'] = str(self.reply_1.id)
        self.update_reply_details['user_id'] = str(self.user_1.id)
        del self.update_reply_details['reply_content']
        self.update_reply_details['is_superuser'] = False
        self.assertFalse(check_reply_new_fields(self.update_reply_details)[0])
        self.update_reply_details['is_superuser'] = True
        self.assertFalse(check_reply_new_fields(self.update_reply_details)[0])

    def test_check_reply_new_fields_edit_after_ten_minutes(self):
        Reply.objects.filter(id=self.reply_1.id).update(timestamp=datetime.datetime.now() -
                                                        datetime.timedelta(minutes=11))
        self.update_reply_details['reply_id'] = str(self.reply_1.id)
        self.update_reply_details['user_id'] = str(self.user_1.id)
        self.update_reply_details['is_superuser'] = False
        self.assertFalse(check_reply_new_fields(self.update_reply_details)[0])
        self.update_reply_details['is_superuser'] = True
        self.assertTrue(check_reply_new_fields(self.update_reply_details)[0])

    def test_check_comment_new_fields_invalid_input_for_content(self):
        self.update_reply_details['reply_id'] = str(self.reply_1.id)
        self.update_reply_details['user_id'] = str(self.user_1.id)
        self.update_reply_details['reply_content'] = 'Խոսքի խառնաշփոթի խառնաշփոթություն'
        self.update_reply_details['is_superuser'] = False
        self.assertFalse(check_reply_new_fields(self.update_reply_details)[0])
        self.update_reply_details['is_superuser'] = True
        self.assertFalse(check_reply_new_fields(self.update_reply_details)[0])

    def test_delete_reply_by_user(self):
        reply_to_delete = {'reply_id': self.reply_1.id}
        self.post_request.POST = reply_to_delete
        self.post_request.user = self.user_1
        len_replies = len(Reply.objects.all())
        response = delete_reply(self.post_request)
        self.assertTrue(len(Reply.objects.all()) == len_replies - 1)
        self.assertTrue(response.status_code == 200)

    def test_delete_reply_by_user_not_his_reply(self):
        reply_to_delete = {'reply_id': self.reply_1.id}
        self.post_request.POST = reply_to_delete
        self.post_request.user = self.user_2
        len_replies = len(Reply.objects.all())
        response = delete_reply(self.post_request)
        self.assertTrue(response.status_code == self.error_code)
        self.assertTrue(len(Reply.objects.all()) == len_replies)

    def test_delete_reply_by_invalid_user(self):
        user = User(id=self.num_of_saved_users + random.randint(1, 10), email='user@gmail.com')
        reply_to_delete = {'reply_id': self.reply_1.id}
        self.post_request.POST = reply_to_delete
        self.post_request.user = user
        len_replies = len(Reply.objects.all())
        response = delete_reply(self.post_request)
        self.assertTrue(response.status_code == self.error_code)
        self.assertTrue(len(Reply.objects.all()) == len_replies)

    def test_delete_reply_by_not_authenticated_user(self):
        from django.contrib.auth.models import AnonymousUser
        reply_to_delete = {'reply_id': self.reply_1.id}
        self.post_request.POST = reply_to_delete
        self.post_request.user = AnonymousUser()
        len_replies = len(Reply.objects.all())
        self.assertRaises(PermissionDenied, delete_reply, self.post_request)
        self.assertTrue(len(Reply.objects.all()) == len_replies)

    def test_delete_reply_by_invalid_reply_id(self):
        reply_to_delete = {'reply_id': self.num_of_saved_replies + random.randint(1, 10)}
        self.post_request.POST = reply_to_delete
        self.post_request.user = self.user_1
        len_replies = len(Reply.objects.all())
        response = delete_reply(self.post_request)
        self.assertTrue(response.status_code == self.error_code)
        self.assertTrue(len(Reply.objects.all()) == len_replies)

    def test_delete_reply_invalid_request(self):
        reply_to_delete = {'reply_id': self.reply_1.id}
        self.get_request.POST = reply_to_delete
        self.get_request.user = self.user_1
        len_replies = len(Reply.objects.all())
        self.assertRaises(PermissionDenied, delete_reply, self.get_request)
        self.assertTrue(len(Reply.objects.all()) == len_replies)

    def test_check_if_delete_reply_is_valid(self):
        reply_to_delete = {'reply_id': self.reply_1.id}
        self.post_request.POST = reply_to_delete
        self.post_request.user = self.user_1
        self.assertTrue(check_if_delete_reply_is_valid(self.post_request)[0])

    def test_check_if_delete_reply_is_valid_missing_reply_id(self):
        self.post_request.user = self.user_1
        self.assertFalse(check_if_delete_reply_is_valid(self.post_request)[0])

    def test_check_if_delete_reply_is_valid_invalid_reply_id(self):
        reply_to_delete = {'reply_id': self.num_of_saved_replies + random.randint(1, 10)}
        self.post_request.POST = reply_to_delete
        self.post_request.user = self.user_1
        self.assertFalse(check_if_delete_reply_is_valid(self.post_request)[0])

    def test_check_if_delete_reply_is_valid_invalid_user_id(self):
        user = User(id=self.num_of_saved_users + random.randint(1, 10), email='user@gmail.com')
        reply_to_delete = {'reply_id': self.reply_1.id}
        self.post_request.POST = reply_to_delete
        self.post_request.user = user
        self.assertFalse(check_if_delete_reply_is_valid(self.post_request)[0])

    def test_check_if_delete_reply_is_valid_another_user(self):
        reply_to_delete = {'reply_id': self.reply_1.id}
        self.post_request.POST = reply_to_delete
        self.post_request.user = self.user_2
        self.assertFalse(check_if_delete_reply_is_valid(self.post_request)[0])

    ################
    # Models Tests #
    ################

    def test__str__(self):
        self.assertTrue(self.reply_1.__str__() ==
                        self.reply_1.user.username + ' replied to comment ' +
                        str(self.reply_1.comment.id) + ' in claim ' + str(self.claim_1.id))


