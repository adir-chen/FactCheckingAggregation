from django.http import HttpRequest, Http404, QueryDict
from django.test import TestCase
from django.utils.datastructures import MultiValueDict
from claims.models import Claim
from comments.models import Comment
from comments.views import add_comment, build_comment, check_if_comment_is_valid, convert_date_format, \
    is_valid_verdict_date, get_system_label_to_comment, get_all_comments_for_user_id, get_all_comments_for_claim_id, \
    export_to_csv, check_if_csv_fields_are_valid, create_df_for_claims, check_if_fields_and_scrapers_lists_valid,\
    up_vote, down_vote, check_if_vote_is_valid, edit_comment, check_comment_new_fields, delete_comment, \
    check_if_delete_comment_is_valid, update_authenticity_grade
from users.models import User, Scrapers
import datetime
import random


class CommentTests(TestCase):
    def setUp(self):
        self.user_1 = User(username="User1", email='user1@gmail.com')
        self.user_2 = User(username="User2", email='user2@gmail.com')
        self.user_1.save()
        self.user_2.save()
        self.new_scraper_1 = User(username="newScraper1")
        self.new_scraper_1.save()
        self.new_scraper_scraper_1 = Scrapers(scraper_name=self.new_scraper_1.username,
                                              scraper_id=self.new_scraper_1)
        self.new_scraper_scraper_1.save()

        self.new_scraper_2 = User(username="newScraper2")
        self.new_scraper_2.save()
        self.new_scraper_scraper_2 = Scrapers(scraper_name=self.new_scraper_2.username,
                                              scraper_id=self.new_scraper_2)
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
        self.comment_1 = Comment(claim_id=self.claim_1.id,
                                 user_id=self.user_1.id,
                                 title=self.claim_1.claim,
                                 description='description1',
                                 url='url1',
                                 tags='tag1',
                                 verdict_date=datetime.date.today() - datetime.timedelta(days=random.randint(1, 10)),
                                 label='label1')
        self.comment_2 = Comment(claim_id=self.claim_2.id,
                                 user_id=self.user_2.id,
                                 title=self.claim_2.claim,
                                 description='description2',
                                 url='url2',
                                 tags='tag2,tag3',
                                 verdict_date=datetime.date.today() - datetime.timedelta(days=random.randint(1, 10)),
                                 label='label2')
        self.comment_3 = Comment(claim_id=self.claim_1.id,
                                 user_id=self.user_2.id,
                                 title=self.claim_1.claim,
                                 description='description3',
                                 url='url3',
                                 tags='',
                                 verdict_date=datetime.date.today() - datetime.timedelta(days=random.randint(1, 10)),
                                 label='label3')
        self.comment_4 = Comment(claim_id=self.claim_2.id,
                                 user_id=self.user_1.id,
                                 title=self.claim_2.claim,
                                 description='description4',
                                 url='url4',
                                 tags='',
                                 verdict_date=datetime.date.today() - datetime.timedelta(days=random.randint(1, 10)),
                                 label='label4')
        self.comment_5 = Comment(claim_id=self.claim_3.id,
                                 user_id=self.claim_3.user_id,
                                 title=self.claim_3.claim,
                                 description='description5',
                                 url='url5',
                                 tags='',
                                 verdict_date=datetime.date.today() - datetime.timedelta(days=random.randint(1, 10)),
                                 label='label5')
        self.comment_6 = Comment(claim_id=self.claim_4.id,
                                 user_id=self.claim_4.user_id,
                                 title=self.claim_4.claim,
                                 description='description6',
                                 url='url6',
                                 tags='',
                                 verdict_date=datetime.date.today() - datetime.timedelta(days=random.randint(1, 10)),
                                 label='label6')
        self.comment_1.save()
        self.comment_2.save()
        self.comment_5.save()
        self.comment_6.save()
        self.num_of_saved_comments = 4
        self.new_comment_details_user_1 = {'claim_id': self.comment_4.claim_id,
                                           'title': self.comment_4.title,
                                           'description': self.comment_4.description,
                                           'url': self.comment_4.url,
                                           'verdict_date': datetime.datetime.strptime(str(self.comment_4.verdict_date), '%Y-%m-%d').strftime('%d/%m/%Y'),
                                           'label': self.comment_4.label}
        self.new_comment_details_user_2 = {'claim_id': self.comment_3.claim_id,
                                           'title': self.comment_3.title,
                                           'description': self.comment_3.description,
                                           'url': self.comment_3.url,
                                           'verdict_date': datetime.datetime.strptime(str(self.comment_3.verdict_date), '%Y-%m-%d').strftime('%d/%m/%Y'),
                                           'label': self.comment_3.label}

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

    def test_add_comment_by_user_not_authenticated(self):
        from django.contrib.auth.models import AnonymousUser
        self.post_request.POST = self.new_comment_details_user_1
        self.post_request.user = AnonymousUser()
        self.assertRaises(Http404, add_comment, self.post_request)

    def test_add_comment_by_invalid_user(self):
        guest = User(id=self.num_of_saved_users + random.randint(1, 10), username='guest')
        self.post_request.POST = self.new_comment_details_user_1
        self.post_request.user = guest
        self.assertRaises(Exception, add_comment, self.post_request)

    def test_add_comment_get_request(self):
        self.post_request.method = 'GET'
        self.post_request.POST = self.new_comment_details_user_1
        self.post_request.user = self.user_1
        self.assertRaises(Http404, add_comment, self.post_request)

    def test_add_comment_missing_claim_id(self):
        del self.new_comment_details_user_1['claim_id']
        self.post_request.POST = self.new_comment_details_user_1
        self.post_request.user = self.user_1
        self.assertRaises(Exception, add_comment, self.post_request)

        del self.new_comment_details_user_2['claim_id']
        self.post_request.POST = self.new_comment_details_user_2
        self.post_request.user = self.user_2
        self.assertRaises(Exception, add_comment, self.post_request)

    def test_add_comment_missing_title(self):
        del self.new_comment_details_user_1['title']
        self.post_request.POST = self.new_comment_details_user_1
        self.post_request.user = self.user_1
        self.assertRaises(Exception, add_comment, self.post_request)

        del self.new_comment_details_user_2['title']
        self.post_request.POST = self.new_comment_details_user_2
        self.post_request.user = self.user_2
        self.assertRaises(Exception, add_comment, self.post_request)

    def test_add_comment_missing_description(self):
        del self.new_comment_details_user_1['description']
        self.post_request.POST = self.new_comment_details_user_1
        self.post_request.user = self.user_1
        self.assertRaises(Exception, add_comment, self.post_request)

        del self.new_comment_details_user_2['description']
        self.post_request.POST = self.new_comment_details_user_2
        self.post_request.user = self.user_2
        self.assertRaises(Exception, add_comment, self.post_request)

    def test_add_comment_missing_url(self):
        del self.new_comment_details_user_1['url']
        self.post_request.POST = self.new_comment_details_user_1
        self.post_request.user = self.user_1
        self.assertRaises(Exception, add_comment, self.post_request)

        del self.new_comment_details_user_2['url']
        self.post_request.POST = self.new_comment_details_user_2
        self.post_request.user = self.user_2
        self.assertRaises(Exception, add_comment, self.post_request)

    def test_add_comment_missing_verdict_date(self):
        del self.new_comment_details_user_1['verdict_date']
        self.post_request.POST = self.new_comment_details_user_1
        self.post_request.user = self.user_1
        self.assertRaises(Exception, add_comment, self.post_request)

        del self.new_comment_details_user_2['verdict_date']
        self.post_request.POST = self.new_comment_details_user_2
        self.post_request.user = self.user_2
        self.assertRaises(Exception, add_comment, self.post_request)

    def test_add_comment_missing_label(self):
        del self.new_comment_details_user_1['label']
        self.post_request.POST = self.new_comment_details_user_1
        self.post_request.user = self.user_1
        self.assertRaises(Exception, add_comment, self.post_request)

        del self.new_comment_details_user_2['label']
        self.post_request.POST = self.new_comment_details_user_2
        self.post_request.user = self.user_2
        self.assertRaises(Exception, add_comment, self.post_request)

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
            self.assertRaises(Exception, add_comment, self.post_request)
            self.assertTrue(len(Comment.objects.filter(claim_id=self.claim_1.id)) == len_comments)
            self.new_comment_details_user_1 = dict_copy.copy()

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

    def test_check_if_comment_is_valid_comment_twice(self):
        self.new_comment_details_user_1['user_id'] = str(self.user_1.id)
        self.new_comment_details_user_2['user_id'] = str(self.user_2.id)
        self.new_comment_details_user_1['claim_id'] = str(self.claim_1.id)
        self.new_comment_details_user_2['claim_id'] = str(self.claim_2.id)
        self.assertFalse(check_if_comment_is_valid(self.new_comment_details_user_1)[0])
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
        self.new_comment_details_user_1['tags'] = 'tag1, tag2'
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
        from django.contrib.auth import get_user_model
        User = get_user_model()
        admin = User.objects.create_superuser(username='admin',
                                              email='admin@gmail.com',
                                              password='admin')
        self.post_request.user = admin
        add_all_scrapers(self.post_request)
        for scraper in Scrapers.objects.all():
            for true_label in scraper.true_labels.split(','):
                self.assertTrue('True' == get_system_label_to_comment(true_label, scraper.scraper_id.id))
            for false_label in scraper.false_labels.split(','):
                self.assertTrue('False' == get_system_label_to_comment(false_label, scraper.scraper_id.id))
            self.assertTrue('Unknown' == get_system_label_to_comment('Unknown', scraper.scraper_id.id))

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

    def test_export_to_csv(self):
        admin = User.objects.create_superuser('admin', 'admin@gmail.com', 'admin')
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.csv_fields)
        self.post_request.POST = query_dict
        self.post_request.user = admin
        res = export_to_csv(self.post_request)
        self.assertTrue(res.status_code == 200)
        expected_info = 'Title,Description,Url,Category,Verdict Date,Tags,Label,System Label,Authenticity Grade\r\n'\
                        'claim3,description5,url5,category3,' + str(self.comment_5.verdict_date) + ',,label5,,0\r\n'\
                        'claim4,description6,url6,category4,' + str(self.comment_6.verdict_date) + ',,label6,,0\r\n'
        self.assertEqual(res.content.decode('utf-8'), expected_info)

        Comment.objects.filter(id=self.comment_5.id).update(tags='tag1', system_label='True')
        Comment.objects.filter(id=self.comment_6.id).update(tags='tag6, tag7', system_label='False')
        res = export_to_csv(self.post_request)
        self.assertTrue(res.status_code == 200)
        expected_info = 'Title,Description,Url,Category,Verdict Date,Tags,Label,System Label,Authenticity Grade\r\n' + \
                        'claim3,description5,url5,category3,' + str(self.comment_5.verdict_date) + ',tag1,label5,True,0\r\n'\
                        'claim4,description6,url6,category4,' + str(self.comment_6.verdict_date) + ',"tag6, tag7",label6,False,0\r\n'
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
        self.assertRaises(Exception, export_to_csv, self.post_request)

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
        self.assertRaises(Exception, export_to_csv, self.post_request)

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
            self.assertRaises(Exception, export_to_csv, self.post_request)
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
                        'Title,Description,Url,Category,Verdict Date,Tags,Label,System Label,Authenticity Grade\r\n')

    def test_export_to_csv_not_authenticated_user(self):
        from django.contrib.auth.models import AnonymousUser
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.csv_fields)
        self.post_request.POST = query_dict
        self.post_request.user = AnonymousUser()
        self.assertRaises(Http404, export_to_csv, self.post_request)

    def test_export_to_csv_not_admin_user(self):
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.csv_fields)
        self.post_request.POST = query_dict
        self.post_request.user = self.user_1
        self.assertRaises(Http404, export_to_csv, self.post_request)

    def test_check_if_csv_fields_are_valid(self):
        self.assertTrue(check_if_csv_fields_are_valid(self.csv_fields)[0])

    def test_check_if_csv_fields_are_valid_with_regular_users(self):
        self.csv_fields['regular_users'] = 'True'
        self.assertTrue(check_if_csv_fields_are_valid(self.csv_fields)[0])

    def test_check_if_csv_fields_are_valid_missing_fields_to_export(self):
        del self.csv_fields['fields_to_export[]']
        self.assertFalse(check_if_csv_fields_are_valid(self.csv_fields)[0])

    def test_check_if_csv_fields_are_valid_missing_scrapers_ids(self):
        del self.csv_fields['scrapers_ids[]']
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

    def test_up_vote(self):
        comment_to_vote = {'comment_id': self.comment_2.id}
        query_dict = QueryDict('', mutable=True)
        query_dict.update(comment_to_vote)
        self.post_request.POST = query_dict
        self.post_request.user = self.user_1
        self.assertRaises(Exception, up_vote, self.post_request)
        Comment.objects.filter(id=self.comment_2.id).update(timestamp=datetime.datetime.now() -
                                                            datetime.timedelta(minutes=6))
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
        self.assertRaises(Exception, up_vote, self.post_request)
        Comment.objects.filter(id=self.comment_2.id).update(timestamp=datetime.datetime.now() -
                                                            datetime.timedelta(minutes=6))
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
        self.assertRaises(Exception, down_vote, self.post_request)
        self.assertRaises(Exception, up_vote, self.post_request)
        Comment.objects.filter(id=self.comment_2.id).update(timestamp=datetime.datetime.now() -
                                                            datetime.timedelta(minutes=6))
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
        self.assertRaises(Http404, up_vote, self.post_request)

    def test_up_vote_invalid_user(self):
        user = User(id=self.num_of_saved_users + random.randint(1, 10), email="user@gmail.com")
        comment_to_vote = {'comment_id': self.comment_1.id}
        query_dict = QueryDict('', mutable=True)
        query_dict.update(comment_to_vote)
        self.post_request.POST = query_dict
        self.post_request.user = user
        self.assertRaises(Exception, down_vote, self.post_request)

    def test_down_vote(self):
        comment_to_vote = {'comment_id': self.comment_1.id}
        query_dict = QueryDict('', mutable=True)
        query_dict.update(comment_to_vote)
        self.post_request.POST = query_dict
        self.post_request.user = self.user_2
        self.assertRaises(Exception, down_vote, self.post_request)
        Comment.objects.filter(id=self.comment_1.id).update(timestamp=datetime.datetime.now() -
                                                            datetime.timedelta(minutes=6))
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
        self.assertRaises(Exception, down_vote, self.post_request)
        Comment.objects.filter(id=self.comment_1.id).update(timestamp=datetime.datetime.now() -
                                                            datetime.timedelta(minutes=6))
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
        self.assertRaises(Exception, up_vote, self.post_request)
        self.assertRaises(Exception, down_vote, self.post_request)
        Comment.objects.filter(id=self.comment_1.id).update(timestamp=datetime.datetime.now() -
                                                            datetime.timedelta(minutes=6))
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
        self.assertRaises(Http404, down_vote, self.post_request)

    def test_down_vote_invalid_user(self):
        user = User(id=self.num_of_saved_users + random.randint(1, 10), email="user@gmail.com")
        comment_to_vote = {'comment_id': self.comment_1.id}
        query_dict = QueryDict('', mutable=True)
        query_dict.update(comment_to_vote)
        self.post_request.POST = query_dict
        self.post_request.user = user
        self.assertRaises(Exception, down_vote, self.post_request)

    def test_check_if_vote_is_valid(self):
        comment_to_vote = {'comment_id': self.comment_1.id,
                           'user_id': self.user_1.id}
        self.assertFalse(check_if_vote_is_valid(comment_to_vote)[0])
        Comment.objects.filter(id=self.comment_1.id).update(timestamp=datetime.datetime.now() -
                                                            datetime.timedelta(minutes=6))
        self.assertTrue(check_if_vote_is_valid(comment_to_vote)[0])

    def test_check_if_vote_is_valid_missing_user_id(self):
        comment_to_vote = {'comment_id': self.comment_1.id}
        self.assertFalse(check_if_vote_is_valid(comment_to_vote)[0])

    def test_check_if_vote_is_valid_missing_invalid_user_id(self):
        comment_to_vote = {'comment_id': self.comment_1.id,
                           'user_id': self.num_of_saved_users + random.randint(1, 10)}
        self.assertFalse(check_if_vote_is_valid(comment_to_vote)[0])

    def test_check_if_vote_is_valid_missing_comment_id(self):
        comment_to_vote = {'user_id': self.user_1.id}
        self.assertFalse(check_if_vote_is_valid(comment_to_vote)[0])

    def test_check_if_vote_is_valid_missing_invalid_comment_id(self):
        comment_to_vote = {'comment_id': self.num_of_saved_comments + random.randint(1, 10),
                           'user_id': self.user_1.id}
        self.assertFalse(check_if_vote_is_valid(comment_to_vote)[0])

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
        self.assertRaises(Exception, edit_comment, self.post_request)
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
        self.assertRaises(Exception, edit_comment, self.post_request)
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
        self.assertRaises(Exception, edit_comment, self.post_request)
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
            self.assertRaises(Exception, edit_comment, self.post_request)
            self.update_comment_details = dict_copy.copy()

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

    def test_check_comment_new_fields_edit_after_five_minutes(self):
        Comment.objects.filter(id=self.comment_1.id).update(timestamp=datetime.datetime.now() -
                                                            datetime.timedelta(minutes=6))
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
        self.assertRaises(Exception, delete_comment, self.post_request)
        self.assertTrue(len(Comment.objects.all()) == len_comments)

    def test_delete_comment_by_invalid_user(self):
        user = User(id=self.num_of_saved_users + random.randint(1, 10), email='user@gmail.com')
        comment_to_delete = {'comment_id': self.comment_1.id}
        self.post_request.POST = comment_to_delete
        self.post_request.user = user
        len_comments = len(Comment.objects.all())
        self.assertRaises(Exception, delete_comment, self.post_request)
        self.assertTrue(len(Comment.objects.all()) == len_comments)

    def test_delete_comment_by_not_authenticated_user(self):
        from django.contrib.auth.models import AnonymousUser
        comment_to_delete = {'comment_id': self.comment_1.id}
        self.post_request.POST = comment_to_delete
        self.post_request.user = AnonymousUser()
        len_comments = len(Comment.objects.all())
        self.assertRaises(Http404, delete_comment, self.post_request)
        self.assertTrue(len(Comment.objects.all()) == len_comments)

    def test_delete_comment_by_invalid_comment_id(self):
        comment_to_delete = {'comment_id': self.num_of_saved_comments + random.randint(1, 10)}
        self.post_request.POST = comment_to_delete
        self.post_request.user = self.user_1
        len_comments = len(Comment.objects.all())
        self.assertRaises(Exception, delete_comment, self.post_request)
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

    def test_update_authenticity_grade_true(self):
        Comment.objects.filter(id=self.comment_1.id).update(system_label='True')
        self.comment_3.save()
        Comment.objects.filter(id=self.comment_3.id).update(system_label='True')
        update_authenticity_grade(self.claim_1.id)
        self.assertTrue(Claim.objects.filter(id=self.claim_1.id).first().authenticity_grade == 100)

    def test_update_authenticity_grade_true_and_false(self):
        Comment.objects.filter(id=self.comment_1.id).update(system_label='True')
        self.comment_3.save()
        Comment.objects.filter(id=self.comment_3.id).update(system_label='False')
        update_authenticity_grade(self.claim_1.id)
        self.assertTrue(Claim.objects.filter(id=self.claim_1.id).first().authenticity_grade == 50)

    def test_update_authenticity_grade_true_and_false_with_down_vote(self):
        Comment.objects.filter(id=self.comment_1.id).update(system_label='True')
        self.comment_3.save()
        Comment.objects.filter(id=self.comment_3.id).update(system_label='False')
        comment_to_vote = {'comment_id': self.comment_3.id}
        query_dict = QueryDict('', mutable=True)
        query_dict.update(comment_to_vote)
        self.post_request.POST = query_dict
        self.post_request.user = self.user_1
        self.assertRaises(Exception, down_vote, self.post_request)
        Comment.objects.filter(id=self.comment_3.id).update(timestamp=datetime.datetime.now() -
                                                            datetime.timedelta(minutes=6))
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
        self.assertRaises(Exception, up_vote, self.post_request)
        Comment.objects.filter(id=self.comment_3.id).update(timestamp=datetime.datetime.now() -
                                                            datetime.timedelta(minutes=6))
        up_vote(self.post_request)
        update_authenticity_grade(self.claim_1.id)
        self.assertTrue(Claim.objects.filter(id=self.claim_1.id).first().authenticity_grade == 50)

    def test_update_authenticity_grade_true_with_up_vote_and_false(self):
        Comment.objects.filter(id=self.comment_1.id).update(system_label='True')
        self.comment_3.save()
        Comment.objects.filter(id=self.comment_3.id).update(system_label='False')
        comment_to_vote = {'comment_id': self.comment_1.id}
        query_dict = QueryDict('', mutable=True)
        query_dict.update(comment_to_vote)
        self.post_request.POST = query_dict
        self.post_request.user = self.user_2
        self.assertRaises(Exception, up_vote, self.post_request)
        Comment.objects.filter(id=self.comment_1.id).update(timestamp=datetime.datetime.now() -
                                                            datetime.timedelta(minutes=6))
        up_vote(self.post_request)
        update_authenticity_grade(self.claim_1.id)
        self.assertTrue(Claim.objects.filter(id=self.claim_1.id).first().authenticity_grade == 50)

    def test_update_authenticity_grade_true_with_down_vote_and_false(self):
        Comment.objects.filter(id=self.comment_1.id).update(system_label='True')
        Comment.objects.filter(id=self.comment_3.id).update(system_label='False')
        comment_to_vote = {'comment_id': self.comment_1.id}
        query_dict = QueryDict('', mutable=True)
        query_dict.update(comment_to_vote)
        self.post_request.POST = query_dict
        self.post_request.user = self.user_1
        self.assertRaises(Exception, up_vote, self.post_request)
        Comment.objects.filter(id=self.comment_1.id).update(timestamp=datetime.datetime.now() -
                                                            datetime.timedelta(minutes=6))
        down_vote(self.post_request)
        update_authenticity_grade(self.claim_1.id)
        self.assertTrue(Claim.objects.filter(id=self.claim_1.id).first().authenticity_grade == 0)

    def test_update_authenticity_grade_true_with_down_vote_and_false_with_down_vote(self):
        Comment.objects.filter(id=self.comment_1.id).update(system_label='True')
        self.comment_3.save()
        Comment.objects.filter(id=self.comment_3.id).update(system_label='False')
        comment_to_vote = {'comment_id': self.comment_1.id}
        query_dict = QueryDict('', mutable=True)
        query_dict.update(comment_to_vote)
        self.post_request.POST = query_dict
        self.post_request.user = self.user_1
        self.assertRaises(Exception, down_vote, self.post_request)
        Comment.objects.filter(id=self.comment_1.id).update(timestamp=datetime.datetime.now() -
                                                            datetime.timedelta(minutes=6))
        down_vote(self.post_request)
        comment_to_vote['comment_id'] = self.comment_3.id
        query_dict = QueryDict('', mutable=True)
        query_dict.update(comment_to_vote)
        self.post_request.POST = query_dict
        self.assertRaises(Exception, down_vote, self.post_request)
        Comment.objects.filter(id=self.comment_3.id).update(timestamp=datetime.datetime.now() -
                                                            datetime.timedelta(minutes=6))
        down_vote(self.post_request)
        update_authenticity_grade(self.claim_1.id)
        self.assertTrue(Claim.objects.filter(id=self.claim_1.id).first().authenticity_grade == 0)
