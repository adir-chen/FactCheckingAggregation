from django.http import HttpRequest, QueryDict
from django.core.exceptions import PermissionDenied
from django.test import TestCase
from django.test.utils import override_settings
from django.utils.datastructures import MultiValueDict
from claims.models import Claim
from comments.models import Comment
from comments.views import add_comment, build_comment, check_if_comment_is_valid, is_valid_url, convert_date_format, \
    is_valid_verdict_date, get_system_label_to_comment, edit_comment, check_comment_new_fields, \
    delete_comment, check_if_delete_comment_is_valid, up_vote, down_vote, check_if_vote_is_valid, \
    export_to_csv, check_if_csv_fields_are_valid, check_if_fields_and_scrapers_lists_valid, \
    create_df_for_claims, get_all_comments_for_user_id, get_all_comments_for_claim_id, \
    update_authenticity_grade, update_authenticity_grade_for_all_claims
from replies.models import Reply
from users.models import User, Scrapers, Users_Reputations
import datetime
import string
import random


class CommentTests(TestCase):
    def setUp(self):
        self.user_1 = User(username="User1", email='user1@gmail.com')
        self.user_2 = User(username="User2", email='user2@gmail.com')
        self.user_1.save()
        self.user_2.save()
        self.user_1_rep = Users_Reputations(user=self.user_1, reputation=100)
        self.user_2_rep = Users_Reputations(user=self.user_2, reputation=1)
        self.user_1_rep.save()
        self.user_2_rep.save()
        self.new_scraper_1 = User(username="newScraper1")
        self.new_scraper_1.save()
        self.new_scraper_scraper_1 = Scrapers(scraper_name=self.new_scraper_1.username,
                                              scraper=self.new_scraper_1)
        self.new_scraper_scraper_1.save()

        self.new_scraper_2 = User(username="newScraper2")
        self.new_scraper_2.save()
        self.new_scraper_scraper_2 = Scrapers(scraper_name=self.new_scraper_2.username,
                                              scraper=self.new_scraper_2)
        self.new_scraper_scraper_2.save()
        self.num_of_saved_users = 4
        self.num_of_saved_scrapers = 2
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
        self.claim_3 = Claim(user_id=self.new_scraper_1.id,
                             claim='claim3',
                             category='category3',
                             tags='',
                             authenticity_grade=0)
        self.claim_4 = Claim(user_id=self.new_scraper_2.id,
                             claim='claim4',
                             category='category4',
                             tags='tag4,tag5,tag6',
                             authenticity_grade=0)
        self.claim_1.save()
        self.claim_2.save()
        self.claim_3.save()
        self.claim_4.save()
        self.num_of_saved_claims = 4
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
        self.comment_3 = Comment(claim_id=self.claim_1.id,
                                 user_id=self.user_2.id,
                                 title=self.claim_1.claim,
                                 description='description3',
                                 url=self.url + str(random.randint(1, 10)),
                                 tags='',
                                 verdict_date=datetime.date.today() - datetime.timedelta(days=random.randint(1, 10)),
                                 label='label3')
        self.comment_4 = Comment(claim_id=self.claim_2.id,
                                 user_id=self.user_1.id,
                                 title=self.claim_2.claim,
                                 description='description4',
                                 url=self.url + str(random.randint(1, 10)),
                                 tags='',
                                 verdict_date=datetime.date.today() - datetime.timedelta(days=random.randint(1, 10)),
                                 label='label4')
        self.comment_5 = Comment(claim_id=self.claim_3.id,
                                 user_id=self.claim_3.user_id,
                                 title=self.claim_3.claim,
                                 description='description5',
                                 url=self.url + str(random.randint(1, 10)),
                                 tags='',
                                 verdict_date=datetime.date.today() - datetime.timedelta(days=random.randint(1, 10)),
                                 label='label5')
        self.comment_6 = Comment(claim_id=self.claim_4.id,
                                 user_id=self.claim_4.user_id,
                                 title=self.claim_4.claim,
                                 description='description6',
                                 url=self.url + str(random.randint(1, 10)),
                                 tags='',
                                 verdict_date=datetime.date.today() - datetime.timedelta(days=random.randint(1, 10)),
                                 label='label6')
        self.comment_1.save()
        self.comment_2.save()
        self.comment_5.save()
        self.comment_6.save()
        self.num_of_saved_comments = 4

        self.reply_1 = Reply(user_id=self.user_1.id,
                             comment_id=self.comment_1.id,
                             content='content')
        self.reply_1.save()
        self.reply_2 = Reply(user_id=self.user_1.id,
                             comment_id=self.comment_1.id,
                             content='content')
        self.reply_2.save()
        self.reply_3 = Reply(user_id=self.user_2.id,
                             comment_id=self.comment_2.id,
                             content='content')
        self.reply_3.save()
        self.num_of_saved_replies = 3

        self.SITE_KEY_TEST = '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI'

        self.new_comment_details_user_1 = {'claim_id': self.comment_4.claim_id,
                                           'title': self.comment_4.title,
                                           'description': self.comment_4.description,
                                           'url': self.comment_4.url,
                                           'verdict_date': datetime.datetime.strptime(str(self.comment_4.verdict_date), '%Y-%m-%d').strftime('%d/%m/%Y'),
                                           'label': self.comment_4.label,
                                           'is_superuser': True,
                                           'g_recaptcha_response': self.SITE_KEY_TEST}
        self.new_comment_details_user_2 = {'claim_id': self.comment_3.claim_id,
                                           'title': self.comment_3.title,
                                           'description': self.comment_3.description,
                                           'url': self.comment_3.url,
                                           'verdict_date': datetime.datetime.strptime(str(self.comment_3.verdict_date), '%Y-%m-%d').strftime('%d/%m/%Y'),
                                           'label': self.comment_3.label,
                                           'is_superuser': False,
                                           'g_recaptcha_response': self.SITE_KEY_TEST}

        self.update_comment_details = {'comment_title': self.comment_3.title,
                                       'comment_description': self.comment_3.description,
                                       'comment_reference': self.comment_3.url,
                                       'comment_verdict_date': datetime.datetime.strptime(str(self.comment_3.verdict_date), '%Y-%m-%d').strftime('%d/%m/%Y'),
                                       'comment_label': 'true'}

        self.csv_fields = MultiValueDict({
            'fields_to_export[]': ["Title", "Description", "Url", "Category", "Verdict Date", "Tags", "Label", "System Label", "Authenticity Grade"],
            'scrapers_ids[]': [str(self.new_scraper_1.id), str(self.new_scraper_2.id)],
            'verdict_date_start': [str(datetime.date.today() - datetime.timedelta(days=20))],
            'verdict_date_end': [str(datetime.date.today())]})

        self.post_request = HttpRequest()
        self.post_request.method = 'POST'

        self.get_request = HttpRequest()
        self.get_request.method = 'GET'

        self.error_code = 404

    def tearDown(self):
        pass

    def test_add_comment_by_user_1(self):
        len_comments = len(Comment.objects.filter(claim_id=self.claim_2.id))
        self.post_request.POST = self.new_comment_details_user_1
        self.post_request.user = self.user_1
        self.assertTrue(add_comment(self.post_request).status_code == 200)
        self.assertTrue(len(Comment.objects.filter(claim_id=self.claim_2.id)) == len_comments + 1)
        new_comment = Comment.objects.all().order_by('-id').first()
        self.assertTrue(new_comment.id == self.num_of_saved_comments + 1)
        self.assertTrue(new_comment.claim_id == self.comment_4.claim_id)
        self.assertTrue(new_comment.user_id == self.comment_4.user_id)
        self.assertTrue(new_comment.title == self.comment_4.title)
        self.assertTrue(new_comment.description == self.comment_4.description)
        self.assertTrue(new_comment.url == self.comment_4.url)
        self.assertTrue(new_comment.verdict_date == self.comment_4.verdict_date)
        self.assertTrue(new_comment.label == self.comment_4.label)

    def test_add_comment_by_user_2(self):
        len_comments = len(Comment.objects.filter(claim_id=self.claim_1.id))
        self.post_request.POST = self.new_comment_details_user_2
        self.post_request.user = self.user_2
        self.assertTrue(add_comment(self.post_request).status_code == 200)
        self.assertTrue(len(Comment.objects.filter(claim_id=self.claim_1.id)) == len_comments + 1)
        new_comment = Comment.objects.all().order_by('-id').first()
        self.assertTrue(new_comment.id == self.num_of_saved_comments + 1)
        self.assertTrue(new_comment.claim_id == self.comment_3.claim_id)
        self.assertTrue(new_comment.user_id == self.comment_3.user_id)
        self.assertTrue(new_comment.title == self.comment_3.title)
        self.assertTrue(new_comment.description == self.comment_3.description)
        self.assertTrue(new_comment.url == self.comment_3.url)
        self.assertTrue(new_comment.verdict_date == self.comment_3.verdict_date)
        self.assertTrue(new_comment.label == self.comment_3.label)

    @override_settings(DEBUG=False)
    def test_add_comment_by_user_2_on_user_1_claim(self):
        len_comments = len(Comment.objects.filter(claim_id=self.claim_1.id))
        self.new_comment_details_user_2['claim_id'] = self.claim_1.id
        self.post_request.POST = self.new_comment_details_user_2
        self.post_request.user = self.user_2
        self.assertTrue(add_comment(self.post_request).status_code == 200)
        self.assertTrue(len(Comment.objects.filter(claim_id=self.claim_1.id)) == len_comments + 1)
        new_comment = Comment.objects.all().order_by('-id').first()
        self.assertTrue(new_comment.id == self.num_of_saved_comments + 1)
        self.assertTrue(new_comment.claim_id == self.claim_1.id)
        self.assertTrue(new_comment.user_id == self.comment_3.user_id)
        self.assertTrue(new_comment.title == self.comment_3.title)
        self.assertTrue(new_comment.description == self.comment_3.description)
        self.assertTrue(new_comment.url == self.comment_3.url)
        self.assertTrue(new_comment.verdict_date == self.comment_3.verdict_date)
        self.assertTrue(new_comment.label == self.comment_3.label)

    def test_add_comment_by_user_not_authenticated(self):
        from django.contrib.auth.models import AnonymousUser
        self.post_request.POST = self.new_comment_details_user_1
        self.post_request.user = AnonymousUser()
        self.assertRaises(PermissionDenied, add_comment, self.post_request)

    def test_add_comment_by_invalid_user(self):
        guest = User(id=self.num_of_saved_users + random.randint(1, 10), username='guest')
        self.post_request.POST = self.new_comment_details_user_1
        self.post_request.user = guest
        response = add_comment(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_add_comment_missing_claim_id(self):
        del self.new_comment_details_user_1['claim_id']
        self.post_request.POST = self.new_comment_details_user_1
        self.post_request.user = self.user_1
        response = add_comment(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

        del self.new_comment_details_user_2['claim_id']
        self.post_request.POST = self.new_comment_details_user_2
        self.post_request.user = self.user_2
        response = add_comment(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_add_comment_missing_title(self):
        del self.new_comment_details_user_1['title']
        self.post_request.POST = self.new_comment_details_user_1
        self.post_request.user = self.user_1
        response = add_comment(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

        del self.new_comment_details_user_2['title']
        self.post_request.POST = self.new_comment_details_user_2
        self.post_request.user = self.user_2
        response = add_comment(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_add_comment_missing_description(self):
        del self.new_comment_details_user_1['description']
        self.post_request.POST = self.new_comment_details_user_1
        self.post_request.user = self.user_1
        response = add_comment(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

        del self.new_comment_details_user_2['description']
        self.post_request.POST = self.new_comment_details_user_2
        self.post_request.user = self.user_2
        response = add_comment(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_add_comment_missing_url(self):
        del self.new_comment_details_user_1['url']
        self.post_request.POST = self.new_comment_details_user_1
        self.post_request.user = self.user_1
        response = add_comment(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

        del self.new_comment_details_user_2['url']
        self.post_request.POST = self.new_comment_details_user_2
        self.post_request.user = self.user_2
        response = add_comment(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_add_comment_missing_verdict_date(self):
        del self.new_comment_details_user_1['verdict_date']
        self.post_request.POST = self.new_comment_details_user_1
        self.post_request.user = self.user_1
        response = add_comment(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

        del self.new_comment_details_user_2['verdict_date']
        self.post_request.POST = self.new_comment_details_user_2
        self.post_request.user = self.user_2
        response = add_comment(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_add_comment_missing_label(self):
        del self.new_comment_details_user_1['label']
        self.post_request.POST = self.new_comment_details_user_1
        self.post_request.user = self.user_1
        response = add_comment(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

        del self.new_comment_details_user_2['label']
        self.post_request.POST = self.new_comment_details_user_2
        self.post_request.user = self.user_2
        response = add_comment(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_add_comment_missing_args(self):
        for i in range(10):
            dict_copy = self.new_comment_details_user_1.copy()
            args_to_remove = []
            for j in range(0, (random.randint(1, len(self.new_comment_details_user_1.keys()) - 1))):
                args_to_remove.append(list(self.new_comment_details_user_1.keys())[j])
            for j in range(len(args_to_remove)):
                del self.new_comment_details_user_1[args_to_remove[j]]
            len_comments = len(Comment.objects.filter(claim_id=self.claim_1.id))
            self.post_request.POST = self.new_comment_details_user_1
            self.post_request.user = self.user_1
            response = add_comment(self.post_request)
            self.assertTrue(response.status_code == self.error_code)
            self.assertTrue(len(Comment.objects.filter(claim_id=self.claim_1.id)) == len_comments)
            self.new_comment_details_user_1 = dict_copy.copy()

    def test_add_comment_invalid_request(self):
        len_comments = len(Comment.objects.filter(claim_id=self.claim_2.id))
        self.get_request.POST = self.new_comment_details_user_1
        self.get_request.user = self.user_1
        self.assertRaises(PermissionDenied, add_comment, self.get_request)
        self.assertTrue(len(Comment.objects.filter(claim_id=self.claim_2.id)) == len_comments)

    def test_build_comment_by_user(self):
        len_comments = len(Comment.objects.all())
        build_comment(self.comment_4.claim_id,
                      self.comment_4.user_id,
                      self.comment_4.title,
                      self.comment_4.description,
                      self.comment_4.url,
                      self.comment_4.tags,
                      datetime.datetime.strptime(str(self.comment_4.verdict_date), '%Y-%m-%d').strftime("%d/%m/%Y"),
                      self.comment_4.label)
        self.assertTrue(len(Comment.objects.all()) == len_comments + 1)
        new_comment = Comment.objects.all().order_by('-id').first()
        self.assertTrue(new_comment.id == self.num_of_saved_comments + 1)
        self.assertTrue(new_comment.claim_id == self.comment_4.claim_id)
        self.assertTrue(new_comment.user_id == self.comment_4.user_id)
        self.assertTrue(new_comment.title == self.comment_4.title)
        self.assertTrue(new_comment.description == self.comment_4.description)
        self.assertTrue(new_comment.url == self.comment_4.url)
        self.assertTrue(new_comment.tags == self.comment_4.tags)
        self.assertTrue(new_comment.verdict_date == self.comment_4.verdict_date)
        self.assertTrue(new_comment.label == self.comment_4.label)

    def test_build_comment_by_added_user(self):
        len_comments = len(Comment.objects.all())
        user_3 = User(username="User3", email='user3@gmail.com')
        user_3.save()
        self.comment_4.user_id = user_3.id
        build_comment(self.comment_4.claim_id,
                      self.comment_4.user_id,
                      self.comment_4.title,
                      self.comment_4.description,
                      self.comment_4.url,
                      self.comment_4.tags,
                      datetime.datetime.strptime(str(self.comment_4.verdict_date), '%Y-%m-%d').strftime("%d/%m/%Y"),
                      self.comment_4.label)
        self.assertTrue(len(Comment.objects.all()) == len_comments + 1)
        new_comment = Comment.objects.all().order_by('-id').first()
        self.assertTrue(new_comment.id == self.num_of_saved_comments + 1)
        self.assertTrue(new_comment.claim_id == self.comment_4.claim_id)
        self.assertTrue(new_comment.user_id == self.comment_4.user_id)
        self.assertTrue(new_comment.title == self.comment_4.title)
        self.assertTrue(new_comment.description == self.comment_4.description)
        self.assertTrue(new_comment.url == self.comment_4.url)
        self.assertTrue(new_comment.tags == self.comment_4.tags)
        self.assertTrue(new_comment.verdict_date == self.comment_4.verdict_date)
        self.assertTrue(new_comment.label == self.comment_4.label)

    def test_check_if_comment_is_valid(self):
        self.new_comment_details_user_1['user_id'] = str(self.user_1.id)
        self.new_comment_details_user_2['user_id'] = str(self.user_2.id)
        self.assertTrue(check_if_comment_is_valid(self.new_comment_details_user_1))
        self.assertTrue(check_if_comment_is_valid(self.new_comment_details_user_2))

    def test_check_if_comment_is_valid_missing_user_id(self):
        self.assertFalse(check_if_comment_is_valid(self.new_comment_details_user_1)[0])
        self.assertFalse(check_if_comment_is_valid(self.new_comment_details_user_2)[0])

    def test_check_if_comment_is_valid_missing_user_type(self):
        self.new_comment_details_user_1['user_id'] = str(self.user_1.id)
        self.new_comment_details_user_2['user_id'] = str(self.user_2.id)
        del self.new_comment_details_user_1['is_superuser']
        del self.new_comment_details_user_2['is_superuser']
        self.assertFalse(check_if_comment_is_valid(self.new_comment_details_user_1)[0])
        self.assertFalse(check_if_comment_is_valid(self.new_comment_details_user_2)[0])

    def test_check_if_comment_is_valid_missing_captcha(self):
        self.new_comment_details_user_1['user_id'] = str(self.user_1.id)
        self.new_comment_details_user_2['user_id'] = str(self.user_2.id)
        del self.new_comment_details_user_1['g_recaptcha_response']
        del self.new_comment_details_user_2['g_recaptcha_response']
        self.assertFalse(check_if_comment_is_valid(self.new_comment_details_user_1)[0])
        self.assertFalse(check_if_comment_is_valid(self.new_comment_details_user_2)[0])

    def test_check_if_comment_is_valid_missing_claim_id(self):
        self.new_comment_details_user_1['user_id'] = str(self.user_1.id)
        self.new_comment_details_user_2['user_id'] = str(self.user_2.id)
        del self.new_comment_details_user_1['claim_id']
        del self.new_comment_details_user_2['claim_id']
        self.assertFalse(check_if_comment_is_valid(self.new_comment_details_user_1)[0])
        self.assertFalse(check_if_comment_is_valid(self.new_comment_details_user_2)[0])

    def test_check_if_comment_is_valid_missing_title(self):
        self.new_comment_details_user_1['user_id'] = str(self.user_1.id)
        self.new_comment_details_user_2['user_id'] = str(self.user_2.id)
        del self.new_comment_details_user_1['title']
        del self.new_comment_details_user_2['title']
        self.assertFalse(check_if_comment_is_valid(self.new_comment_details_user_1)[0])
        self.assertFalse(check_if_comment_is_valid(self.new_comment_details_user_2)[0])

    def test_check_if_comment_is_valid_missing_description(self):
        self.new_comment_details_user_1['user_id'] = str(self.user_1.id)
        self.new_comment_details_user_2['user_id'] = str(self.user_2.id)
        del self.new_comment_details_user_1['description']
        del self.new_comment_details_user_2['description']
        self.assertFalse(check_if_comment_is_valid(self.new_comment_details_user_1)[0])
        self.assertFalse(check_if_comment_is_valid(self.new_comment_details_user_2)[0])

    def test_check_if_comment_is_valid_missing_url(self):
        self.new_comment_details_user_1['user_id'] = str(self.user_1.id)
        self.new_comment_details_user_2['user_id'] = str(self.user_2.id)
        del self.new_comment_details_user_1['url']
        del self.new_comment_details_user_2['url']
        self.assertFalse(check_if_comment_is_valid(self.new_comment_details_user_1)[0])
        self.assertFalse(check_if_comment_is_valid(self.new_comment_details_user_2)[0])

    def test_check_if_comment_is_valid_invalid_url(self):
        letters = string.ascii_lowercase
        self.new_comment_details_user_1['user_id'] = str(self.user_1.id)
        self.new_comment_details_user_2['user_id'] = str(self.user_2.id)
        self.new_comment_details_user_1['url'] = ''.join(random.choice(letters) for i in range(random.randint(1, 10)))
        self.new_comment_details_user_2['url'] = ''.join(random.choice(letters) for i in range(random.randint(1, 10)))
        self.assertFalse(check_if_comment_is_valid(self.new_comment_details_user_1)[0])
        self.assertFalse(check_if_comment_is_valid(self.new_comment_details_user_2)[0])

    def test_check_if_comment_is_valid_missing_label(self):
        self.new_comment_details_user_1['user_id'] = str(self.user_1.id)
        self.new_comment_details_user_2['user_id'] = str(self.user_2.id)
        del self.new_comment_details_user_1['label']
        del self.new_comment_details_user_2['label']
        self.assertFalse(check_if_comment_is_valid(self.new_comment_details_user_1)[0])
        self.assertFalse(check_if_comment_is_valid(self.new_comment_details_user_2)[0])

    def test_check_if_comment_is_valid_invalid_claim_id(self):
        self.new_comment_details_user_1['user_id'] = str(self.user_1.id)
        self.new_comment_details_user_2['user_id'] = str(self.user_2.id)
        self.new_comment_details_user_1['claim_id'] = str(self.num_of_saved_claims + random.randint(1, 10))
        self.new_comment_details_user_2['claim_id'] = str(self.num_of_saved_claims + random.randint(1, 10))
        self.assertFalse(check_if_comment_is_valid(self.new_comment_details_user_1)[0])
        self.assertFalse(check_if_comment_is_valid(self.new_comment_details_user_2)[0])

    def test_check_if_comment_is_valid_invalid_user_id(self):
        self.new_comment_details_user_1['user_id'] = str(self.num_of_saved_users + random.randint(1, 10))
        self.new_comment_details_user_2['user_id'] = str(self.num_of_saved_users + random.randint(1, 10))
        self.assertFalse(check_if_comment_is_valid(self.new_comment_details_user_1)[0])
        self.assertFalse(check_if_comment_is_valid(self.new_comment_details_user_2)[0])

    def test_check_if_comment_is_valid_comment_above_maximum(self):
        self.new_comment_details_user_1['user_id'] = str(self.user_1.id)
        self.new_comment_details_user_2['user_id'] = str(self.user_2.id)
        self.new_comment_details_user_1['claim_id'] = str(self.claim_1.id)
        self.new_comment_details_user_2['claim_id'] = str(self.claim_2.id)
        for i in range(4):
            self.assertTrue(check_if_comment_is_valid(self.new_comment_details_user_1)[0])
            self.assertTrue(check_if_comment_is_valid(self.new_comment_details_user_2)[0])
            self.post_request.POST = self.new_comment_details_user_1
            self.post_request.user = self.user_1
            self.assertTrue(add_comment(self.post_request).status_code == 200)
            self.post_request.POST = self.new_comment_details_user_2
            self.post_request.user = self.user_2
            self.assertTrue(add_comment(self.post_request).status_code == 200)
        self.assertTrue(check_if_comment_is_valid(self.new_comment_details_user_1)[0])
        self.assertFalse(check_if_comment_is_valid(self.new_comment_details_user_2)[0])

    def test_check_if_comment_is_valid_invalid_date_format(self):
        self.new_comment_details_user_1['user_id'] = str(self.user_1.id)
        self.new_comment_details_user_2['user_id'] = str(self.user_2.id)
        self.new_comment_details_user_1['verdict_date'] = datetime.datetime.strptime(str(self.comment_3.verdict_date), '%Y-%m-%d').strftime('%Y/%m/%d')
        self.new_comment_details_user_2['verdict_date'] = datetime.datetime.strptime(str(self.comment_4.verdict_date), '%Y-%m-%d').strftime('%Y/%d/%m')
        self.assertFalse(check_if_comment_is_valid(self.new_comment_details_user_1)[0])
        self.assertFalse(check_if_comment_is_valid(self.new_comment_details_user_2)[0])

    def test_check_if_comment_is_valid_invalid_date_format_with_invalid_with_hyphen(self):
        self.new_comment_details_user_1['user_id'] = str(self.user_1.id)
        self.new_comment_details_user_2['user_id'] = str(self.user_2.id)
        year = str(random.randint(2000, 2018))
        month = str(random.randint(1, 12))
        day = str(random.randint(1, 28))
        self.new_comment_details_user_1['verdict_date'] = year + '--' + month + '-' + day
        self.new_comment_details_user_2['verdict_date'] = year + '-' + month + '--' + day
        self.assertFalse(check_if_comment_is_valid(self.new_comment_details_user_1)[0])
        self.assertFalse(check_if_comment_is_valid(self.new_comment_details_user_2)[0])

    def test_check_if_comment_is_valid_invalid_input_for_title(self):
        self.new_comment_details_user_1['user_id'] = str(self.user_1.id)
        self.new_comment_details_user_2['user_id'] = str(self.user_2.id)
        self.new_comment_details_user_1['title'] = 'קלט בשפה שאינה אנגלית'
        self.new_comment_details_user_2['title'] = 'קלט בשפה שאינה אנגלית'
        self.assertFalse(check_if_comment_is_valid(self.new_comment_details_user_1)[0])
        self.assertFalse(check_if_comment_is_valid(self.new_comment_details_user_2)[0])

    def test_check_if_comment_is_valid_invalid_input_for_category(self):
        self.new_comment_details_user_1['user_id'] = str(self.user_1.id)
        self.new_comment_details_user_2['user_id'] = str(self.user_2.id)
        self.new_comment_details_user_1['description'] = 'المدخلات بلغة غير الإنجليزية'
        self.new_comment_details_user_2['description'] = 'المدخلات بلغة غير الإنجليزية'
        self.assertFalse(check_if_comment_is_valid(self.new_comment_details_user_1)[0])
        self.assertFalse(check_if_comment_is_valid(self.new_comment_details_user_2)[0])

    def test_check_if_comment_is_valid_invalid_input_for_tags(self):
        self.new_comment_details_user_1['user_id'] = str(self.user_1.id)
        self.new_comment_details_user_2['user_id'] = str(self.user_2.id)
        self.new_comment_details_user_1['tags'] = '输入英语以外的语言 输入英语以外的语言'
        self.new_comment_details_user_2['tags'] = '输入英语以外的语言 输入英语以外的语言'
        self.assertFalse(check_if_comment_is_valid(self.new_comment_details_user_1)[0])
        self.assertFalse(check_if_comment_is_valid(self.new_comment_details_user_2)[0])

    def test_check_if_comment_is_valid_with_tags(self):
        self.new_comment_details_user_1['user_id'] = str(self.user_1.id)
        self.new_comment_details_user_2['user_id'] = str(self.user_2.id)
        self.new_comment_details_user_1['tags'] = 'tag1,tag2'
        self.new_comment_details_user_2['tags'] = 'tag3,tag4'
        self.assertTrue(check_if_comment_is_valid(self.new_comment_details_user_1)[0])
        self.assertTrue(check_if_comment_is_valid(self.new_comment_details_user_2)[0])

    def test_check_if_comment_is_valid_with_invalid_format_for_tags(self):
        self.new_comment_details_user_1['user_id'] = str(self.user_1.id)
        self.new_comment_details_user_2['user_id'] = str(self.user_2.id)
        self.new_comment_details_user_1['tags'] = 'tag1,  tag2'
        self.new_comment_details_user_2['tags'] = 'tag3; tag4'
        self.assertFalse(check_if_comment_is_valid(self.new_comment_details_user_1)[0])
        self.assertFalse(check_if_comment_is_valid(self.new_comment_details_user_2)[0])

        self.new_comment_details_user_1['tags'] = 'tag1,,tag2'
        self.new_comment_details_user_2['tags'] = 'tag3,tag4, '
        self.assertFalse(check_if_comment_is_valid(self.new_comment_details_user_1)[0])
        self.assertFalse(check_if_comment_is_valid(self.new_comment_details_user_2)[0])

        self.new_comment_details_user_1['tags'] = 'tag1,?tag2'
        self.new_comment_details_user_2['tags'] = 'tag%,tag4'
        self.assertFalse(check_if_comment_is_valid(self.new_comment_details_user_1)[0])
        self.assertFalse(check_if_comment_is_valid(self.new_comment_details_user_2)[0])

    def test_is_valid_url(self):
        self.assertTrue(is_valid_url(self.new_comment_details_user_1['url']))

    def test_is_valid_url_invalid(self):
        letters = string.ascii_lowercase
        self.new_comment_details_user_1['url'] = ''.join(random.choice(letters) for i in range(random.randint(1, 10)))
        self.assertFalse(is_valid_url(self.new_comment_details_user_1['url']))

    def test_convert_date_format_valid(self):
        err = ''
        self.assertTrue(err == convert_date_format(self.new_comment_details_user_1, 'verdict_date'))

    def test_convert_date_format_invalid(self):
        self.new_comment_details_user_1['verdict_date'] = datetime.datetime.strptime(str(self.comment_2.verdict_date), '%Y-%m-%d').strftime('%m/%d/%y')
        err = ''
        self.assertFalse(err == convert_date_format(self.new_comment_details_user_1, 'verdict_date'))

    def test_is_valid_verdict_date_valid(self):
        self.assertTrue(is_valid_verdict_date(datetime.datetime.strftime(datetime.datetime.now() - datetime.timedelta(days=1),'%d/%m/%Y')))

    def test_is_valid_verdict_date_invalid_format(self):
        self.assertFalse(is_valid_verdict_date(datetime.datetime.strftime(datetime.datetime.now() - datetime.timedelta(days=1),'%d.%m.%Y')))

    def test_is_valid_verdict_date_invalid_datetime(self):
        self.assertFalse(is_valid_verdict_date(datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=7),'%d/%m/%Y')))

    def test_get_system_label_to_comment(self):
        self.assertTrue('True' == get_system_label_to_comment("True", self.user_1.id))
        self.assertTrue('False' == get_system_label_to_comment("False", self.user_1.id))
        self.assertTrue('Unknown' == get_system_label_to_comment("Unknown", self.user_1.id))
        from users.views import add_all_scrapers
        from users.models import Scrapers
        admin = User.objects.create_superuser(username='admin',
                                              email='admin@gmail.com',
                                              password='admin')
        self.get_request.user = admin
        add_all_scrapers(self.get_request)
        for scraper in Scrapers.objects.all():
            for true_label in scraper.true_labels.split(','):
                self.assertTrue('True' == get_system_label_to_comment(true_label, scraper.scraper.id))
            for false_label in scraper.false_labels.split(','):
                self.assertTrue('False' == get_system_label_to_comment(false_label, scraper.scraper.id))
            self.assertTrue('Unknown' == get_system_label_to_comment('Unknown', scraper.scraper.id))

    def test_edit_comment(self):
        self.update_comment_details['comment_id'] = str(self.comment_1.id)
        self.update_comment_details['user_id'] = str(self.comment_1.user_id)
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.update_comment_details)
        self.post_request.POST = query_dict
        self.post_request.user = self.user_1
        self.assertTrue(edit_comment(self.post_request).status_code == 200)
        new_comment = Comment.objects.filter(id=self.comment_1.id).first()
        self.assertTrue(new_comment.title == self.update_comment_details['comment_title'])
        self.assertTrue(new_comment.description == self.update_comment_details['comment_description'])
        self.assertTrue(new_comment.url == self.update_comment_details['comment_reference'])
        self.assertTrue(new_comment.verdict_date == self.comment_3.verdict_date)
        self.assertTrue(new_comment.system_label == self.update_comment_details['comment_label'])

    def test_edit_comment_by_user_not_his_comment(self):
        self.update_comment_details['comment_id'] = str(self.comment_1.id)
        self.update_comment_details['user_id'] = str(self.user_2.id)
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.update_comment_details)
        self.post_request.POST = query_dict
        self.post_request.user = self.user_2
        response = edit_comment(self.post_request)
        self.assertTrue(response.status_code == self.error_code)
        comment = Comment.objects.filter(id=self.comment_1.id).first()
        self.assertTrue(comment.title == self.comment_1.title)
        self.assertTrue(comment.description == self.comment_1.description)
        self.assertTrue(comment.url == self.comment_1.url)
        self.assertTrue(comment.verdict_date == self.comment_1.verdict_date)
        self.assertTrue(comment.label == self.comment_1.label)

    def test_edit_comment_by_invalid_user_id(self):
        user = User(id=self.num_of_saved_users + random.randint(1, 10), email='user@gmail.com')
        self.update_comment_details['user_id'] = user.id
        self.update_comment_details['comment_id'] = str(self.comment_1.id)
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.update_comment_details)
        self.post_request.POST = query_dict
        self.post_request.user = user
        response = edit_comment(self.post_request)
        self.assertTrue(response.status_code == self.error_code)
        comment = Comment.objects.filter(id=self.comment_1.id).first()
        self.assertTrue(comment.title == self.comment_1.title)
        self.assertTrue(comment.description == self.comment_1.description)
        self.assertTrue(comment.url == self.comment_1.url)
        self.assertTrue(comment.verdict_date == self.comment_1.verdict_date)
        self.assertTrue(comment.label == self.comment_1.label)

    def test_edit_comment_by_invalid_comment_id(self):
        self.update_comment_details['comment_id'] = self.num_of_saved_comments + random.randint(1, 10)
        self.update_comment_details['user_id'] = str(self.comment_1.user_id)
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.update_comment_details)
        self.post_request.POST = query_dict
        self.post_request.user = self.user_1
        response = edit_comment(self.post_request)
        self.assertTrue(response.status_code == self.error_code)
        comment = Comment.objects.filter(id=self.comment_1.id).first()
        self.assertTrue(comment.title == self.comment_1.title)
        self.assertTrue(comment.description == self.comment_1.description)
        self.assertTrue(comment.url == self.comment_1.url)
        self.assertTrue(comment.verdict_date == self.comment_1.verdict_date)
        self.assertTrue(comment.label == self.comment_1.label)

    def test_edit_comment_missing_args(self):
        for i in range(10):
            dict_copy = self.update_comment_details.copy()
            args_to_remove = []
            for j in range(0, (random.randint(1, len(self.update_comment_details.keys()) - 1))):
                args_to_remove.append(list(self.update_comment_details.keys())[j])
            for j in range(len(args_to_remove)):
                del self.update_comment_details[args_to_remove[j]]
            query_dict = QueryDict('', mutable=True)
            query_dict.update(self.update_comment_details)
            self.post_request.POST = query_dict
            self.post_request.user = self.user_1
            response = edit_comment(self.post_request)
            self.assertTrue(response.status_code == self.error_code)
            self.update_comment_details = dict_copy.copy()

    def test_edit_comment_invalid_request(self):
        self.update_comment_details['comment_id'] = str(self.comment_1.id)
        self.update_comment_details['user_id'] = str(self.comment_1.user_id)
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.update_comment_details)
        self.get_request.POST = query_dict
        self.get_request.user = self.user_1
        self.assertRaises(PermissionDenied, edit_comment, self.get_request)

    def test_check_comment_new_fields(self):
        self.update_comment_details['comment_id'] = str(self.comment_1.id)
        self.update_comment_details['user_id'] = str(self.user_1.id)
        self.update_comment_details['is_superuser'] = False
        self.assertTrue(check_comment_new_fields(self.update_comment_details)[0])
        self.update_comment_details['is_superuser'] = True
        self.assertTrue(check_comment_new_fields(self.update_comment_details)[0])

    def test_check_comment_new_fields_missing_user_id(self):
        self.update_comment_details['comment_id'] = str(self.comment_1.id)
        self.update_comment_details['is_superuser'] = False
        self.assertFalse(check_comment_new_fields(self.update_comment_details)[0])
        self.update_comment_details['is_superuser'] = True
        self.assertFalse(check_comment_new_fields(self.update_comment_details)[0])

    def test_check_comment_new_fields_invalid_user_id(self):
        self.update_comment_details['comment_id'] = str(self.comment_1.id)
        self.update_comment_details['user_id'] = str(self.num_of_saved_users + random.randint(1, 10))
        self.update_comment_details['is_superuser'] = False
        self.assertFalse(check_comment_new_fields(self.update_comment_details)[0])
        self.update_comment_details['is_superuser'] = True
        self.assertFalse(check_comment_new_fields(self.update_comment_details)[0])

    def test_check_comment_new_fields_missing_user_type(self):
        self.update_comment_details['comment_id'] = str(self.comment_1.id)
        self.update_comment_details['user_id'] = str(self.user_1.id)
        self.assertFalse(check_comment_new_fields(self.update_comment_details)[0])

    def test_check_comment_new_fields_missing_comment_id(self):
        self.update_comment_details['user_id'] = str(self.user_1.id)
        self.update_comment_details['is_superuser'] = False
        self.assertFalse(check_comment_new_fields(self.update_comment_details)[0])
        self.update_comment_details['is_superuser'] = True
        self.assertFalse(check_comment_new_fields(self.update_comment_details)[0])

    def test_check_comment_new_fields_invalid_comment_id(self):
        self.update_comment_details['comment_id'] = str(self.num_of_saved_comments + random.randint(1, 10))
        self.update_comment_details['user_id'] = self.user_1.id
        self.update_comment_details['is_superuser'] = False
        self.assertFalse(check_comment_new_fields(self.update_comment_details)[0])
        self.update_comment_details['is_superuser'] = True
        self.assertFalse(check_comment_new_fields(self.update_comment_details)[0])

    def test_check_comment_new_fields_invalid_format_for_tags(self):
        invalid_input = 'tag1,'
        for i in range(random.randint(1, 10)):
            invalid_input += ','
        invalid_input += ',tag2'
        self.update_comment_details['comment_id'] = str(self.comment_1.id)
        self.update_comment_details['user_id'] = self.user_1.id
        self.update_comment_details['comment_tags'] = invalid_input
        self.update_comment_details['is_superuser'] = False
        self.assertFalse(check_comment_new_fields(self.update_comment_details)[0])
        self.update_comment_details['is_superuser'] = True
        self.assertFalse(check_comment_new_fields(self.update_comment_details)[0])

    def test_check_comment_new_fields_missing_title(self):
        self.update_comment_details['comment_id'] = str(self.comment_1.id)
        self.update_comment_details['user_id'] = str(self.user_1.id)
        self.update_comment_details['is_superuser'] = False
        del self.update_comment_details['comment_title']
        self.assertFalse(check_comment_new_fields(self.update_comment_details)[0])
        self.update_comment_details['is_superuser'] = True
        self.assertFalse(check_comment_new_fields(self.update_comment_details)[0])

    def test_check_comment_new_fields_missing_description(self):
        self.update_comment_details['comment_id'] = str(self.comment_1.id)
        self.update_comment_details['user_id'] = str(self.user_1.id)
        self.update_comment_details['is_superuser'] = False
        del self.update_comment_details['comment_description']
        self.assertFalse(check_comment_new_fields(self.update_comment_details)[0])
        self.update_comment_details['is_superuser'] = True
        self.assertFalse(check_comment_new_fields(self.update_comment_details)[0])

    def test_check_comment_new_fields_missing_verdict_date(self):
        self.update_comment_details['comment_id'] = str(self.comment_1.id)
        self.update_comment_details['user_id'] = str(self.user_1.id)
        self.update_comment_details['is_superuser'] = False
        del self.update_comment_details['comment_verdict_date']
        self.assertFalse(check_comment_new_fields(self.update_comment_details)[0])
        self.update_comment_details['is_superuser'] = True
        self.assertFalse(check_comment_new_fields(self.update_comment_details)[0])

    def test_check_comment_new_fields_missing_reference(self):
        self.update_comment_details['comment_id'] = str(self.comment_1.id)
        self.update_comment_details['user_id'] = str(self.user_1.id)
        self.update_comment_details['is_superuser'] = False
        del self.update_comment_details['comment_reference']
        self.assertFalse(check_comment_new_fields(self.update_comment_details)[0])
        self.update_comment_details['is_superuser'] = True
        self.assertFalse(check_comment_new_fields(self.update_comment_details)[0])

    def test_check_comment_new_fields_invalid_reference(self):
        letters = string.ascii_lowercase
        self.update_comment_details['comment_id'] = str(self.comment_1.id)
        self.update_comment_details['user_id'] = str(self.user_1.id)
        self.update_comment_details['is_superuser'] = False
        self.update_comment_details['comment_reference'] = ''.join(random.choice(letters) for i in range(random.randint(1, 10)))
        self.assertFalse(check_comment_new_fields(self.update_comment_details)[0])
        self.update_comment_details['is_superuser'] = True
        self.assertFalse(check_comment_new_fields(self.update_comment_details)[0])

    def test_check_comment_new_fields_missing_label(self):
        self.update_comment_details['comment_id'] = str(self.comment_1.id)
        self.update_comment_details['user_id'] = str(self.user_1.id)
        self.update_comment_details['is_superuser'] = False
        del self.update_comment_details['comment_label']
        self.assertFalse(check_comment_new_fields(self.update_comment_details)[0])
        self.update_comment_details['is_superuser'] = True
        self.assertFalse(check_comment_new_fields(self.update_comment_details)[0])

    def test_check_comment_new_fields_comment_not_belong_to_user(self):
        self.update_comment_details['comment_id'] = str(self.comment_2.id)
        self.update_comment_details['user_id'] = str(self.user_1.id)
        self.update_comment_details['is_superuser'] = False
        self.assertFalse(check_comment_new_fields(self.update_comment_details)[0])
        self.update_comment_details['is_superuser'] = True
        self.assertTrue(check_comment_new_fields(self.update_comment_details)[0])

    def test_check_comment_new_fields_edit_after_ten_minutes(self):
        Comment.objects.filter(id=self.comment_1.id).update(timestamp=datetime.datetime.now() -
                                                            datetime.timedelta(minutes=11))
        self.update_comment_details['comment_id'] = str(self.comment_1.id)
        self.update_comment_details['user_id'] = str(self.user_1.id)
        self.update_comment_details['is_superuser'] = False
        self.assertFalse(check_comment_new_fields(self.update_comment_details)[0])
        self.update_comment_details['is_superuser'] = True
        self.assertTrue(check_comment_new_fields(self.update_comment_details)[0])

    def test_check_comment_new_fields_comment_invalid_date_format(self):
        self.update_comment_details['comment_id'] = str(self.comment_1.id)
        self.update_comment_details['user_id'] = str(self.user_1.id)
        self.update_comment_details['is_superuser'] = False
        self.update_comment_details['comment_verdict_date'] = datetime.datetime.strptime(str(self.comment_1.verdict_date), '%Y-%m-%d').strftime('%m/%d/%y')
        self.assertFalse(check_comment_new_fields(self.update_comment_details)[0])
        self.update_comment_details['is_superuser'] = True
        self.assertFalse(check_comment_new_fields(self.update_comment_details)[0])

    def test_check_comment_new_fields_invalid_input_for_title(self):
        self.update_comment_details['comment_id'] = str(self.comment_1.id)
        self.update_comment_details['user_id'] = str(self.user_1.id)
        self.update_comment_details['comment_title'] = 'Խոսքի խառնաշփոթի խառնաշփոթություն'
        self.update_comment_details['is_superuser'] = False
        self.assertFalse(check_comment_new_fields(self.update_comment_details)[0])
        self.update_comment_details['is_superuser'] = True
        self.assertFalse(check_comment_new_fields(self.update_comment_details)[0])

    def test_check_comment_new_fields_invalid_input_for_description(self):
        self.update_comment_details['comment_id'] = str(self.comment_1.id)
        self.update_comment_details['user_id'] = str(self.user_1.id)
        self.update_comment_details['comment_description'] = 'Μια κουβέντα από ανοησίες λέξεων'
        self.update_comment_details['is_superuser'] = False
        self.assertFalse(check_comment_new_fields(self.update_comment_details)[0])
        self.update_comment_details['is_superuser'] = True
        self.assertFalse(check_comment_new_fields(self.update_comment_details)[0])

    def test_delete_comment_by_user(self):
        comment_to_delete = {'comment_id': self.comment_1.id}
        self.post_request.POST = comment_to_delete
        self.post_request.user = self.user_1
        len_comments = len(Comment.objects.all())
        response = delete_comment(self.post_request)
        self.assertTrue(len(Comment.objects.all()) == len_comments - 1)
        self.assertTrue(response.status_code == 200)

    def test_delete_comment_by_user_not_his_comment(self):
        comment_to_delete = {'comment_id': self.comment_2.id}
        self.post_request.POST = comment_to_delete
        self.post_request.user = self.user_1
        len_comments = len(Comment.objects.all())
        response = delete_comment(self.post_request)
        self.assertTrue(response.status_code == self.error_code)
        self.assertTrue(len(Comment.objects.all()) == len_comments)

    def test_delete_comment_by_invalid_user(self):
        user = User(id=self.num_of_saved_users + random.randint(1, 10), email='user@gmail.com')
        comment_to_delete = {'comment_id': self.comment_1.id}
        self.post_request.POST = comment_to_delete
        self.post_request.user = user
        len_comments = len(Comment.objects.all())
        response = delete_comment(self.post_request)
        self.assertTrue(response.status_code == self.error_code)
        self.assertTrue(len(Comment.objects.all()) == len_comments)

    def test_delete_comment_by_not_authenticated_user(self):
        from django.contrib.auth.models import AnonymousUser
        comment_to_delete = {'comment_id': self.comment_1.id}
        self.post_request.POST = comment_to_delete
        self.post_request.user = AnonymousUser()
        len_comments = len(Comment.objects.all())
        self.assertRaises(PermissionDenied, delete_comment, self.post_request)
        self.assertTrue(len(Comment.objects.all()) == len_comments)

    def test_delete_comment_by_invalid_comment_id(self):
        comment_to_delete = {'comment_id': self.num_of_saved_comments + random.randint(1, 10)}
        self.post_request.POST = comment_to_delete
        self.post_request.user = self.user_1
        len_comments = len(Comment.objects.all())
        response = delete_comment(self.post_request)
        self.assertTrue(response.status_code == self.error_code)
        self.assertTrue(len(Comment.objects.all()) == len_comments)

    def test_delete_comment_invalid_request(self):
        comment_to_delete = {'comment_id': self.comment_1.id}
        self.get_request.POST = comment_to_delete
        self.get_request.user = self.user_1
        len_comments = len(Comment.objects.all())
        self.assertRaises(PermissionDenied, delete_comment, self.get_request)
        self.assertTrue(len(Comment.objects.all()) == len_comments)

    def test_check_if_delete_comment_is_valid(self):
        comment_to_delete = {'comment_id': self.comment_1.id}
        self.post_request.POST = comment_to_delete
        self.post_request.user = self.user_1
        self.assertTrue(check_if_delete_comment_is_valid(self.post_request)[0])

    def test_check_if_delete_comment_is_valid_missing_comment_id(self):
        self.post_request.user = self.user_1
        self.assertFalse(check_if_delete_comment_is_valid(self.post_request)[0])

    def test_check_if_delete_comment_is_valid_invalid_comment_id(self):
        comment_to_delete = {'comment_id': self.num_of_saved_comments + random.randint(1, 10)}
        self.post_request.POST = comment_to_delete
        self.post_request.user = self.user_1
        self.assertFalse(check_if_delete_comment_is_valid(self.post_request)[0])

    def test_check_if_delete_comment_is_valid_invalid_user_id(self):
        user = User(id=self.num_of_saved_users + random.randint(1, 10), email='user@gmail.com')
        comment_to_delete = {'comment_id':  self.comment_1.id}
        self.post_request.POST = comment_to_delete
        self.post_request.user = user
        self.assertFalse(check_if_delete_comment_is_valid(self.post_request)[0])

    def test_check_if_delete_comment_is_valid_another_user(self):
        comment_to_delete = {'comment_id':  self.comment_1.id}
        self.post_request.POST = comment_to_delete
        self.post_request.user = self.user_2
        self.assertFalse(check_if_delete_comment_is_valid(self.post_request)[0])

    def test_up_vote(self):
        comment_to_vote = {'comment_id': self.comment_2.id}
        query_dict = QueryDict('', mutable=True)
        query_dict.update(comment_to_vote)
        self.post_request.POST = query_dict
        self.post_request.user = self.user_1
        response = up_vote(self.post_request)
        self.assertTrue(response.status_code == self.error_code)
        Comment.objects.filter(id=self.comment_2.id).update(timestamp=datetime.datetime.now() -
                                                                      datetime.timedelta(minutes=11))
        response = up_vote(self.post_request)
        self.assertTrue(self.comment_2.up_votes.count() == 1)
        self.assertTrue(self.comment_2.down_votes.count() == 0)
        self.assertTrue(response.status_code == 200)

    def test_up_vote_twice(self):
        comment_to_vote = {'comment_id': self.comment_2.id}
        query_dict = QueryDict('', mutable=True)
        query_dict.update(comment_to_vote)
        self.post_request.POST = query_dict
        self.post_request.user = self.user_1
        response = up_vote(self.post_request)
        self.assertTrue(response.status_code == self.error_code)
        Comment.objects.filter(id=self.comment_2.id).update(timestamp=datetime.datetime.now() -
                                                                      datetime.timedelta(minutes=11))
        up_vote(self.post_request)
        response = up_vote(self.post_request)
        self.assertTrue(self.comment_2.up_votes.count() == 0)
        self.assertTrue(self.comment_2.down_votes.count() == 0)
        self.assertTrue(response.status_code == 200)

    def test_up_vote_after_down_vote(self):
        comment_to_vote = {'comment_id': self.comment_2.id}
        query_dict = QueryDict('', mutable=True)
        query_dict.update(comment_to_vote)
        self.post_request.POST = query_dict
        self.post_request.user = self.user_1
        response = down_vote(self.post_request)
        self.assertTrue(response.status_code == self.error_code)
        response = up_vote(self.post_request)
        self.assertTrue(response.status_code == self.error_code)
        Comment.objects.filter(id=self.comment_2.id).update(timestamp=datetime.datetime.now() -
                                                                      datetime.timedelta(minutes=11))
        down_vote(self.post_request)
        response = up_vote(self.post_request)
        self.assertTrue(self.comment_2.up_votes.count() == 1)
        self.assertTrue(self.comment_2.down_votes.count() == 0)
        self.assertTrue(response.status_code == 200)

    def test_up_vote_user_not_authenticated(self):
        from django.contrib.auth.models import AnonymousUser
        comment_to_vote = {'comment_id': self.comment_2.id}
        query_dict = QueryDict('', mutable=True)
        query_dict.update(comment_to_vote)
        self.post_request.POST = query_dict
        self.post_request.user = AnonymousUser()
        response = up_vote(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_up_vote_invalid_user(self):
        user = User(id=self.num_of_saved_users + random.randint(1, 10), email="user@gmail.com")
        comment_to_vote = {'comment_id': self.comment_1.id}
        query_dict = QueryDict('', mutable=True)
        query_dict.update(comment_to_vote)
        self.post_request.POST = query_dict
        self.post_request.user = user
        response = up_vote(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_up_vote_invalid_request(self):
        comment_to_vote = {'comment_id': self.comment_2.id}
        query_dict = QueryDict('', mutable=True)
        query_dict.update(comment_to_vote)
        self.get_request.POST = query_dict
        self.get_request.user = self.user_1
        response = up_vote(self.get_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_down_vote(self):
        comment_to_vote = {'comment_id': self.comment_1.id}
        query_dict = QueryDict('', mutable=True)
        query_dict.update(comment_to_vote)
        self.post_request.POST = query_dict
        self.post_request.user = self.user_2
        response = down_vote(self.post_request)
        self.assertTrue(response.status_code == self.error_code)
        Comment.objects.filter(id=self.comment_1.id).update(timestamp=datetime.datetime.now() -
                                                                      datetime.timedelta(minutes=11))
        response = down_vote(self.post_request)
        self.assertTrue(self.comment_1.down_votes.count() == 1)
        self.assertTrue(self.comment_1.up_votes.count() == 0)
        self.assertTrue(response.status_code == 200)

    def test_down_vote_twice(self):
        comment_to_vote = {'comment_id': self.comment_1.id}
        query_dict = QueryDict('', mutable=True)
        query_dict.update(comment_to_vote)
        self.post_request.POST = query_dict
        self.post_request.user = self.user_2
        response = down_vote(self.post_request)
        self.assertTrue(response.status_code == self.error_code)
        Comment.objects.filter(id=self.comment_1.id).update(timestamp=datetime.datetime.now() -
                                                                      datetime.timedelta(minutes=11))
        down_vote(self.post_request)
        response = down_vote(self.post_request)
        self.assertTrue(self.comment_2.down_votes.count() == 0)
        self.assertTrue(self.comment_2.down_votes.count() == 0)
        self.assertTrue(response.status_code == 200)

    def test_down_vote_after_up_vote(self):
        comment_to_vote = {'comment_id': self.comment_1.id}
        query_dict = QueryDict('', mutable=True)
        query_dict.update(comment_to_vote)
        self.post_request.POST = query_dict
        self.post_request.user = self.user_2
        response = up_vote(self.post_request)
        self.assertTrue(response.status_code == self.error_code)
        response = down_vote(self.post_request)
        self.assertTrue(response.status_code == self.error_code)
        Comment.objects.filter(id=self.comment_1.id).update(timestamp=datetime.datetime.now() -
                                                                      datetime.timedelta(minutes=11))
        up_vote(self.post_request)
        response = down_vote(self.post_request)
        self.assertTrue(self.comment_1.up_votes.count() == 0)
        self.assertTrue(self.comment_1.down_votes.count() == 1)
        self.assertTrue(response.status_code == 200)

    def test_down_vote_user_not_authenticated(self):
        from django.contrib.auth.models import AnonymousUser
        comment_to_vote = {'comment_id': self.comment_1.id}
        query_dict = QueryDict('', mutable=True)
        query_dict.update(comment_to_vote)
        self.post_request.POST = query_dict
        self.post_request.user = AnonymousUser()
        response = down_vote(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_down_vote_invalid_user(self):
        user = User(id=self.num_of_saved_users + random.randint(1, 10), email="user@gmail.com")
        comment_to_vote = {'comment_id': self.comment_1.id}
        query_dict = QueryDict('', mutable=True)
        query_dict.update(comment_to_vote)
        self.post_request.POST = query_dict
        self.post_request.user = user
        response = down_vote(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_down_vote_invalid_request(self):
        comment_to_vote = {'comment_id': self.comment_1.id}
        query_dict = QueryDict('', mutable=True)
        query_dict.update(comment_to_vote)
        self.get_request.POST = query_dict
        self.get_request.user = self.user_1
        response = up_vote(self.get_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_check_if_vote_is_valid(self):
        comment_to_vote = {'comment_id': self.comment_1.id,
                           'user_id': self.user_1.id}
        self.assertFalse(check_if_vote_is_valid(comment_to_vote)[0])
        Comment.objects.filter(id=self.comment_1.id).update(timestamp=datetime.datetime.now() -
                                                                      datetime.timedelta(minutes=11))
        self.assertTrue(check_if_vote_is_valid(comment_to_vote)[0])

    def test_check_if_vote_is_valid_missing_user_id(self):
        comment_to_vote = {'comment_id': self.comment_1.id}
        self.assertFalse(check_if_vote_is_valid(comment_to_vote)[0])

    def test_check_if_vote_is_valid_invalid_user_id(self):
        comment_to_vote = {'comment_id': self.comment_1.id,
                           'user_id': self.num_of_saved_users + random.randint(1, 10)}
        self.assertFalse(check_if_vote_is_valid(comment_to_vote)[0])

    def test_check_if_vote_is_valid_missing_comment_id(self):
        comment_to_vote = {'user_id': self.user_1.id}
        self.assertFalse(check_if_vote_is_valid(comment_to_vote)[0])

    def test_check_if_vote_is_valid_invalid_comment_id(self):
        comment_to_vote = {'comment_id': self.num_of_saved_comments + random.randint(1, 10),
                           'user_id': self.user_1.id}
        self.assertFalse(check_if_vote_is_valid(comment_to_vote)[0])

    def test_export_to_csv(self):
        admin = User.objects.create_superuser('admin', 'admin@gmail.com', 'admin')
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.csv_fields)
        self.post_request.POST = query_dict
        self.post_request.user = admin
        res = export_to_csv(self.post_request)
        self.assertTrue(res.status_code == 200)
        expected_info = 'Claim Id,Title,Description,Url,Category,Verdict Date,Tags,Label,System Label,Authenticity Grade\r\n' +\
                        str(self.comment_5.claim.id) + ',claim3,description5,' + self.comment_5.url + ',category3,' + str(self.comment_5.verdict_date) + ',,label5,,0\r\n' +\
                        str(self.comment_6.claim.id) + ',claim4,description6,' + self.comment_6.url + ',category4,' + str(self.comment_6.verdict_date) + ',,label6,,0\r\n'
        self.assertEqual(res.content.decode('utf-8'), expected_info)
        Comment.objects.filter(id=self.comment_5.id).update(tags='tag1', system_label='True')
        Comment.objects.filter(id=self.comment_6.id).update(tags='tag6, tag7', system_label='False')
        res = export_to_csv(self.post_request)
        self.assertTrue(res.status_code == 200)
        expected_info = 'Claim Id,Title,Description,Url,Category,Verdict Date,Tags,Label,System Label,Authenticity Grade\r\n'  + \
                        str(self.comment_5.claim.id) + ',claim3,description5,' + self.comment_5.url + ',category3,' + str(self.comment_5.verdict_date) + ',tag1,label5,True,0\r\n' + \
                        str(self.comment_6.claim.id) + ',claim4,description6,' + self.comment_6.url + ',category4,' + str(self.comment_6.verdict_date) + ',"tag6, tag7",label6,False,0\r\n'
        self.assertEqual(res.content.decode('utf-8'), expected_info)

    def test_export_to_csv_invalid_arg_for_scraper(self):
        new_scrapers_ids = self.csv_fields.getlist('scrapers_ids[]')
        new_scrapers_ids.append(str(self.num_of_saved_users + random.randint(1, 10)))
        self.csv_fields.setlist('scrapers_ids[]', new_scrapers_ids)
        admin = User.objects.create_superuser('admin', 'admin@gmail.com', 'admin')
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.csv_fields)
        self.post_request.POST = query_dict
        self.post_request.user = admin
        response = export_to_csv(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_export_to_csv_invalid_arg_for_field(self):
        import string
        fields_to_export = self.csv_fields.getlist('fields_to_export[]')
        fields_to_export.append(''.join(random.choices(string.ascii_uppercase + string.digits, k=random.randint(1, 20))))
        self.csv_fields.setlist('fields_to_export[]', fields_to_export)
        admin = User.objects.create_superuser('admin', 'admin@gmail.com', 'admin')
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.csv_fields)
        self.post_request.POST = query_dict
        self.post_request.user = admin
        response = export_to_csv(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_export_to_csv_missing_args(self):
        admin = User.objects.create_superuser('admin', 'admin@gmail.com', 'admin')
        for i in range(10):
            dict_copy = self.csv_fields.copy()
            args_to_remove = []
            for j in range(0, (random.randint(1, len(self.csv_fields.keys()) - 1))):
                args_to_remove.append(list(self.csv_fields.keys())[j])
            for j in range(len(args_to_remove)):
                del self.csv_fields[args_to_remove[j]]
            query_dict = QueryDict('', mutable=True)
            query_dict.update(self.csv_fields)
            self.post_request.POST = query_dict
            self.post_request.user = admin
            response = export_to_csv(self.post_request)
            self.assertTrue(response.status_code == self.error_code)
            self.csv_fields = dict_copy.copy()

    def test_export_to_csv_empty(self):
        admin = User.objects.create_superuser('admin', 'admin@gmail.com', 'admin')
        self.post_request.user = admin
        Comment.objects.all().delete()
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.csv_fields)
        self.post_request.POST = query_dict
        res = export_to_csv(self.post_request)
        self.assertTrue(res.status_code == 200)
        self.assertTrue(res.content.decode('utf-8') ==
                        'Claim Id,Title,Description,Url,Category,Verdict Date,Tags,Label,System Label,Authenticity Grade\r\n')

    def test_export_to_csv_not_authenticated_user(self):
        from django.contrib.auth.models import AnonymousUser
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.csv_fields)
        self.post_request.POST = query_dict
        self.post_request.user = AnonymousUser()
        self.assertRaises(PermissionDenied, export_to_csv, self.post_request)

    def test_export_to_csv_not_admin_user(self):
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.csv_fields)
        self.post_request.POST = query_dict
        self.post_request.user = self.user_1
        self.assertRaises(PermissionDenied, export_to_csv, self.post_request)

    def test_check_if_csv_fields_are_valid(self):
        self.assertTrue(check_if_csv_fields_are_valid(self.csv_fields)[0])

    def test_check_if_csv_fields_are_valid_with_regular_users(self):
        self.csv_fields['regular_users'] = 'True'
        self.assertTrue(check_if_csv_fields_are_valid(self.csv_fields)[0])

    def test_check_if_csv_fields_are_valid_missing_fields_to_export(self):
        del self.csv_fields['fields_to_export[]']
        self.assertFalse(check_if_csv_fields_are_valid(self.csv_fields)[0])

    def test_check_if_csv_fields_are_valid_missing_verdict_date_start(self):
        del self.csv_fields['verdict_date_start']
        self.assertFalse(check_if_csv_fields_are_valid(self.csv_fields)[0])

    def test_check_if_csv_fields_are_valid_missing_verdict_date_end(self):
        del self.csv_fields['verdict_date_end']
        self.assertFalse(check_if_csv_fields_are_valid(self.csv_fields)[0])

    def test_check_if_csv_fields_are_valid_invalid_format_verdict_date_start(self):
        self.csv_fields['verdict_date_start'] = datetime.datetime.strftime(datetime.datetime.now() - datetime.timedelta(days=1),'%d.%m.%Y')
        self.assertFalse(check_if_csv_fields_are_valid(self.csv_fields)[0])
        self.csv_fields['verdict_date_start'] = datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=7),'%d/%m/%Y')
        self.assertFalse(check_if_csv_fields_are_valid(self.csv_fields)[0])
        self.csv_fields['verdict_date_start'] = datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=7),'%d/%m/%y')
        self.assertFalse(check_if_csv_fields_are_valid(self.csv_fields)[0])
        self.csv_fields['verdict_date_start'] = datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=7),'%Y/%m/%d')
        self.assertFalse(check_if_csv_fields_are_valid(self.csv_fields)[0])
        year = str(random.randint(2000, 2018))
        month = str(random.randint(1, 12))
        day = str(random.randint(1, 28))
        self.csv_fields['verdict_date_start'] = year + '--' + month + '-' + day
        self.assertFalse(check_if_csv_fields_are_valid(self.csv_fields)[0])
        self.csv_fields['verdict_date_start'] = year + '-' + month + '--' + day
        self.assertFalse(check_if_csv_fields_are_valid(self.csv_fields)[0])

    def test_check_if_csv_fields_are_valid_invalid_format_verdict_date_end(self):
        self.csv_fields['verdict_date_end'] = datetime.datetime.strftime(datetime.datetime.now() - datetime.timedelta(days=1),'%d.%m.%Y')
        self.assertFalse(check_if_csv_fields_are_valid(self.csv_fields)[0])
        self.csv_fields['verdict_date_end'] = datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=7),'%d/%m/%Y')
        self.assertFalse(check_if_csv_fields_are_valid(self.csv_fields)[0])
        self.csv_fields['verdict_date_end'] = datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=7),'%d/%m/%y')
        self.assertFalse(check_if_csv_fields_are_valid(self.csv_fields)[0])
        self.csv_fields['verdict_date_end'] = datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=7),'%Y/%m/%d')
        self.assertFalse(check_if_csv_fields_are_valid(self.csv_fields)[0])
        year = str(random.randint(2000, 2018))
        month = str(random.randint(1, 12))
        day = str(random.randint(1, 28))
        self.csv_fields['verdict_date_end'] = year + '--' + month + '-' + day
        self.assertFalse(check_if_csv_fields_are_valid(self.csv_fields)[0])
        self.csv_fields['verdict_date_end'] = year + '-' + month + '--' + day
        self.assertFalse(check_if_csv_fields_are_valid(self.csv_fields)[0])

    def test_check_if_fields_and_scrapers_lists_valid(self):
        self.assertTrue(check_if_fields_and_scrapers_lists_valid(self.csv_fields.getlist('fields_to_export[]'),
                                                                 self.csv_fields.getlist('scrapers_ids[]'))[0])

    def test_check_if_fields_and_scrapers_lists_valid_invalid_field(self):
        import string
        new_fields = self.csv_fields.getlist('fields_to_export[]')
        new_fields.append(''.join(random.choices(string.ascii_uppercase + string.digits, k=random.randint(1, 20))))
        self.csv_fields.setlist('fields_to_export[]', new_fields)
        self.assertFalse(check_if_fields_and_scrapers_lists_valid(self.csv_fields.getlist('fields_to_export[]'),
                                                                  self.csv_fields.getlist('scrapers_ids[]'))[0])

    def test_check_if_fields_and_scrapers_lists_valid_invalid_fields(self):
        import string
        new_fields = self.csv_fields.getlist('fields_to_export[]')
        for i in range(random.randint(1, 10)):
            new_fields.append(''.join(random.choices(string.ascii_uppercase + string.digits, k=random.randint(1, 20))))
        self.csv_fields.setlist('fields_to_export[]', new_fields)
        self.assertFalse(check_if_fields_and_scrapers_lists_valid(self.csv_fields.getlist('fields_to_export[]'),
                                                                  self.csv_fields.getlist('scrapers_ids[]'))[0])

    def test_check_if_fields_and_scrapers_lists_valid_invalid_scraper_id(self):
        new_scrapers_ids = [int(scraper_id) for scraper_id in self.csv_fields.getlist('scrapers_ids[]')]
        new_scrapers_ids.append(self.num_of_saved_users + random.randint(1, 10))
        self.csv_fields.setlist('scrapers_ids[]', new_scrapers_ids)
        self.assertFalse(check_if_fields_and_scrapers_lists_valid(self.csv_fields.getlist('fields_to_export[]'),
                                                                  self.csv_fields.getlist('scrapers_ids[]'))[0])

    def test_check_if_fields_and_scrapers_lists_valid_invalid_scrapers_ids(self):
        new_scrapers_ids = [int(scraper_id) for scraper_id in self.csv_fields.getlist('scrapers_ids[]')]
        for i in range(random.randint(1, 10)):
            new_scrapers_ids.append(self.num_of_saved_users + (i + 1))
        self.csv_fields.setlist('scrapers_ids[]', new_scrapers_ids)
        self.assertFalse(check_if_fields_and_scrapers_lists_valid(self.csv_fields.getlist('fields_to_export[]'),
                                                                  self.csv_fields.getlist('scrapers_ids[]'))[0])

    def test_create_df_for_claims_with_regular_users(self):
        df_claims = create_df_for_claims(self.csv_fields.getlist('fields_to_export[]'),
                                         [int(scraper_id) for scraper_id in self.csv_fields.getlist('scrapers_ids[]')],
                                         True,
                                         datetime.datetime.strptime(datetime.datetime.strptime(self.csv_fields.get('verdict_date_start'),
                                                                    '%Y-%m-%d').strftime('%d/%m/%Y'), '%d/%m/%Y').date(),
                                         datetime.datetime.strptime(datetime.datetime.strptime(self.csv_fields.get('verdict_date_end'),
                                                                    '%Y-%m-%d').strftime('%d/%m/%Y'), '%d/%m/%Y').date())
        self.assertTrue(len(df_claims) == self.num_of_saved_comments)
        for index, row in df_claims.iterrows():
            if index == 0:
                self.assertTrue(row['Title'] == self.comment_1.title)
                self.assertTrue(row['Description'] == self.comment_1.description)
                self.assertTrue(row['Url'] == self.comment_1.url)
                self.assertTrue(row['Verdict Date'] == self.comment_1.verdict_date)
                self.assertTrue(row['Url'] == self.comment_1.url)
                self.assertTrue(row['Tags'] == self.comment_1.tags)
                self.assertTrue(row['Label'] == self.comment_1.label)
                self.assertTrue(row['System Label'] == self.comment_1.system_label)
            elif index == 1:
                self.assertTrue(row['Title'] == self.comment_2.title)
                self.assertTrue(row['Description'] == self.comment_2.description)
                self.assertTrue(row['Url'] == self.comment_2.url)
                self.assertTrue(row['Verdict Date'] == self.comment_2.verdict_date)
                self.assertTrue(row['Url'] == self.comment_2.url)
                self.assertTrue(row['Tags'] == self.comment_2.tags)
                self.assertTrue(row['Label'] == self.comment_2.label)
                self.assertTrue(row['System Label'] == self.comment_2.system_label)
            elif index == 2:
                self.assertTrue(row['Title'] == self.comment_5.title)
                self.assertTrue(row['Description'] == self.comment_5.description)
                self.assertTrue(row['Url'] == self.comment_5.url)
                self.assertTrue(row['Verdict Date'] == self.comment_5.verdict_date)
                self.assertTrue(row['Url'] == self.comment_5.url)
                self.assertTrue(row['Tags'] == self.comment_5.tags)
                self.assertTrue(row['Label'] == self.comment_5.label)
                self.assertTrue(row['System Label'] == self.comment_5.system_label)
            elif index == 3:
                self.assertTrue(row['Title'] == self.comment_6.title)
                self.assertTrue(row['Description'] == self.comment_6.description)
                self.assertTrue(row['Url'] == self.comment_6.url)
                self.assertTrue(row['Verdict Date'] == self.comment_6.verdict_date)
                self.assertTrue(row['Url'] == self.comment_6.url)
                self.assertTrue(row['Tags'] == self.comment_6.tags)
                self.assertTrue(row['Label'] == self.comment_6.label)
                self.assertTrue(row['System Label'] == self.comment_6.system_label)

    def test_create_df_for_claims_without_regular_users(self):
        df_claims = create_df_for_claims(self.csv_fields.getlist('fields_to_export[]'),
                                         [int(scraper_id) for scraper_id in self.csv_fields.getlist('scrapers_ids[]')],
                                         False,
                                         datetime.datetime.strptime(datetime.datetime.strptime(self.csv_fields.get('verdict_date_start'),
                                                                    '%Y-%m-%d').strftime('%d/%m/%Y'), '%d/%m/%Y').date(),
                                         datetime.datetime.strptime(datetime.datetime.strptime(self.csv_fields.get('verdict_date_end'),
                                                                    '%Y-%m-%d').strftime('%d/%m/%Y'), '%d/%m/%Y').date())
        self.assertTrue(len(df_claims) == self.num_of_saved_scrapers)
        for index, row in df_claims.iterrows():
            if index == 0:
                self.assertTrue(row['Title'] == self.comment_5.title)
                self.assertTrue(row['Description'] == self.comment_5.description)
                self.assertTrue(row['Url'] == self.comment_5.url)
                self.assertTrue(row['Verdict Date'] == self.comment_5.verdict_date)
                self.assertTrue(row['Url'] == self.comment_5.url)
                self.assertTrue(row['Tags'] == self.comment_5.tags)
                self.assertTrue(row['Label'] == self.comment_5.label)
                self.assertTrue(row['System Label'] == self.comment_5.system_label)
            elif index == 1:
                self.assertTrue(row['Title'] == self.comment_6.title)
                self.assertTrue(row['Description'] == self.comment_6.description)
                self.assertTrue(row['Url'] == self.comment_6.url)
                self.assertTrue(row['Verdict Date'] == self.comment_6.verdict_date)
                self.assertTrue(row['Url'] == self.comment_6.url)
                self.assertTrue(row['Tags'] == self.comment_6.tags)
                self.assertTrue(row['Label'] == self.comment_6.label)
                self.assertTrue(row['System Label'] == self.comment_6.system_label)

    def test_create_df_for_claims_empty(self):
        self.csv_fields['verdict_date_start'] = str(datetime.datetime.now().date())
        df_claims = create_df_for_claims(self.csv_fields.getlist('fields_to_export[]'),
                                         [int(scraper_id) for scraper_id in self.csv_fields.getlist('scrapers_ids[]')],
                                         False,
                                         datetime.datetime.strptime(
                                             datetime.datetime.strptime(self.csv_fields.get('verdict_date_start'),
                                                                        '%Y-%m-%d').strftime('%d/%m/%Y'),
                                             '%d/%m/%Y').date(),
                                         datetime.datetime.strptime(
                                             datetime.datetime.strptime(self.csv_fields.get('verdict_date_end'),
                                                                        '%Y-%m-%d').strftime('%d/%m/%Y'),
                                             '%d/%m/%Y').date())
        self.assertTrue(len(df_claims) == 0)

    def test_get_all_comments_for_user_id(self):
        result = get_all_comments_for_user_id(self.user_1.id)
        self.assertTrue(len(result) == 1)
        self.assertTrue(result.first().claim_id == self.comment_1.claim_id)
        self.assertTrue(result.first().user_id == self.comment_1.user_id)
        self.assertTrue(result.first().title == self.comment_1.title)
        self.assertTrue(result.first().description == self.comment_1.description)
        self.assertTrue(result.first().url == self.comment_1.url)
        self.assertTrue(result.first().verdict_date == self.comment_1.verdict_date)
        self.assertTrue(result.first().label == self.comment_1.label)

        result = get_all_comments_for_user_id(self.user_2.id)
        self.assertTrue(len(result) == 1)
        self.assertTrue(result.first().claim_id == self.comment_2.claim_id)
        self.assertTrue(result.first().user_id == self.comment_2.user_id)
        self.assertTrue(result.first().title == self.comment_2.title)
        self.assertTrue(result.first().description == self.comment_2.description)
        self.assertTrue(result.first().url == self.comment_2.url)
        self.assertTrue(result.first().verdict_date == self.comment_2.verdict_date)
        self.assertTrue(result.first().label == self.comment_2.label)

    def test_get_all_comments_for_user_id_after_existing_user_add_comment(self):
        result = get_all_comments_for_user_id(self.user_1.id)
        len_user_comments = len(result)
        self.assertTrue(len_user_comments == 1)
        self.post_request.POST = self.new_comment_details_user_1
        self.post_request.user = self.user_1
        add_comment(self.post_request)
        result = get_all_comments_for_user_id(self.user_1.id).order_by('-id')
        self.assertTrue(len(result) == len_user_comments + 1)
        self.assertTrue(result.first().claim_id == self.new_comment_details_user_1['claim_id'])
        self.assertTrue(result.first().user_id == self.user_1.id)
        self.assertTrue(result.first().title == self.new_comment_details_user_1['title'])
        self.assertTrue(result.first().description == self.new_comment_details_user_1['description'])
        self.assertTrue(result.first().url == self.new_comment_details_user_1['url'])
        self.assertTrue(result.first().verdict_date == self.comment_4.verdict_date)
        self.assertTrue(result.first().label == self.new_comment_details_user_1['label'])

    def test_get_all_comments_for_added_user(self):
        user_3 = User(username="User3", email='user3@gmail.com')
        user_3.save()
        comment_4 = Comment(claim_id=self.claim_1.id,
                            user_id=user_3.id,
                            title=self.claim_1.claim,
                            description='description4',
                            url='url1',
                            verdict_date=datetime.date.today() - datetime.timedelta(days=random.randint(0, 10)),
                            label='label1')
        comment_4.save()
        result = get_all_comments_for_user_id(user_3.id)
        self.assertTrue(len(result) == 1)
        self.assertTrue(result.first().claim_id == comment_4.claim_id)
        self.assertTrue(result.first().user_id == comment_4.user_id)
        self.assertTrue(result.first().title == comment_4.title)
        self.assertTrue(result.first().description == comment_4.description)
        self.assertTrue(result.first().url == comment_4.url)
        self.assertTrue(result.first().verdict_date == comment_4.verdict_date)
        self.assertTrue(result.first().label == comment_4.label)

    def test_get_all_comments_for_invalid_user_id(self):
        result = get_all_comments_for_user_id(self.num_of_saved_users + random.randint(1, 10))
        self.assertTrue(result is None)

    def test_get_all_comments_for_claim_id(self):
        result_comment_1 = get_all_comments_for_claim_id(self.claim_1.id)
        self.assertTrue(len(result_comment_1) == 1)
        self.assertTrue(result_comment_1.first().claim_id == self.claim_1.id)
        self.assertTrue(result_comment_1.first().user_id == self.comment_1.user_id)
        self.assertTrue(result_comment_1.first().title == self.comment_1.title)
        self.assertTrue(result_comment_1.first().description == self.comment_1.description)
        self.assertTrue(result_comment_1.first().url == self.comment_1.url)
        self.assertTrue(result_comment_1.first().verdict_date == self.comment_1.verdict_date)
        self.assertTrue(result_comment_1.first().label == self.comment_1.label)

        result_comment_2 = get_all_comments_for_claim_id(self.claim_2.id)
        self.assertTrue(len(result_comment_2) == 1)
        self.assertTrue(result_comment_2.first().claim_id == self.claim_2.id)
        self.assertTrue(result_comment_2.first().user_id == self.comment_2.user_id)
        self.assertTrue(result_comment_2.first().title == self.comment_2.title)
        self.assertTrue(result_comment_2.first().description == self.comment_2.description)
        self.assertTrue(result_comment_2.first().url == self.comment_2.url)
        self.assertTrue(result_comment_2.first().verdict_date == self.comment_2.verdict_date)
        self.assertTrue(result_comment_2.first().label == self.comment_2.label)

    def test_get_all_comments_for_claim_id_user_added_new_comment(self):
        user_3 = User(username="User3", email='user3@gmail.com')
        user_3.save()
        comment_4 = Comment(claim_id=self.claim_1.id,
                            user_id=user_3.id,
                            title=self.claim_1.claim,
                            description='description4',
                            url='url1',
                            verdict_date=datetime.date.today() - datetime.timedelta(days=random.randint(0, 10)),
                            label='label1')
        comment_4.save()
        result_comment_1 = get_all_comments_for_claim_id(self.claim_1.id)
        self.assertTrue(len(result_comment_1) == 2)
        self.assertTrue(result_comment_1[0].claim_id == self.claim_1.id)
        self.assertTrue(result_comment_1[0].user_id == self.comment_1.user_id)
        self.assertTrue(result_comment_1[0].title == self.comment_1.title)
        self.assertTrue(result_comment_1[0].description == self.comment_1.description)
        self.assertTrue(result_comment_1[0].url == self.comment_1.url)
        self.assertTrue(result_comment_1[0].verdict_date == self.comment_1.verdict_date)
        self.assertTrue(result_comment_1[0].label == self.comment_1.label)
        self.assertTrue(result_comment_1[1].claim_id == comment_4.claim_id)
        self.assertTrue(result_comment_1[1].user_id == comment_4.user_id)
        self.assertTrue(result_comment_1[1].title == comment_4.title)
        self.assertTrue(result_comment_1[1].description == comment_4.description)
        self.assertTrue(result_comment_1[1].url == comment_4.url)
        self.assertTrue(result_comment_1[1].verdict_date == comment_4.verdict_date)
        self.assertTrue(result_comment_1[1].label == comment_4.label)

    def test_get_all_comments_for_invalid_claim_id(self):
        result = get_all_comments_for_claim_id(self.num_of_saved_claims + random.randint(1, 10))
        self.assertTrue(result is None)

    def test_update_authenticity_grade_two_true_comments(self):
        Comment.objects.filter(id=self.comment_1.id).update(system_label='True')
        self.comment_3.save()
        Comment.objects.filter(id=self.comment_3.id).update(system_label='True')
        update_authenticity_grade(self.claim_1.id)
        self.assertTrue(Claim.objects.filter(id=self.claim_1.id).first().authenticity_grade == 100)

    def test_update_authenticity_grade_true_and_false_comments(self):
        Comment.objects.filter(id=self.comment_1.id).update(system_label='True')
        self.comment_3.save()
        Comment.objects.filter(id=self.comment_3.id).update(system_label='False')
        update_authenticity_grade(self.claim_1.id)
        self.assertTrue(Claim.objects.filter(id=self.claim_1.id).first().authenticity_grade == 90)

    def test_update_authenticity_grade_true_and_false_with_down_vote(self):
        Comment.objects.filter(id=self.comment_1.id).update(system_label='True')
        self.comment_3.save()
        Comment.objects.filter(id=self.comment_3.id).update(system_label='False')
        comment_to_vote = {'comment_id': self.comment_3.id}
        query_dict = QueryDict('', mutable=True)
        query_dict.update(comment_to_vote)
        self.post_request.POST = query_dict
        self.post_request.user = self.user_1
        response = down_vote(self.post_request)
        self.assertTrue(response.status_code == self.error_code)
        Comment.objects.filter(id=self.comment_3.id).update(timestamp=datetime.datetime.now() -
                                                            datetime.timedelta(minutes=11))
        down_vote(self.post_request)
        update_authenticity_grade(self.claim_1.id)
        self.assertTrue(Claim.objects.filter(id=self.claim_1.id).first().authenticity_grade == 100)

    def test_update_authenticity_grade_true_and_false_with_up_vote(self):
        Comment.objects.filter(id=self.comment_1.id).update(system_label='True')
        self.comment_3.save()
        Comment.objects.filter(id=self.comment_3.id).update(system_label='False')
        comment_to_vote = {'comment_id': self.comment_3.id}
        query_dict = QueryDict('', mutable=True)
        query_dict.update(comment_to_vote)
        self.post_request.POST = query_dict
        self.post_request.user = self.user_2
        response = up_vote(self.post_request)
        self.assertTrue(response.status_code == self.error_code)
        Comment.objects.filter(id=self.comment_3.id).update(timestamp=datetime.datetime.now() -
                                                            datetime.timedelta(minutes=11))
        up_vote(self.post_request)
        update_authenticity_grade(self.claim_1.id)
        self.assertTrue(Claim.objects.filter(id=self.claim_1.id).first().authenticity_grade == 90)

    def test_update_authenticity_grade_true_with_up_vote_and_false(self):
        Comment.objects.filter(id=self.comment_1.id).update(system_label='True')
        self.comment_3.save()
        Comment.objects.filter(id=self.comment_3.id).update(system_label='False')
        comment_to_vote = {'comment_id': self.comment_1.id}
        query_dict = QueryDict('', mutable=True)
        query_dict.update(comment_to_vote)
        self.post_request.POST = query_dict
        self.post_request.user = self.user_2
        response = up_vote(self.post_request)
        self.assertTrue(response.status_code == self.error_code)
        Comment.objects.filter(id=self.comment_1.id).update(timestamp=datetime.datetime.now() -
                                                            datetime.timedelta(minutes=11))
        up_vote(self.post_request)
        update_authenticity_grade(self.claim_1.id)
        self.assertTrue(Claim.objects.filter(id=self.claim_1.id).first().authenticity_grade == 90)

    def test_update_authenticity_grade_true_with_down_vote_and_false(self):
        Comment.objects.filter(id=self.comment_1.id).update(system_label='True')
        self.comment_3.save()
        Comment.objects.filter(id=self.comment_3.id).update(system_label='False')
        comment_to_vote = {'comment_id': self.comment_1.id}
        query_dict = QueryDict('', mutable=True)
        query_dict.update(comment_to_vote)
        self.post_request.POST = query_dict
        self.post_request.user = self.user_1
        response = up_vote(self.post_request)
        self.assertTrue(response.status_code == self.error_code)
        Comment.objects.filter(id=self.comment_1.id).update(timestamp=datetime.datetime.now() -
                                                            datetime.timedelta(minutes=11))
        down_vote(self.post_request)
        update_authenticity_grade(self.claim_1.id)
        self.assertTrue(Claim.objects.filter(id=self.claim_1.id).first().authenticity_grade == 40)

    def test_update_authenticity_grade_true_with_down_vote_and_false_with_down_vote(self):
        Comment.objects.filter(id=self.comment_1.id).update(system_label='True')
        self.comment_3.save()
        Comment.objects.filter(id=self.comment_3.id).update(system_label='False')
        comment_to_vote = {'comment_id': self.comment_1.id}
        query_dict = QueryDict('', mutable=True)
        query_dict.update(comment_to_vote)
        self.post_request.POST = query_dict
        self.post_request.user = self.user_1
        response = down_vote(self.post_request)
        self.assertTrue(response.status_code == self.error_code)
        Comment.objects.filter(id=self.comment_1.id).update(timestamp=datetime.datetime.now() -
                                                            datetime.timedelta(minutes=11))
        down_vote(self.post_request)
        comment_to_vote['comment_id'] = self.comment_3.id
        query_dict = QueryDict('', mutable=True)
        query_dict.update(comment_to_vote)
        self.post_request.POST = query_dict
        response = down_vote(self.post_request)
        self.assertTrue(response.status_code == self.error_code)
        Comment.objects.filter(id=self.comment_3.id).update(timestamp=datetime.datetime.now() -
                                                            datetime.timedelta(minutes=11))
        down_vote(self.post_request)
        update_authenticity_grade(self.claim_1.id)
        self.assertTrue(Claim.objects.filter(id=self.claim_1.id).first().authenticity_grade == 50)

    def test_update_authenticity_grade_for_all_claims(self):
        admin = User.objects.create_superuser(username='admin', password='admin', email='admin@gmail.com')
        self.get_request.user = admin
        response = update_authenticity_grade_for_all_claims(self.get_request)
        self.assertTrue(response.status_code == 200)

    ################
    # Models Tests #
    ################

    def test__str__(self):
        self.assertTrue(self.comment_1.__str__() == self.comment_1.user.username + ' - ' + self.comment_1.title)
        self.assertTrue(self.comment_2.__str__() == self.comment_2.user.username + ' - ' + self.comment_2.title)
        self.assertTrue(self.comment_5.__str__() == self.comment_5.user.username + ' - ' + self.comment_5.title)
        self.assertTrue(self.comment_6.__str__() == self.comment_6.user.username + ' - ' + self.comment_6.title)

    def test_tags_as_list(self):
        self.assertTrue(self.comment_1.tags_as_list() == self.comment_1.tags.split(','))
        self.assertTrue(self.comment_2.tags_as_list() == self.comment_2.tags.split(','))
        self.assertTrue(self.comment_5.tags_as_list() == self.comment_5.tags.split(','))
        self.assertTrue(self.comment_6.tags_as_list() == self.comment_6.tags.split(','))

    def test_users_commented_ids(self):
        user_2 = User(username='User_2', email='user_2@gmail.com')
        user_2.save()
        user_3 = User(username='User_3', email='user_3@gmail.com')
        user_3.save()
        user_4 = User(username='User_4', email='user_4@gmail.com')
        user_4.save()

        for i in range(5):
            reply = Reply(user_id=user_2.id,
                          comment_id=self.comment_1.id,
                          content='content' + str(i))
            reply.save()
            reply = Reply(user_id=user_3.id,
                          comment_id=self.comment_1.id,
                          content='content' + str(i))
            reply.save()
            reply = Reply(user_id=user_4.id,
                          comment_id=self.comment_2.id,
                          content='content' + str(i))
            reply.save()
            if i % 2 == 0:
                reply = Reply(user_id=user_4.id,
                              comment_id=self.comment_2.id,
                              content='content' + str(i))
                reply.save()
        comment_1_users_replies_ids = self.comment_1.users_replied_ids()
        self.assertTrue(len(comment_1_users_replies_ids) == 2)
        self.assertTrue(user_2.id in comment_1_users_replies_ids)
        self.assertTrue(user_3.id in comment_1_users_replies_ids)

        comment_2_users_replies_ids = self.comment_2.users_replied_ids()
        self.assertTrue(len(comment_2_users_replies_ids) == 1)
        self.assertTrue(user_4.id in comment_2_users_replies_ids)

        comment_3_users_replies_ids = self.comment_3.users_replied_ids()
        self.assertTrue(len(comment_3_users_replies_ids) == 0)

    def test_get_replies(self):
        comment_1_replies = self.comment_1.get_replies()
        reply = comment_1_replies[0]
        self.assertTrue(reply.id == self.reply_1.id)
        self.assertTrue(reply.comment_id == self.reply_1.comment_id)
        self.assertTrue(reply.content == self.reply_1.content)
        reply = comment_1_replies[1]
        self.assertTrue(reply.id == self.reply_2.id)
        self.assertTrue(reply.comment_id == self.reply_2.comment_id)
        self.assertTrue(reply.content == self.reply_2.content)

        comment_2_replies = self.comment_2.get_replies()
        reply = comment_2_replies[0]
        self.assertTrue(reply.id == self.reply_3.id)
        self.assertTrue(reply.comment_id == self.reply_3.comment_id)
        self.assertTrue(reply.content == self.reply_3.content)

    def test_get_first_two_replies(self):
        user_3 = User(username='User_3', email='user_3@gmail.com')
        user_3.save()
        comment_1_replies = self.comment_1.get_first_two_replies()
        self.assertTrue(len(comment_1_replies) == 2)
        reply = comment_1_replies[0]
        self.assertTrue(reply.id == self.reply_1.id)
        self.assertTrue(reply.comment_id == self.reply_1.comment_id)
        self.assertTrue(reply.content == self.reply_1.content)
        reply = comment_1_replies[1]
        self.assertTrue(reply.id == self.reply_2.id)
        self.assertTrue(reply.comment_id == self.reply_2.comment_id)
        self.assertTrue(reply.content == self.reply_2.content)
        reply = Reply(user_id=user_3.id,
                      comment_id=self.comment_1.id,
                      content='content')
        reply.save()
        comment_1_replies = self.comment_1.get_first_two_replies()
        self.assertTrue(len(comment_1_replies) == 2)
        reply = comment_1_replies[0]
        self.assertTrue(reply.id == self.reply_1.id)
        self.assertTrue(reply.comment_id == self.reply_1.comment_id)
        self.assertTrue(reply.content == self.reply_1.content)
        reply = comment_1_replies[1]
        self.assertTrue(reply.id == self.reply_2.id)
        self.assertTrue(reply.comment_id == self.reply_2.comment_id)
        self.assertTrue(reply.content == self.reply_2.content)

        comment_2_replies = self.comment_2.get_first_two_replies()
        self.assertTrue(len(comment_2_replies) == 1)
        reply = comment_2_replies[0]
        self.assertTrue(reply.id == self.reply_3.id)
        self.assertTrue(reply.comment_id == self.reply_3.comment_id)
        self.assertTrue(reply.content == self.reply_3.content)

    def test_get_more_replies(self):
        user_3 = User(username='User_3', email='user_3@gmail.com')
        user_3.save()
        comment_1_replies = self.comment_1.get_more_replies()
        self.assertTrue(len(comment_1_replies) == 0)
        reply = Reply(user_id=user_3.id,
                      comment_id=self.comment_1.id,
                      content='content')
        reply.save()
        comment_1_replies = self.comment_1.get_more_replies()
        self.assertTrue(len(comment_1_replies) == 1)
        reply = comment_1_replies[0]
        self.assertTrue(reply.id == reply.id)
        self.assertTrue(reply.comment_id == reply.comment_id)
        self.assertTrue(reply.content == reply.content)

        comment_2_replies = self.comment_2.get_more_replies()
        self.assertTrue(len(comment_2_replies) == 0)

    def test_has_more_replies(self):
        user_3 = User(username='User_3', email='user_3@gmail.com')
        user_3.save()
        self.assertFalse(self.comment_1.has_more_replies())
        reply = Reply(user_id=user_3.id,
                      comment_id=self.comment_1.id,
                      content='content')
        reply.save()
        self.assertTrue(self.comment_1.has_more_replies())
        self.assertFalse(self.comment_2.has_more_replies())

    def test_get_preview(self):
        import json
        url = 'https://www.snopes.com/fact-check/bella-ramsey-break-dancing/'
        comment = Comment(claim_id=self.claim_1.id,
                          user_id=self.user_2.id,
                          title=self.claim_2.claim,
                          description='description1',
                          url=url,
                          tags='tag1',
                          verdict_date=datetime.date.today() - datetime.timedelta(days=random.randint(1, 10)),
                          label='label1')
        comment.save()
        url = 'http://factscan.ca/andrew-scheer-canadas-sovereignty/'
        comment_2 = Comment(claim_id=self.claim_2.id,
                          user_id=self.user_2.id,
                          title=self.claim_2.claim,
                          description='description1',
                          url=url,
                          tags='tag1',
                          verdict_date=datetime.date.today() - datetime.timedelta(days=random.randint(1, 10)),
                          label='label1')
        comment_2.save()

        comment_preview = comment.get_preview()
        preview = {'title': "FACT CHECK: Does a Viral Video Really Show \'Game of Thrones\' Actress Bella Ramsey Break-Dancing?",
                   'description': 'The English actress may have moves on the battlefield, but does she have moves on the dance floor?',
                   'src': 'https://www.snopes.com/tachyon/2019/05/bella-ramsey-getty-british-academy-childrens-awards-2018.jpg?fit=1200,628'}
        self.assertTrue(json.dumps(preview) == comment_preview)
        self.assertFalse(comment_2.get_preview())

    def test_vote_on_comment(self):
        from django.utils import timezone
        self.assertFalse(self.comment_1.vote_on_comment())
        comment = Comment.objects.create(claim_id=self.claim_4.id,
                                         user_id=self.claim_4.user_id,
                                         title=self.claim_4.claim,
                                         description='description6',
                                         url=self.url + str(random.randint(1, 10)),
                                         tags='',
                                         verdict_date=datetime.date.today() - datetime.timedelta(days=random.randint(1, 10)),
                                         label='label6',
                                         timestamp=(timezone.now() - datetime.timedelta(minutes=11)))
        comment.save()
        self.assertTrue(comment.vote_on_comment())



