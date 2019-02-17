from django.http import HttpRequest
from django.test import TestCase
from users.models import User, Scrapers
from claims.models import Claim
from comments.models import Comment
from users.views import check_if_user_exists_by_user_id, get_username_by_user_id, add_all_scrapers, \
    get_all_scrapers_ids, get_random_claims_from_scrapers
import json


class UsersTest(TestCase):
    def setUp(self):
        self.user_1 = User(username="User1", email='user1@gmail.com')
        self.user_2 = User(username="User2", email='user2@gmail.com')
        self.user_3 = User(username="User3", email='user3@gmail.com')
        self.user_1.save()
        self.user_2.save()
        self.user_3.save()

    def tearDown(self):
        pass

    def test_check_if_user_exists_by_user_id(self):
        self.assertTrue(check_if_user_exists_by_user_id(1))
        self.assertTrue(check_if_user_exists_by_user_id(2))
        self.assertTrue(check_if_user_exists_by_user_id(3))

    def test_check_if_user_exists_by_invalid_user_id(self):
        self.assertFalse(check_if_user_exists_by_user_id(4))

    def test_get_username_by_user_id(self):
        self.assertTrue(get_username_by_user_id(1) == self.user_1.username)
        self.assertTrue(get_username_by_user_id(2) == self.user_2.username)
        self.assertTrue(get_username_by_user_id(3) == self.user_3.username)

    def test_get_username_by_user_id_invalid_user(self):
        self.assertTrue(get_username_by_user_id(4) is None)

    def test_add_all_scrapers(self):
        add_all_scrapers()
        self.assertTrue(check_if_user_exists_by_user_id(4))
        self.assertTrue(check_if_user_exists_by_user_id(5))
        self.assertTrue(check_if_user_exists_by_user_id(6))
        self.assertTrue(check_if_user_exists_by_user_id(7))
        self.assertTrue(check_if_user_exists_by_user_id(8))
        self.assertTrue(check_if_user_exists_by_user_id(9))
        self.assertTrue(check_if_user_exists_by_user_id(10))
        self.assertTrue(check_if_user_exists_by_user_id(11))
        self.assertTrue(get_username_by_user_id(4) == 'Snopes')
        self.assertTrue(get_username_by_user_id(5) == 'Polygraph')
        self.assertTrue(get_username_by_user_id(6) == 'TruthOrFiction')
        self.assertTrue(get_username_by_user_id(7) == 'Politifact')
        self.assertTrue(get_username_by_user_id(8) == 'GossipCop')
        self.assertTrue(get_username_by_user_id(9) == 'ClimateFeedback')
        self.assertTrue(get_username_by_user_id(10) == 'FactScan')
        self.assertTrue(get_username_by_user_id(11) == 'AfricaCheck')

    def test_get_all_scrapers_ids(self):
        import json
        add_all_scrapers()
        scrapers_ids = json.loads(get_all_scrapers_ids(HttpRequest()).content.decode('utf-8'))
        self.assertTrue(scrapers_ids == {'Snopes': 4,
                                         'Polygraph': 5,
                                         'TruthOrFiction': 6,
                                         'Politifact': 7,
                                         'GossipCop': 8,
                                         'ClimateFeedback': 9,
                                         'FactScan': 10,
                                         'AfricaCheck': 11,
                                         })

    def test_get_random_claims_from_scrapers_not_many_claims(self):
        from claims.models import Claim
        from comments.models import Comment
        scrapers_comments = {}
        add_all_scrapers()
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
        add_all_scrapers()
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