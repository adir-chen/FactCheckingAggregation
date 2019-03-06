from django.http import HttpRequest, QueryDict, Http404
from django.test import TestCase
from users.models import User, Scrapers, Users_Reputations
from claims.models import Claim
from comments.models import Comment
from users.views import check_if_user_exists_by_user_id, get_username_by_user_id, add_all_scrapers, \
    get_all_scrapers_ids, get_all_scrapers_ids_arr, get_random_claims_from_scrapers, add_scraper_guide, add_new_scraper, \
    check_if_scraper_info_is_valid, update_reputation_for_user
import json
import random
import datetime


class UsersTest(TestCase):
    def setUp(self):
        self.user_1 = User(username="User1", email='user1@gmail.com')
        self.user_2 = User(username="User2", email='user2@gmail.com')
        self.user_3 = User(username="User3", email='user3@gmail.com')
        self.new_scraper = User(username="newScraper")
        self.user_1.save()
        self.user_2.save()
        self.user_3.save()
        self.new_scraper.save()
        self.admin = User.objects.create_superuser(username='admin',
                                                   email='admin@gmail.com',
                                                   password='admin')
        self.init_rep = 1
        self.rep = random.randint(1, 80)
        self.user_1_rep = Users_Reputations(user_id=self.user_1, user_rep=self.rep)
        self.user_1_rep.save()
        self.all_users_dict = {1: self.user_1,
                               2: self.user_2,
                               3: self.user_3,
                               4: self.new_scraper,
                               5: self.admin}

        self.num_of_saved_users = 5
        self.post_request = HttpRequest()
        self.post_request.method = 'POST'
        password = User.objects.make_random_password()
        self.new_scraper_details = {'scraper_name': 'newScraper_2',
                                    'scraper_password': str(password),
                                    'scraper_password_2': str(password),
                                    'scraper_icon': 'newScraperIcon',
                                    'scraper_true_labels': '',
                                    'scraper_false_labels': ''}

    def tearDown(self):
        pass

    def test_check_if_user_exists_by_user_id(self):
        for i in range(self.num_of_saved_users):
            self.assertTrue(check_if_user_exists_by_user_id(i + 1))

    def test_check_if_user_exists_by_invalid_user_id(self):
        self.assertFalse(check_if_user_exists_by_user_id(self.num_of_saved_users + 1))
        self.assertFalse(check_if_user_exists_by_user_id(self.num_of_saved_users + random.randint(1, 10)))

    def test_get_username_by_user_id(self):
        for user_id, user in self.all_users_dict.items():
            self.assertTrue(get_username_by_user_id(user_id) == user.username)

    def test_get_username_by_user_id_invalid_user(self):
        self.assertTrue(get_username_by_user_id(self.num_of_saved_users + 1) is None)
        self.assertTrue(get_username_by_user_id(self.num_of_saved_users + random.randint(1, 10)) is None)

    def test_add_all_scrapers(self):
        self.post_request.user = self.admin
        add_all_scrapers(self.post_request)
        self.assertTrue(check_if_user_exists_by_user_id(self.num_of_saved_users + 1))
        self.assertTrue(check_if_user_exists_by_user_id(self.num_of_saved_users + 2))
        self.assertTrue(check_if_user_exists_by_user_id(self.num_of_saved_users + 3))
        self.assertTrue(check_if_user_exists_by_user_id(self.num_of_saved_users + 4))
        self.assertTrue(check_if_user_exists_by_user_id(self.num_of_saved_users + 5))
        self.assertTrue(check_if_user_exists_by_user_id(self.num_of_saved_users + 6))
        self.assertTrue(check_if_user_exists_by_user_id(self.num_of_saved_users + 7))
        self.assertTrue(check_if_user_exists_by_user_id(self.num_of_saved_users + 8))
        self.assertTrue(get_username_by_user_id(self.num_of_saved_users + 1) == 'Snopes')
        self.assertTrue(get_username_by_user_id(self.num_of_saved_users + 2) == 'Polygraph')
        self.assertTrue(get_username_by_user_id(self.num_of_saved_users + 3) == 'TruthOrFiction')
        self.assertTrue(get_username_by_user_id(self.num_of_saved_users + 4) == 'Politifact')
        self.assertTrue(get_username_by_user_id(self.num_of_saved_users + 5) == 'GossipCop')
        self.assertTrue(get_username_by_user_id(self.num_of_saved_users + 6) == 'ClimateFeedback')
        self.assertTrue(get_username_by_user_id(self.num_of_saved_users + 7) == 'FactScan')
        self.assertTrue(get_username_by_user_id(self.num_of_saved_users + 8) == 'AfricaCheck')

    def test_add_all_scrapers_user_not_admin(self):
        self.post_request.user = self.user_1
        self.assertRaises(Http404, add_all_scrapers, self.post_request)
        self.assertFalse(check_if_user_exists_by_user_id(self.num_of_saved_users + 1))
        self.assertFalse(check_if_user_exists_by_user_id(self.num_of_saved_users + 2))
        self.assertFalse(check_if_user_exists_by_user_id(self.num_of_saved_users + 3))
        self.assertFalse(check_if_user_exists_by_user_id(self.num_of_saved_users + 4))
        self.assertFalse(check_if_user_exists_by_user_id(self.num_of_saved_users + 5))
        self.assertFalse(check_if_user_exists_by_user_id(self.num_of_saved_users + 6))
        self.assertFalse(check_if_user_exists_by_user_id(self.num_of_saved_users + 7))
        self.assertFalse(check_if_user_exists_by_user_id(self.num_of_saved_users + 8))
        self.assertFalse(get_username_by_user_id(self.num_of_saved_users + 1) == 'Snopes')
        self.assertFalse(get_username_by_user_id(self.num_of_saved_users + 2) == 'Polygraph')
        self.assertFalse(get_username_by_user_id(self.num_of_saved_users + 3) == 'TruthOrFiction')
        self.assertFalse(get_username_by_user_id(self.num_of_saved_users + 4) == 'Politifact')
        self.assertFalse(get_username_by_user_id(self.num_of_saved_users + 5) == 'GossipCop')
        self.assertFalse(get_username_by_user_id(self.num_of_saved_users + 6) == 'ClimateFeedback')
        self.assertFalse(get_username_by_user_id(self.num_of_saved_users + 7) == 'FactScan')
        self.assertFalse(get_username_by_user_id(self.num_of_saved_users + 8) == 'AfricaCheck')

    def test_add_all_scrapers_twice(self):
        self.post_request.user = self.admin
        self.assertTrue(add_all_scrapers(self.post_request).status_code == 200)
        self.assertRaises(Http404, add_all_scrapers, self.post_request)

    def test_get_all_scrapers_ids(self):
        import json
        self.post_request.user = self.admin
        add_all_scrapers(self.post_request)
        scrapers_ids = json.loads(get_all_scrapers_ids(HttpRequest()).content.decode('utf-8'))
        self.assertTrue(scrapers_ids == {'Snopes': self.num_of_saved_users + 1,
                                         'Polygraph': self.num_of_saved_users + 2,
                                         'TruthOrFiction': self.num_of_saved_users + 3,
                                         'Politifact': self.num_of_saved_users + 4,
                                         'GossipCop': self.num_of_saved_users + 5,
                                         'ClimateFeedback': self.num_of_saved_users + 6,
                                         'FactScan': self.num_of_saved_users + 7,
                                         'AfricaCheck': self.num_of_saved_users + 8,
                                         })

    def test_get_all_scrapers_ids_arr(self):
        self.post_request.user = self.admin
        add_all_scrapers(self.post_request)
        scrapers_ids = [(i+6) for i in range(8)]
        self.assertEqual(scrapers_ids, get_all_scrapers_ids_arr())

    def test_get_random_claims_from_scrapers_not_many_claims(self):
        from claims.models import Claim
        from comments.models import Comment
        scrapers_comments = {}
        self.post_request.user = self.admin
        add_all_scrapers(self.post_request)
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
                              verdict_date=datetime.date.today() - datetime.timedelta(days=random.randint(0, 10)),
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
                    'verdict_date': str(scrapers_comments[scraper_name][1].verdict_date),
                    'category': scrapers_comments[scraper_name][0].category,
                    'label':  scrapers_comments[scraper_name][1].label})

    def test_get_random_claims_from_scrapers_many_claims(self):
        scrapers_comments = {}
        self.post_request.user = self.admin
        add_all_scrapers(self.post_request)
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
                                verdict_date=datetime.date.today() - datetime.timedelta(days=random.randint(0, 10)),
                                label='label' + str(i + 1))
            comment_2 = Comment(claim_id=claim_2.id,
                                user_id=Scrapers.objects.filter(scraper_name=scrapers_names[i])[0].scraper_id.id,
                                title='title_' + str(i + 2),
                                description='description_' + str(i + 2),
                                url='url_' + str(i + 2),
                                verdict_date=datetime.date.today() - datetime.timedelta(days=random.randint(0, 10)),
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
                                                'verdict_date': str(scrapers_comments[scraper_name][1].verdict_date),
                                                'category': scrapers_comments[scraper_name][0].category,
                                                'label':  scrapers_comments[scraper_name][1].label})

    def test_add_scraper_guide(self):
        self.assertTrue(add_scraper_guide(HttpRequest()).status_code == 200)

    def test_add_new_scraper_valid(self):
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.new_scraper_details)
        self.post_request.POST = query_dict
        self.post_request.user = self.admin
        old_length = len(User.objects.all())
        self.assertTrue(add_new_scraper(self.post_request).status_code == 200)
        self.assertTrue(len(User.objects.all()) == old_length + 1)

    def test_add_new_scraper_by_invalid_user(self):
        self.post_request.user = self.user_1
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.new_scraper_details)
        self.post_request.POST = query_dict
        old_length = len(User.objects.all())
        self.assertRaises(Http404, add_new_scraper, self.post_request)
        self.assertTrue(len(User.objects.all()) == old_length)

    def test_add_existing_scraper(self):
        self.new_scraper_details['scraper_name'] = 'newScraper'
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.new_scraper_details)
        self.post_request.POST = query_dict
        old_length = len(User.objects.all())
        self.assertRaises(Exception, add_new_scraper, self.post_request)
        self.assertTrue(len(User.objects.all()) == old_length)

    def test_add_new_scraper_missing_args(self):
        for i in range(10):
            dict_copy = self.new_scraper_details.copy()
            args_to_remove = []
            for j in range(random.randint(1, len(self.new_scraper_details.keys()) - 1)):
                args_to_remove.append(list(self.new_scraper_details.keys())[j])
            for j in range(len(args_to_remove)):
                del self.new_scraper_details[args_to_remove[j]]
            len_users = len(User.objects.all())
            query_dict = QueryDict('', mutable=True)
            query_dict.update(self.new_scraper_details)
            self.post_request.POST = query_dict
            self.post_request.user = self.admin
            self.assertRaises(Exception, add_new_scraper, self.post_request)
            self.assertTrue(len(User.objects.all()) == len_users)
            self.new_scraper_details = dict_copy.copy()

    def test_add_new_scraper_get(self):
        request = HttpRequest()
        request.user = self.user_2
        request.method = 'GET'
        self.assertRaises(Http404, add_new_scraper, request)

    def test_check_if_scraper_info_is_valid(self):
        self.assertTrue(check_if_scraper_info_is_valid(self.new_scraper_details)[0])

    def test_check_if_scraper_info_is_valid_missing_scraper_name(self):
        del self.new_scraper_details['scraper_name']
        self.assertFalse(check_if_scraper_info_is_valid(self.new_scraper_details)[0])

    def test_check_if_scraper_info_is_valid_missing_scraper_password(self):
        del self.new_scraper_details['scraper_password']
        self.assertFalse(check_if_scraper_info_is_valid(self.new_scraper_details)[0])

    def test_check_if_scraper_info_is_valid_missing_scraper_password_2(self):
        del self.new_scraper_details['scraper_password_2']
        self.assertFalse(check_if_scraper_info_is_valid(self.new_scraper_details)[0])

    def test_check_if_scraper_info_is_valid_passwords_not_match(self):
        self.new_scraper_details['scraper_password_2'] = random.randint(0, 10)
        self.assertFalse(check_if_scraper_info_is_valid(self.new_scraper_details)[0])

    def test_check_if_scraper_info_is_valid_missing_scraper_icon(self):
        del self.new_scraper_details['scraper_icon']
        self.assertFalse(check_if_scraper_info_is_valid(self.new_scraper_details)[0])

    def test_check_if_scraper_info_scraper_name_already_exists(self):
        self.new_scraper_details['scraper_name'] = 'newScraper'
        self.assertFalse(check_if_scraper_info_is_valid(self.new_scraper_details)[0])

    def test_update_reputation_for_user_with_reputation_earn_points(self):
        update_reputation_for_user(self.user_1.id, True, 1)
        user_rep = Users_Reputations.objects.filter(user_id=self.user_1).first()
        self.assertTrue(user_rep.user_rep == self.rep + 1)

    def test_update_reputation_for_user_with_reputation_earn_many_points(self):
        for i in range(100):
            update_reputation_for_user(self.user_1.id, True, 1)
        user_rep = Users_Reputations.objects.filter(user_id=self.user_1).first()
        self.assertTrue(user_rep.user_rep == 100)

    def test_update_reputation_for_user_with_reputation_lost_points(self):
        update_reputation_for_user(self.user_1.id, False, 1)
        user_rep = Users_Reputations.objects.filter(user_id=self.user_1).first()
        self.assertTrue(user_rep.user_rep == self.rep - 1)

    def test_update_reputation_for_user_with_reputation_lost_many_points(self):
        for i in range(100):
            update_reputation_for_user(self.user_1.id, False, 1)
        user_rep = Users_Reputations.objects.filter(user_id=self.user_1).first()
        self.assertTrue(user_rep.user_rep == 1)

    def test_update_reputation_for_user_without_reputation_earn_points(self):
        update_reputation_for_user(self.user_2.id, True, 1)
        user_rep = Users_Reputations.objects.filter(user_id=self.user_2).first()
        self.assertTrue(user_rep.user_rep == self.init_rep + 1)

    def test_update_reputation_for_user_without_reputation_earn_many_points(self):
        for i in range(100):
            update_reputation_for_user(self.user_2.id, True, 1)
        user_rep = Users_Reputations.objects.filter(user_id=self.user_2).first()
        self.assertTrue(user_rep.user_rep == 100)

    def test_update_reputation_for_user_without_reputation_lost_points(self):
        update_reputation_for_user(self.user_2.id, False, 1)
        user_rep = Users_Reputations.objects.filter(user_id=self.user_2).first()
        self.assertTrue(user_rep.user_rep == 1)

    def test_update_reputation_for_user_without_reputation_lost_many_points(self):
        for i in range(100):
            update_reputation_for_user(self.user_2.id, False, 1)
        user_rep = Users_Reputations.objects.filter(user_id=self.user_2).first()
        self.assertTrue(user_rep.user_rep == 1)

    def test_update_reputation_for_user_invalid_user(self):
        self.assertRaises(Exception, update_reputation_for_user,
                          self.num_of_saved_users + random.randint(1, 10),
                          False, random.randint(1, 20))
        self.assertRaises(Exception, update_reputation_for_user,
                          self.num_of_saved_users + random.randint(1, 10),
                          True, random.randint(1, 20))
