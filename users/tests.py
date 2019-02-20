from django.http import HttpRequest, QueryDict, Http404
from django.test import TestCase
from users.models import User, Scrapers
from claims.models import Claim
from comments.models import Comment
from users.views import check_if_user_exists_by_user_id, get_username_by_user_id, add_all_scrapers, \
    get_all_scrapers_ids, get_random_claims_from_scrapers, add_scraper_guide, add_new_scraper, \
    check_if_scraper_info_is_valid
import json
import random


class UsersTest(TestCase):
    def setUp(self):
        self.user_1 = User(username="User1", email='user1@gmail.com')
        self.user_2 = User(username="User2", email='user2@gmail.com')
        self.user_3 = User(username="User3", email='user3@gmail.com')
        new_scraper = User(username="newScraper")

        self.user_1.save()
        self.user_2.save()
        self.user_3.save()
        new_scraper.save()

        self.post_request = HttpRequest()
        self.post_request.method = 'POST'
        self.data = {'scraper_name': 'newScraper_2',
                     'scraper_icon': 'newScraperIcon'}

    def tearDown(self):
        pass

    def test_check_if_user_exists_by_user_id(self):
        self.assertTrue(check_if_user_exists_by_user_id(1))
        self.assertTrue(check_if_user_exists_by_user_id(2))
        self.assertTrue(check_if_user_exists_by_user_id(3))

    def test_check_if_user_exists_by_invalid_user_id(self):
        self.assertFalse(check_if_user_exists_by_user_id(5))

    def test_get_username_by_user_id(self):
        self.assertTrue(get_username_by_user_id(1) == self.user_1.username)
        self.assertTrue(get_username_by_user_id(2) == self.user_2.username)
        self.assertTrue(get_username_by_user_id(3) == self.user_3.username)

    def test_get_username_by_user_id_invalid_user(self):
        self.assertTrue(get_username_by_user_id(5) is None)

    def test_add_all_scrapers(self):
        add_all_scrapers(HttpRequest())
        self.assertTrue(check_if_user_exists_by_user_id(5))
        self.assertTrue(check_if_user_exists_by_user_id(6))
        self.assertTrue(check_if_user_exists_by_user_id(7))
        self.assertTrue(check_if_user_exists_by_user_id(8))
        self.assertTrue(check_if_user_exists_by_user_id(9))
        self.assertTrue(check_if_user_exists_by_user_id(10))
        self.assertTrue(check_if_user_exists_by_user_id(11))
        self.assertTrue(check_if_user_exists_by_user_id(12))
        self.assertTrue(get_username_by_user_id(5) == 'Snopes')
        self.assertTrue(get_username_by_user_id(6) == 'Polygraph')
        self.assertTrue(get_username_by_user_id(7) == 'TruthOrFiction')
        self.assertTrue(get_username_by_user_id(8) == 'Politifact')
        self.assertTrue(get_username_by_user_id(9) == 'GossipCop')
        self.assertTrue(get_username_by_user_id(10) == 'ClimateFeedback')
        self.assertTrue(get_username_by_user_id(11) == 'FactScan')
        self.assertTrue(get_username_by_user_id(12) == 'AfricaCheck')

    def test_get_all_scrapers_ids(self):
        import json
        add_all_scrapers(HttpRequest())
        scrapers_ids = json.loads(get_all_scrapers_ids(HttpRequest()).content.decode('utf-8'))
        self.assertTrue(scrapers_ids == {'Snopes': 5,
                                         'Polygraph': 6,
                                         'TruthOrFiction': 7,
                                         'Politifact': 8,
                                         'GossipCop': 9,
                                         'ClimateFeedback': 10,
                                         'FactScan': 11,
                                         'AfricaCheck': 12,
                                         })

    def test_get_random_claims_from_scrapers_not_many_claims(self):
        from claims.models import Claim
        from comments.models import Comment
        scrapers_comments = {}
        add_all_scrapers(HttpRequest())
        scrapers_names = ['Snopes', 'Polygraph', 'TruthOrFiction', 'Politifact', 'GossipCop',
                             'ClimateFeedback', 'FactScan', 'AfricaCheck']
        for i in range(len(scrapers_names)):
            claim = Claim(user_id=Scrapers.objects.filter(scraper_name=scrapers_names[i])[0].scraper_id.id,
                          claim='Sniffing rosemary increases human memory by up to 75 percent',
                          category='Science',
                          tags="sniffing human memory",
                          authenticity_grade=0)
            claim.save()
            comment = Comment(claim_id=claim.id,
                                 user_id=Scrapers.objects.filter(scraper_name=scrapers_names[i])[0].scraper_id.id,
                                 title='title_' + str(i + 1),
                                 description='description_' + str(i + 1),
                                 url='url_' + str(i + 1),
                                 verdict_date='11/2/2019',
                                 label='label' + str(i + 1))
            comment.save()
            scrapers_comments[scrapers_names[i]] = [claim, comment]
        import json
        scrapers_comments_val = json.loads(get_random_claims_from_scrapers(HttpRequest()).content.decode('utf-8'))
        for scraper_name, scraper_comment in scrapers_comments_val.items():
            self.assertTrue(scraper_comment == {'title': scrapers_comments[scraper_name][1].title,
                    'claim': scrapers_comments[scraper_name][0].claim,
                    'description': scrapers_comments[scraper_name][1].description,
                    'url': scrapers_comments[scraper_name][1].url,
                    'verdict_date': scrapers_comments[scraper_name][1].verdict_date,
                    'category': scrapers_comments[scraper_name][0].category,
                    'label':  scrapers_comments[scraper_name][1].label})

    def test_get_random_claims_from_scrapers_many_claims(self):
        scrapers_comments = {}
        add_all_scrapers(HttpRequest())
        scrapers_names = ['Snopes', 'Polygraph', 'TruthOrFiction', 'Politifact', 'GossipCop',
                             'ClimateFeedback', 'FactScan', 'AfricaCheck']
        for i in range(len(scrapers_names)):
            claim_1 = Claim(user_id=Scrapers.objects.filter(scraper_name=scrapers_names[i])[0].scraper_id.id,
                          claim='Sniffing rosemary increases human memory by up to 75 percent' + str(i),
                          category='Science',
                          tags="sniffing human memory",
                          authenticity_grade=0)
            claim_2 = Claim(user_id=Scrapers.objects.filter(scraper_name=scrapers_names[i])[0].scraper_id.id,
                          claim='Sniffing rosemary increases human memory by up to 75 percent' + str(i + 1),
                          category='Science',
                          tags="sniffing human memory",
                          authenticity_grade=0)
            claim_2.save()
            claim_1.save()
            comment_1 = Comment(claim_id=claim_1.id,
                                 user_id=Scrapers.objects.filter(scraper_name=scrapers_names[i])[0].scraper_id.id,
                                 title='title_' + str(i + 1),
                                 description='description_' + str(i + 1),
                                 url='url_' + str(i + 1),
                                 verdict_date='11/2/2019',
                                 label='label' + str(i + 1))
            comment_2 = Comment(claim_id=claim_2.id,
                                 user_id=Scrapers.objects.filter(scraper_name=scrapers_names[i])[0].scraper_id.id,
                                 title='title_' + str(i + 2),
                                 description='description_' + str(i + 2),
                                 url='url_' + str(i + 2),
                                 verdict_date='11/2/2019',
                                 label='label' + str(i + 2))
            comment_2.save()
            comment_1.save()
            scrapers_comments[scrapers_names[i]] = [claim_1, comment_1]
            scrapers_comments_val = json.loads(get_random_claims_from_scrapers(HttpRequest()).content.decode('utf-8'))
        for scraper_name, scraper_comment in scrapers_comments_val.items():
            self.assertTrue(scraper_comment == {'title': scrapers_comments[scraper_name][1].title,
                    'claim': scrapers_comments[scraper_name][0].claim,
                    'description': scrapers_comments[scraper_name][1].description,
                    'url': scrapers_comments[scraper_name][1].url,
                    'verdict_date': scrapers_comments[scraper_name][1].verdict_date,
                    'category': scrapers_comments[scraper_name][0].category,
                    'label':  scrapers_comments[scraper_name][1].label})

    def test_add_scraper_guide(self):
        self.assertTrue(add_scraper_guide(HttpRequest()).status_code == 200)

    def test_add_new_scraper_valid(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        admin = User.objects.create_superuser('admin', 'admin@gmail.com', 'admin')
        self.post_request.user = admin
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.data)
        self.post_request.POST = query_dict
        old_length = len(User.objects.all())
        self.assertTrue(add_new_scraper(self.post_request).status_code == 200)
        self.assertTrue(len(User.objects.all()) == old_length + 1)

    def test_add_new_scraper_by_invalid_user(self):
        self.post_request.user = self.user_1
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.data)
        self.post_request.POST = query_dict
        old_length = len(User.objects.all())
        self.assertRaises(Http404, add_new_scraper, self.post_request)
        self.assertTrue(len(User.objects.all()) == old_length)

    def test_add_existing_scraper(self):
        self.data['scraper_name'] = 'newScraper'
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.data)
        self.post_request.POST = query_dict
        old_length = len(User.objects.all())
        self.assertRaises(Exception, add_new_scraper, self.post_request)
        self.assertTrue(len(User.objects.all()) == old_length)

    def test_add_claim_missing_args(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        admin = User.objects.create_superuser('admin', 'admin@gmail.com', 'admin')
        self.post_request.user = admin
        for i in range(10):
            dict_copy = self.data.copy()
            args_to_remove = []
            for j in range(random.randint(1, len(self.data.keys()) - 1)):
                args_to_remove.append(list(self.data.keys())[j])
            for j in range(len(args_to_remove)):
                del self.data[args_to_remove[j]]
            len_users = len(User.objects.all())
            query_dict = QueryDict('', mutable=True)
            query_dict.update(self.data)
            self.post_request.POST = query_dict
            self.assertRaises(Exception, add_new_scraper, self.post_request)
            self.assertTrue(len(User.objects.all()) == len_users)
            self.data = dict_copy.copy()

    def test_add_new_scraper_get(self):
        request = HttpRequest()
        request.user = self.user_2
        request.method = 'GET'
        self.assertRaises(Http404, add_new_scraper, request)

    def test_check_if_scraper_info_is_valid(self):
        self.assertTrue(check_if_scraper_info_is_valid(self.data)[0])

    def test_check_if_scraper_info_is_valid_missing_scraper_name(self):
        del self.data['scraper_name']
        self.assertFalse(check_if_scraper_info_is_valid(self.data)[0])

    def test_check_if_scraper_info_is_valid_missing_scraper_icon(self):
        del self.data['scraper_icon']
        self.assertFalse(check_if_scraper_info_is_valid(self.data)[0])

    def test_check_if_scraper_info_scraper_name_already_exists(self):
        self.data['scraper_name'] = 'newScraper'
        self.assertFalse(check_if_scraper_info_is_valid(self.data)[0])
