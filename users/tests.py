from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpRequest, QueryDict, Http404
from django.core.exceptions import PermissionDenied
from django.utils.datastructures import MultiValueDict
from django.test import TestCase
from notifications.models import Notification
from notifications.signals import notify
from users.models import User, Scrapers, Users_Reputations, Users_Images
from claims.models import Claim
from comments.models import Comment
from users.views import check_if_user_exists_by_user_id, get_username_by_user_id, get_user_reputation, add_all_scrapers, \
    get_all_scrapers_ids, get_all_scrapers_ids_arr, get_random_claims_from_scrapers, add_scraper_guide, add_new_scraper, \
    check_if_scraper_info_is_valid, update_reputation_for_user, user_page, get_scraper_url, \
    add_true_label_to_scraper, delete_true_label_from_scraper, add_false_label_to_scraper, \
    delete_false_label_from_scraper, check_if_scraper_new_label_is_valid, \
    check_if_scraper_label_delete_is_valid, check_if_scraper_labels_already_exist, \
    update_scrapers_comments_verdicts, check_if_user_is_scraper, upload_user_img, notifications_page, read_all_notifications, read_notification, \
    delete_notification, check_if_notification_is_valid, change_username, check_if_user_info_is_valid
import json
import random
import datetime


class UsersTest(TestCase):
    def setUp(self):
        self.user_1 = User(username="User1", email='user1@gmail.com')
        self.user_2 = User(username="User2", email='user2@gmail.com')
        self.user_3 = User(username="User3", email='user3@gmail.com')
        self.user_1.save()
        self.user_2.save()
        self.user_3.save()
        self.new_scraper = User(username="newScraper")
        self.new_scraper.save()
        self.admin = User.objects.create_superuser(username='admin',
                                                   email='admin@gmail.com',
                                                   password='admin')
        self.init_rep = 1
        self.rep = random.randint(2, 80)
        self.user_1_rep = Users_Reputations(user=self.user_1, reputation=self.rep)
        self.user_1_rep.save()
        self.all_users_dict = {1: self.user_1,
                               2: self.user_2,
                               3: self.user_3,
                               4: self.new_scraper,
                               5: self.admin}

        self.num_of_saved_users = 5
        self.post_request = HttpRequest()
        self.post_request.method = 'POST'
        self.get_request = HttpRequest()
        self.get_request.method = 'GET'
        password = User.objects.make_random_password()
        self.url = 'https://www.google.com'
        self.new_scraper_details = {'scraper_name': 'newScraper_2',
                                    'scraper_password': str(password),
                                    'scraper_password_2': str(password),
                                    'scraper_url': self.url,
                                    'scraper_true_labels': '',
                                    'scraper_false_labels': ''}
        self.new_label_for_scraper = {'scraper_id': self.new_scraper.id}
        self.delete_label_for_scraper = MultiValueDict({
            'scraper_id': str(self.new_scraper.id)})

        self.claim_1 = Claim(user=self.new_scraper,
                             claim='claim1',
                             category='category1',
                             tags='tag1,tag2,tag3',
                             authenticity_grade=0,
                             image_src='image1')
        self.claim_1.save()
        self.num_of_saved_claims = 1
        self.comment_1 = Comment(claim_id=self.claim_1.id,
                                 user=self.claim_1.user,
                                 title='title1',
                                 description='description1',
                                 url='http://url1',
                                 verdict_date=datetime.date.today() - datetime.timedelta(days=random.randint(0, 10)),
                                 system_label='Unknown')

        self.comment_1.save()
        self.num_of_saved_comments = 1

        notify.send(self.user_1, recipient=self.user_2, verb='some msg')
        self.notification = Notification.objects.get(recipient=self.user_2)
        self.num_of_saved_notifications = 1
        self.notification_info = {'notification_id': self.notification.id,
                                  'user_id': self.user_2.id}
        self.user_info = {'new_username': "new_username",
                          'user_id': self.user_1.id,
                          'request_user_id': self.user_1.id,
                          'is_superuser': False}
        self.image_file_test = SimpleUploadedFile(name="profile_default_image_test.jpg", content=open(
            'users/profile_default_image_test.jpg', 'rb').read(), content_type='image/jpeg')
        self.image_file_test_invalid = SimpleUploadedFile(name="profile_default_image_test_invalid.jpg", content=open(
            'users/profile_default_image_test_invalid.jpg', 'rb').read(), content_type='image/jpeg')
        self.error_code = 404

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

    def test_get_user_reputation(self):
        self.assertTrue(get_user_reputation(self.user_1.id) == self.rep)

    def test_get_user_reputation_invalid_user(self):
        response = get_user_reputation(self.num_of_saved_users + 1)
        self.assertTrue(response.status_code == self.error_code)

    def test_get_user_reputation_for_valid_user_without_reputation(self):
        self.assertTrue(get_user_reputation(self.user_2.id) == 1)

    def test_add_all_scrapers(self):
        self.get_request.user = self.admin
        add_all_scrapers(self.get_request)
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
        self.assertRaises(PermissionDenied, add_all_scrapers, self.post_request)
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
        self.get_request.user = self.admin
        self.assertTrue(add_all_scrapers(self.get_request).status_code == 200)
        self.assertRaises(Http404, add_all_scrapers, self.get_request)

    def test_get_all_scrapers_ids(self):
        import json
        self.get_request.user = self.admin
        self.assertTrue(add_all_scrapers(self.get_request).status_code == 200)
        self.get_request.user = self.admin
        scrapers_ids = json.loads(get_all_scrapers_ids(self.get_request).content.decode('utf-8'))
        self.assertTrue(scrapers_ids == {'Snopes': self.num_of_saved_users + 1,
                                         'Polygraph': self.num_of_saved_users + 2,
                                         'TruthOrFiction': self.num_of_saved_users + 3,
                                         'Politifact': self.num_of_saved_users + 4,
                                         'GossipCop': self.num_of_saved_users + 5,
                                         'ClimateFeedback': self.num_of_saved_users + 6,
                                         'FactScan': self.num_of_saved_users + 7,
                                         'AfricaCheck': self.num_of_saved_users + 8,
                                         'CNN': self.num_of_saved_users + 9,
                                         })

    def test_get_all_scrapers_ids_invalid_request(self):
        self.get_request.user = self.admin
        self.assertTrue(add_all_scrapers(self.get_request).status_code == 200)
        self.post_request.user = self.admin
        self.assertRaises(PermissionDenied, get_all_scrapers_ids, self.post_request)

    def test_get_all_scrapers_ids_arr(self):
        self.get_request.user = self.admin
        self.assertTrue(add_all_scrapers(self.get_request).status_code == 200)
        scrapers_ids = [(i+6) for i in range(9)]
        self.assertEqual(scrapers_ids, get_all_scrapers_ids_arr())

    def test_get_random_claims_from_scrapers_not_many_claims(self):
        from claims.models import Claim
        from comments.models import Comment
        scrapers_comments = {}
        self.get_request.user = self.admin
        add_all_scrapers(self.get_request)
        scrapers_names = ['Snopes', 'Polygraph', 'TruthOrFiction', 'Politifact', 'GossipCop',
                          'ClimateFeedback', 'FactScan', 'AfricaCheck', 'CNN']
        for i in range(len(scrapers_names)):
            claim = Claim(user_id=Scrapers.objects.filter(scraper_name=scrapers_names[i])[0].scraper.id,
                          claim='Sniffing rosemary increases human memory by up to 75 percent',
                          category='Science',
                          tags="sniffing human memory",
                          authenticity_grade=0)
            claim.save()
            comment = Comment(claim_id=claim.id,
                              user_id=Scrapers.objects.filter(scraper_name=scrapers_names[i])[0].scraper.id,
                              title='title_' + str(i + 1),
                              description='description_' + str(i + 1),
                              url='http://url_' + str(i + 1) +'/',
                              verdict_date=datetime.date.today() - datetime.timedelta(days=random.randint(0, 10)),
                              label='label' + str(i + 1))
            comment.save()
            scrapers_comments[scrapers_names[i]] = [claim, comment]
        import json
        self.get_request.user = self.admin
        scrapers_comments_val = json.loads(get_random_claims_from_scrapers(self.get_request).content.decode('utf-8'))
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
        self.get_request.user = self.admin
        self.assertTrue(add_all_scrapers(self.get_request).status_code == 200)
        scrapers_names = ['Snopes', 'Polygraph', 'TruthOrFiction', 'Politifact', 'GossipCop',
                          'ClimateFeedback', 'FactScan', 'AfricaCheck', 'CNN']
        for i in range(len(scrapers_names)):
            claim_1 = Claim(user_id=Scrapers.objects.filter(scraper_name=scrapers_names[i])[0].scraper.id,
                            claim='Sniffing rosemary increases human memory by up to 75 percent' + str(i),
                            category='Science',
                            tags="sniffing human memory",
                            authenticity_grade=0)
            claim_2 = Claim(user_id=Scrapers.objects.filter(scraper_name=scrapers_names[i])[0].scraper.id,
                            claim='Sniffing rosemary increases human memory by up to 75 percent' + str(i + 1),
                            category='Science',
                            tags="sniffing human memory",
                            authenticity_grade=0)
            claim_2.save()
            claim_1.save()
            comment_1 = Comment(claim_id=claim_1.id,
                                user_id=Scrapers.objects.filter(scraper_name=scrapers_names[i])[0].scraper.id,
                                title='title_' + str(i + 1),
                                description='description_' + str(i + 1),
                                url='http://url_' + str(i + 1) + '/',
                                verdict_date=datetime.date.today() - datetime.timedelta(days=random.randint(0, 10)),
                                label='label' + str(i + 1))
            comment_2 = Comment(claim_id=claim_2.id,
                                user_id=Scrapers.objects.filter(scraper_name=scrapers_names[i])[0].scraper.id,
                                title='title_' + str(i + 2),
                                description='description_' + str(i + 2),
                                url='http://url_' + str(i + 2) + '/',
                                verdict_date=datetime.date.today() - datetime.timedelta(days=random.randint(0, 10)),
                                label='label' + str(i + 2))
            comment_2.save()
            comment_1.save()
            scrapers_comments[scrapers_names[i]] = [claim_1, comment_1]
        self.get_request.user = self.admin
        scrapers_comments_val = json.loads(get_random_claims_from_scrapers(self.get_request).content.decode('utf-8'))
        for scraper_name, scraper_comment in scrapers_comments_val.items():
            scraper_dict = {'title': scrapers_comments[scraper_name][1].title,
                                                'claim': scrapers_comments[scraper_name][0].claim,
                                                'description': scrapers_comments[scraper_name][1].description,
                                                'url': scrapers_comments[scraper_name][1].url,
                                                'verdict_date': str(scrapers_comments[scraper_name][1].verdict_date),
                                                'category': scrapers_comments[scraper_name][0].category,
                                                'label':  scrapers_comments[scraper_name][1].label}
            self.assertTrue(scraper_comment == scraper_dict)

    def test_get_random_claims_from_scrapers_not_admin_user(self):
        self.get_request.user = self.admin
        self.assertTrue(add_all_scrapers(self.get_request).status_code == 200)
        self.get_request.user = self.user_1
        self.assertRaises(PermissionDenied, get_random_claims_from_scrapers, self.get_request)

    def test_get_random_claims_from_scrapers_invalid_request(self):
        self.get_request.user = self.admin
        self.assertTrue(add_all_scrapers(self.get_request).status_code == 200)
        self.post_request.user = self.user_1
        self.assertRaises(PermissionDenied, get_random_claims_from_scrapers, self.post_request)

    def test_add_scraper_guide(self):
        self.get_request.user = self.admin
        self.assertTrue(add_scraper_guide(self.get_request).status_code == 200)

    def test_add_scraper_guide_by_not_admin_user(self):
        self.get_request.user = self.user_1
        self.assertRaises(PermissionDenied, add_scraper_guide, self.get_request)

    def test_add_scraper_guide_invalid_request(self):
        self.post_request.user = self.admin
        self.assertRaises(PermissionDenied, add_scraper_guide, self.post_request)

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
        self.assertRaises(PermissionDenied, add_new_scraper, self.post_request)
        self.assertTrue(len(User.objects.all()) == old_length)

    def test_add_existing_scraper(self):
        self.new_scraper_details['scraper_name'] = 'newScraper'
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.new_scraper_details)
        self.post_request.POST = query_dict
        self.post_request.user = self.admin
        old_length = len(User.objects.all())
        response = add_new_scraper(self.post_request)
        self.assertTrue(response.status_code == self.error_code)
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
            response = add_new_scraper(self.post_request)
            self.assertTrue(response.status_code == self.error_code)
            self.assertTrue(len(User.objects.all()) == len_users)
            self.new_scraper_details = dict_copy.copy()

    def test_add_new_scraper_get(self):
        request = HttpRequest()
        request.user = self.user_2
        request.method = 'GET'
        self.assertRaises(PermissionDenied, add_new_scraper, request)

    def test_check_if_scraper_info_is_valid(self):
        self.assertTrue(check_if_scraper_info_is_valid(self.new_scraper_details)[0])

    def test_check_if_scraper_info_is_valid_missing_scraper_name(self):
        del self.new_scraper_details['scraper_name']
        self.assertFalse(check_if_scraper_info_is_valid(self.new_scraper_details)[0])

    def test_check_if_scraper_info_is_valid_missing_scraper_url(self):
        del self.new_scraper_details['scraper_url']
        self.assertFalse(check_if_scraper_info_is_valid(self.new_scraper_details)[0])

    def test_check_if_scraper_info_is_valid_invalid_scraper_url(self):
        self.new_scraper_details['scraper_url'] = 'invalid_url'
        self.assertFalse(check_if_scraper_info_is_valid(self.new_scraper_details)[0])

    def test_check_if_scraper_info_is_valid_invalid_format_scrapers_true_labels(self):
        self.new_scraper_details['scraper_true_labels'] = 'true,  mostly true'
        self.assertFalse(check_if_scraper_info_is_valid(self.new_scraper_details)[0])
        self.new_scraper_details['scraper_true_labels'] = 'true,,mostly true'
        self.assertFalse(check_if_scraper_info_is_valid(self.new_scraper_details)[0])
        self.new_scraper_details['scraper_true_labels'] = ',true, mostly true'
        self.assertFalse(check_if_scraper_info_is_valid(self.new_scraper_details)[0])
        self.new_scraper_details['scraper_true_labels'] = 'true,mostly true,'
        self.assertFalse(check_if_scraper_info_is_valid(self.new_scraper_details)[0])

    def test_check_if_scraper_info_is_valid_invalid_format_scrapers_false_labels(self):
        self.new_scraper_details['scraper_false_labels'] = 'false,  mostly false'
        self.assertFalse(check_if_scraper_info_is_valid(self.new_scraper_details)[0])
        self.new_scraper_details['scraper_false_labels'] = 'false,,mostly false'
        self.assertFalse(check_if_scraper_info_is_valid(self.new_scraper_details)[0])
        self.new_scraper_details['scraper_false_labels'] = ',false, mostly false'
        self.assertFalse(check_if_scraper_info_is_valid(self.new_scraper_details)[0])
        self.new_scraper_details['scraper_false_labels'] = 'false,mostly false,'
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

    def test_check_if_scraper_info_is_valid_scraper_name_already_exists(self):
        self.new_scraper_details['scraper_name'] = 'newScraper'
        self.assertFalse(check_if_scraper_info_is_valid(self.new_scraper_details)[0])

    def test_check_if_scraper_info_is_valid_scraper_name_invalid(self):
        self.new_scraper_details['scraper_name'] = 'новый'
        self.assertFalse(check_if_scraper_info_is_valid(self.new_scraper_details)[0])

    def test_check_if_scraper_info_is_valid_scraper_true_labels_invalid(self):
        self.new_scraper_details['scraper_true_labels'] = 'правда'
        self.assertFalse(check_if_scraper_info_is_valid(self.new_scraper_details)[0])

    def test_check_if_scraper_info_is_valid_scraper_false_labels_invalid(self):
        self.new_scraper_details['scraper_false_labels'] = 'തെറ്റായ'
        self.assertFalse(check_if_scraper_info_is_valid(self.new_scraper_details)[0])

    def test_update_reputation_for_user_with_reputation_earn_points(self):
        update_reputation_for_user(self.user_1.id, True, 1)
        user_rep = Users_Reputations.objects.filter(user=self.user_1).first()
        self.assertTrue(user_rep.reputation == self.rep + 1)

    def test_update_reputation_for_user_with_reputation_earn_many_points(self):
        for i in range(100):
            update_reputation_for_user(self.user_1.id, True, 1)
        user_rep = Users_Reputations.objects.filter(user=self.user_1).first()
        self.assertTrue(user_rep.reputation == 100)

    def test_update_reputation_for_user_with_reputation_lost_points(self):
        update_reputation_for_user(self.user_1.id, False, 1)
        user_rep = Users_Reputations.objects.filter(user_id=self.user_1).first()
        self.assertTrue(user_rep.reputation == self.rep - 1)

    def test_update_reputation_for_user_with_reputation_lost_many_points(self):
        for i in range(100):
            update_reputation_for_user(self.user_1.id, False, 1)
        user_rep = Users_Reputations.objects.filter(user=self.user_1).first()
        self.assertTrue(user_rep.reputation == 1)

    def test_update_reputation_for_user_without_reputation_earn_points(self):
        update_reputation_for_user(self.user_2.id, True, 1)
        user_rep = Users_Reputations.objects.filter(user=self.user_2).first()
        self.assertTrue(user_rep.reputation == self.init_rep + 1)

    def test_update_reputation_for_user_without_reputation_earn_many_points(self):
        for i in range(100):
            update_reputation_for_user(self.user_2.id, True, 1)
        user_rep = Users_Reputations.objects.filter(user=self.user_2).first()
        self.assertTrue(user_rep.reputation == 100)

    def test_update_reputation_for_user_without_reputation_lost_points(self):
        update_reputation_for_user(self.user_2.id, False, 1)
        user_rep = Users_Reputations.objects.filter(user=self.user_2).first()
        self.assertTrue(user_rep.reputation == 1)

    def test_update_reputation_for_user_without_reputation_lost_many_points(self):
        for i in range(100):
            update_reputation_for_user(self.user_2.id, False, 1)
        user_rep = Users_Reputations.objects.filter(user=self.user_2).first()
        self.assertTrue(user_rep.reputation == 1)

    def test_update_reputation_for_user_invalid_user(self):
        response = update_reputation_for_user(self.num_of_saved_users + random.randint(1, 10),
                                              False, random.randint(1, 20))
        self.assertTrue(response.status_code == self.error_code)

        response = update_reputation_for_user(self.num_of_saved_users + random.randint(1, 10),
                                              True, random.randint(1, 20))
        self.assertTrue(response.status_code == self.error_code)

    def test_user_page_with_claim_and_comment(self):
        claim = Claim(user_id=self.user_1.id,
                      claim='claim1',
                      category='category1',
                      tags='tag1,tag2,tag3',
                      authenticity_grade=0)
        claim.save()
        comment = Comment(claim_id=claim.id,
                          user_id=self.user_1.id,
                          title='title1',
                          description='description1',
                          url='http://url1/',
                          tags='tag1',
                          verdict_date=datetime.date.today() - datetime.timedelta(days=random.randint(1, 10)),
                          label='label1')
        comment.save()
        self.get_request.user = self.user_1
        self.assertTrue(user_page(self.get_request, self.user_1.id).status_code == 200)

    def test_user_page_with_claim_only(self):
        claim = Claim(user_id=self.user_1.id,
                      claim='claim1',
                      category='category1',
                      tags='tag1,tag2,tag3',
                      authenticity_grade=0)
        claim.save()
        self.get_request.user = self.user_1
        self.assertTrue(user_page(self.get_request, self.user_1.id).status_code == 200)

    def test_user_page_with_comment_only(self):
        claim = Claim(user_id=self.user_2.id,
                      claim='claim1',
                      category='category1',
                      tags='tag1,tag2,tag3',
                      authenticity_grade=0)
        claim.save()
        comment = Comment(claim_id=claim.id,
                          user_id=self.user_1.id,
                          title='title1',
                          description='description1',
                          url='http://url1/',
                          tags='tag1',
                          verdict_date=datetime.date.today() - datetime.timedelta(days=random.randint(1, 10)),
                          label='label1')
        comment.save()
        self.get_request.user = self.user_1
        self.assertTrue(user_page(self.get_request, self.user_1.id).status_code == 200)

    def test_user_page_invalid_user(self):
        invalid_user_id = random.randint(self.num_of_saved_users + 1, self.num_of_saved_users + 20)
        self.get_request.user = self.user_1
        self.assertRaises(Http404, user_page, self.get_request, invalid_user_id)

    def test_user_page_invalid_request(self):
        self.post_request.user = self.user_1
        self.assertRaises(PermissionDenied, user_page, self.post_request, self.user_1.id)

    def test_test_get_scraper_url_for_user(self):
        self.assertTrue((get_scraper_url(self.user_1.username)) == '')

    def test_get_scraper_url_for_scraper(self):
        scraper = Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        scraper_url = get_scraper_url(self.new_scraper.username)
        self.assertTrue(scraper_url == '')
        Scrapers.objects.filter(id=scraper.id).update(scraper_url='http://wwww.' + self.new_scraper.username + '.com')
        scraper_url = get_scraper_url(self.new_scraper.username)
        self.assertTrue(scraper_url == 'http://wwww.' + self.new_scraper.username + '.com')

    def test_add_true_label_to_scraper(self):
        Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        random_label = ['accurate', 'correct', 'mostly correct']
        self.new_label_for_scraper['scraper_label'] = random_label[random.randint(0, 2)]
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.new_label_for_scraper)
        self.post_request.POST = query_dict
        self.post_request.user = self.admin
        self.assertTrue(add_true_label_to_scraper(self.post_request).status_code == 200)

    def test_add_true_label_to_scraper_by_user_not_admin(self):
        Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        random_label = ['accurate', 'correct', 'mostly correct']
        self.new_label_for_scraper['scraper_label'] = random_label[random.randint(0, 2)]
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.new_label_for_scraper)
        self.post_request.POST = query_dict
        self.post_request.user = self.user_1
        self.assertRaises(PermissionDenied, add_true_label_to_scraper, self.post_request)

    def test_add_true_label_to_scraper_invalid_request(self):
        Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        random_label = ['accurate', 'correct', 'mostly correct']
        self.new_label_for_scraper['scraper_label'] = random_label[random.randint(0, 2)]
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.new_label_for_scraper)
        self.get_request.GET = query_dict
        self.get_request.user = self.admin
        self.assertRaises(PermissionDenied, add_true_label_to_scraper, self.get_request)

    def test_add_true_label_to_scraper_missing_scraper_id(self):
        Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        random_label = ['accurate', 'correct', 'mostly correct']
        self.new_label_for_scraper['scraper_label'] = random_label[random.randint(0, 2)]
        del self.new_label_for_scraper['scraper_id']
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.new_label_for_scraper)
        self.post_request.POST = query_dict
        self.post_request.user = self.admin
        response = add_true_label_to_scraper(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_add_true_label_to_scraper_missing_scraper_label(self):
        Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.new_label_for_scraper)
        self.post_request.POST = query_dict
        self.post_request.user = self.admin
        response = add_true_label_to_scraper(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_add_true_label_to_scraper_missing_args(self):
        Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        random_label = ['accurate', 'correct', 'mostly correct']
        for i in range(10):
            self.new_label_for_scraper['scraper_label'] = random_label[random.randint(0, 2)]
            dict_copy = self.new_label_for_scraper.copy()
            args_to_remove = []
            for j in range(random.randint(1, len(self.new_label_for_scraper.keys()) - 1)):
                args_to_remove.append(list(self.new_label_for_scraper.keys())[j])
            for j in range(len(args_to_remove)):
                del self.new_label_for_scraper[args_to_remove[j]]
            query_dict = QueryDict('', mutable=True)
            query_dict.update(self.new_label_for_scraper)
            self.post_request.POST = query_dict
            self.post_request.user = self.admin
            response = add_true_label_to_scraper(self.post_request)
            self.assertTrue(response.status_code == self.error_code)
            self.new_label_for_scraper = dict_copy.copy()

    def test_add_true_label_to_scraper_invalid_label(self):
        Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        self.new_label_for_scraper['scraper_label'] = 'সত্য'
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.new_label_for_scraper)
        self.post_request.POST = query_dict
        self.post_request.user = self.admin
        response = add_true_label_to_scraper(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_add_true_label_to_scraper_invalid_scraper_id(self):
        self.new_label_for_scraper['scraper_id'] = self.num_of_saved_users + random.randint(1, 10)
        Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        random_label = ['accurate', 'correct', 'mostly correct']
        self.new_label_for_scraper['scraper_label'] = random_label[random.randint(0, 2)]
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.new_label_for_scraper)
        self.post_request.POST = query_dict
        self.post_request.user = self.admin
        response = add_true_label_to_scraper(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_add_true_label_to_scraper_label_already_exists(self):
        scraper = Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        Scrapers.objects.filter(id=scraper.id).update(true_labels='true,correct,mostly correct')
        random_label = ['true', 'correct', 'mostly correct']
        self.new_label_for_scraper['scraper_label'] = random_label[random.randint(0, 2)]
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.new_label_for_scraper)
        self.post_request.POST = query_dict
        self.post_request.user = self.admin
        response = add_true_label_to_scraper(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_delete_true_label_from_scraper(self):
        scraper = Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        Scrapers.objects.filter(id=scraper.id).update(true_labels='true,correct,mostly correct')
        labels_to_delete = ['correct', 'mostly correct']
        self.delete_label_for_scraper.setlist('scraper_label[]', labels_to_delete)
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.delete_label_for_scraper)
        self.post_request.POST = query_dict
        self.post_request.user = self.admin
        self.assertTrue(delete_true_label_from_scraper(self.post_request).status_code == 200)
        for label in labels_to_delete:
            self.assertTrue(label != scraper_label for scraper_label in Scrapers.objects.filter(id=scraper.id).first().true_labels)

    def test_delete_true_label_from_scraper_by_user_not_admin(self):
        scraper = Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        Scrapers.objects.filter(id=scraper.id).update(true_labels='true,correct,mostly correct')
        labels_to_delete = ['correct', 'mostly correct']
        self.delete_label_for_scraper.setlist('scraper_label[]', labels_to_delete)
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.delete_label_for_scraper)
        self.post_request.POST = query_dict
        self.post_request.user = self.user_1
        self.assertRaises(PermissionDenied, delete_true_label_from_scraper, self.post_request)

    def test_delete_true_label_from_scraper_invalid_request(self):
        scraper = Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        Scrapers.objects.filter(id=scraper.id).update(true_labels='true,correct,mostly correct')
        labels_to_delete = ['correct', 'mostly correct']
        self.delete_label_for_scraper.setlist('scraper_label[]', labels_to_delete)
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.delete_label_for_scraper)
        self.get_request.GET = query_dict
        self.get_request.user = self.admin
        self.assertRaises(PermissionDenied, delete_true_label_from_scraper, self.get_request)

    def test_delete_true_label_from_scraper_missing_scraper_id(self):
        scraper = Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        Scrapers.objects.filter(id=scraper.id).update(true_labels='true,correct,mostly correct')
        del self.delete_label_for_scraper['scraper_id']
        labels_to_delete = ['correct', 'mostly correct']
        self.delete_label_for_scraper.setlist('scraper_label[]', labels_to_delete)
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.delete_label_for_scraper)
        self.post_request.POST = query_dict
        self.post_request.user = self.admin
        response = delete_true_label_from_scraper(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_delete_true_label_from_scraper_missing_scraper_label(self):
        Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.delete_label_for_scraper)
        self.post_request.POST = query_dict
        self.post_request.user = self.admin
        response = delete_true_label_from_scraper(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_delete_true_label_from_scraper_missing_args(self):
        scraper = Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        Scrapers.objects.filter(id=scraper.id).update(true_labels='true,correct,mostly correct')
        labels_to_delete = ['correct', 'mostly correct']
        for i in range(10):
            self.delete_label_for_scraper.setlist('scraper_label[]', labels_to_delete)
            dict_copy = self.delete_label_for_scraper.copy()
            args_to_remove = []
            for j in range(random.randint(1, len(self.delete_label_for_scraper.keys()) - 1)):
                args_to_remove.append(list(self.delete_label_for_scraper.keys())[j])
            for j in range(len(args_to_remove)):
                del self.delete_label_for_scraper[args_to_remove[j]]
            query_dict = QueryDict('', mutable=True)
            query_dict.update(self.delete_label_for_scraper)
            self.post_request.POST = query_dict
            self.post_request.user = self.admin
            response = delete_true_label_from_scraper(self.post_request)
            self.assertTrue(response.status_code == self.error_code)
            self.delete_label_for_scraper = dict_copy.copy()

    def test_delete_true_label_from_scraper_invalid_label(self):
        Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        self.delete_label_for_scraper['scraper_label'] = 'সত্য'
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.delete_label_for_scraper)
        self.post_request.POST = query_dict
        self.post_request.user = self.admin
        response = delete_true_label_from_scraper(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_delete_true_label_from_scraper_invalid_scraper_id(self):
        scraper = Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        Scrapers.objects.filter(id=scraper.id).update(true_labels='true,correct,mostly correct')
        self.delete_label_for_scraper['scraper_id'] = self.num_of_saved_users + random.randint(1, 10)
        labels_to_delete = ['correct', 'mostly correct']
        self.delete_label_for_scraper.setlist('scraper_label[]', labels_to_delete)
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.delete_label_for_scraper)
        self.post_request.POST = query_dict
        self.post_request.user = self.admin
        response = delete_true_label_from_scraper(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_delete_true_label_from_scraper_label_does_not_exist(self):
        scraper = Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        Scrapers.objects.filter(id=scraper.id).update(true_labels='true,correct,mostly correct')
        invalid_labels = ['accurate', 'not correct']
        self.delete_label_for_scraper.setlist('scraper_label[]', invalid_labels)
        Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.delete_label_for_scraper)
        self.post_request.POST = query_dict
        self.post_request.user = self.admin
        response = delete_true_label_from_scraper(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_add_false_label_to_scraper(self):
        Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        random_label = ['not accurate', 'not correct', 'mostly fake']
        self.new_label_for_scraper['scraper_label'] = random_label[random.randint(0, 2)]
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.new_label_for_scraper)
        self.post_request.POST = query_dict
        self.post_request.user = self.admin
        self.assertTrue(add_false_label_to_scraper(self.post_request).status_code == 200)

    def test_add_false_label_to_scraper_by_user_not_admin(self):
        Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        random_label = ['not accurate', 'not correct', 'mostly fake']
        self.new_label_for_scraper['scraper_label'] = random_label[random.randint(0, 2)]
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.new_label_for_scraper)
        self.post_request.POST = query_dict
        self.post_request.user = self.user_1
        self.assertRaises(PermissionDenied, add_false_label_to_scraper, self.post_request)

    def test_add_false_label_to_scraper_invalid_request(self):
        Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        random_label = ['not accurate', 'not correct', 'mostly fake']
        self.new_label_for_scraper['scraper_label'] = random_label[random.randint(0, 2)]
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.new_label_for_scraper)
        self.get_request.GET = query_dict
        self.get_request.user = self.admin
        self.assertRaises(PermissionDenied, add_false_label_to_scraper, self.get_request)

    def test_add_false_label_to_scraper_missing_scraper_id(self):
        Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        random_label = ['not accurate', 'not correct', 'mostly fake']
        self.new_label_for_scraper['scraper_label'] = random_label[random.randint(0, 2)]
        del self.new_label_for_scraper['scraper_id']
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.new_label_for_scraper)
        self.post_request.POST = query_dict
        self.post_request.user = self.admin
        response = add_false_label_to_scraper(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_add_false_label_to_scraper_missing_scraper_label(self):
        Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.new_label_for_scraper)
        self.post_request.POST = query_dict
        self.post_request.user = self.admin
        response = add_false_label_to_scraper(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_add_false_label_to_scraper_missing_args(self):
        Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        random_label = ['not accurate', 'not correct', 'mostly fake']
        self.new_label_for_scraper['scraper_label'] = random_label[random.randint(0, 2)]
        for i in range(10):
            dict_copy = self.new_label_for_scraper.copy()
            args_to_remove = []
            for j in range(random.randint(1, len(self.new_label_for_scraper.keys()) - 1)):
                args_to_remove.append(list(self.new_label_for_scraper.keys())[j])
            for j in range(len(args_to_remove)):
                del self.new_label_for_scraper[args_to_remove[j]]
            query_dict = QueryDict('', mutable=True)
            query_dict.update(self.new_label_for_scraper)
            self.post_request.POST = query_dict
            self.post_request.user = self.admin
            response = add_false_label_to_scraper(self.post_request)
            self.assertTrue(response.status_code == self.error_code)
            self.new_label_for_scraper = dict_copy.copy()

    def test_add_false_label_to_scraper_invalid_label(self):
        Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        self.new_label_for_scraper['scraper_label'] = 'সত্য'
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.new_label_for_scraper)
        self.post_request.POST = query_dict
        self.post_request.user = self.admin
        response = add_false_label_to_scraper(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_add_false_label_to_scraper_invalid_scraper_id(self):
        self.new_label_for_scraper['scraper_id'] = self.num_of_saved_users + random.randint(1, 10)
        Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        random_label = ['not accurate', 'not correct', 'mostly fake']
        self.new_label_for_scraper['scraper_label'] = random_label[random.randint(0, 2)]
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.new_label_for_scraper)
        self.post_request.POST = query_dict
        self.post_request.user = self.admin
        response = add_false_label_to_scraper(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_add_false_label_to_scraper_label_already_exists(self):
        scraper = Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        Scrapers.objects.filter(id=scraper.id).update(false_labels='false,not correct,mostly fake')
        random_label = ['false', 'not correct', 'mostly fake']
        self.new_label_for_scraper['scraper_label'] = random_label[random.randint(0, 2)]
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.new_label_for_scraper)
        self.post_request.POST = query_dict
        self.post_request.user = self.admin
        response = add_false_label_to_scraper(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_delete_false_label_from_scraper(self):
        scraper = Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        Scrapers.objects.filter(id=scraper.id).update(false_labels='false,not correct,mostly fake')
        false_labels = ['false', 'mostly fake']
        self.delete_label_for_scraper.setlist('scraper_label[]', false_labels)
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.delete_label_for_scraper)
        self.post_request.POST = query_dict
        self.post_request.user = self.admin
        self.assertTrue(delete_false_label_from_scraper(self.post_request).status_code == 200)
        self.assertTrue(self.new_label_for_scraper['scraper_label'] != label for label in Scrapers.objects.filter(id=scraper.id).first().false_labels)

    def test_delete_false_label_from_scraper_by_user_not_admin(self):
        scraper = Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        Scrapers.objects.filter(id=scraper.id).update(false_labels='false,not correct,mostly fake')
        false_labels = ['false', 'mostly fake']
        self.delete_label_for_scraper.setlist('scraper_label[]', false_labels)
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.delete_label_for_scraper)
        self.post_request.POST = query_dict
        self.post_request.user = self.user_1
        self.assertRaises(PermissionDenied, delete_false_label_from_scraper, self.post_request)

    def test_delete_false_label_from_scraper_invalid_request(self):
        scraper = Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        Scrapers.objects.filter(id=scraper.id).update(false_labels='false,not correct,mostly fake')
        false_labels = ['false', 'mostly fake']
        self.delete_label_for_scraper.setlist('scraper_label[]', false_labels)
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.delete_label_for_scraper)
        self.get_request.GET = query_dict
        self.get_request.user = self.admin
        self.assertRaises(PermissionDenied, delete_false_label_from_scraper, self.get_request)

    def test_delete_false_label_from_scraper_missing_scraper_id(self):
        scraper = Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        Scrapers.objects.filter(id=scraper.id).update(false_labels='false,not correct,mostly fake')
        del self.delete_label_for_scraper['scraper_id']
        false_labels = ['false', 'mostly fake']
        self.delete_label_for_scraper.setlist('scraper_label[]', false_labels)
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.delete_label_for_scraper)
        self.post_request.POST = query_dict
        self.post_request.user = self.admin
        response = delete_false_label_from_scraper(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_delete_false_label_from_scraper_missing_scraper_label(self):
        scraper = Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        query_dict = QueryDict('', mutable=True)
        Scrapers.objects.filter(id=scraper.id).update(false_labels='false,not correct,mostly fake')
        query_dict.update(self.delete_label_for_scraper)
        self.post_request.POST = query_dict
        self.post_request.user = self.admin
        response = delete_false_label_from_scraper(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_delete_false_label_from_scraper_missing_args(self):
        scraper = Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        Scrapers.objects.filter(id=scraper.id).update(false_labels='false,not correct,mostly fake')
        false_labels = ['false', 'mostly fake']
        for i in range(10):
            self.delete_label_for_scraper.setlist('scraper_label[]', false_labels)
            dict_copy = self.delete_label_for_scraper.copy()
            args_to_remove = []
            for j in range(random.randint(1, len(self.delete_label_for_scraper.keys()) - 1)):
                args_to_remove.append(list(self.delete_label_for_scraper.keys())[j])
            for j in range(len(args_to_remove)):
                del self.delete_label_for_scraper[args_to_remove[j]]
            query_dict = QueryDict('', mutable=True)
            query_dict.update(self.delete_label_for_scraper)
            self.post_request.POST = query_dict
            self.post_request.user = self.admin
            response = delete_false_label_from_scraper(self.post_request)
            self.assertTrue(response.status_code == self.error_code)
            self.delete_label_for_scraper = dict_copy.copy()

    def test_delete_false_label_from_scraper_invalid_label(self):
        Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        self.delete_label_for_scraper['scraper_label'] = 'সত্য'
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.delete_label_for_scraper)
        self.post_request.POST = query_dict
        self.post_request.user = self.admin
        response = delete_false_label_from_scraper(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_delete_false_label_from_scraper_invalid_scraper_id(self):
        scraper = Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        Scrapers.objects.filter(id=scraper.id).update(false_labels='false,not correct,mostly fake')
        self.delete_label_for_scraper['scraper_id'] = self.num_of_saved_users + random.randint(1, 10)
        false_labels = ['false', 'mostly fake']
        self.delete_label_for_scraper.setlist('scraper_label[]', false_labels)
        Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.delete_label_for_scraper)
        self.post_request.POST = query_dict
        self.post_request.user = self.admin
        response = delete_false_label_from_scraper(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_delete_false_label_from_scraper_label_does_not_exist(self):
        scraper = Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        Scrapers.objects.filter(id=scraper.id).update(false_labels='false,not correct,mostly fake')
        invalid_labels = ['accurate', 'correct', str(random.randint(1, 2))]
        self.delete_label_for_scraper.setlist('scraper_label[]', invalid_labels)
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.delete_label_for_scraper)
        self.post_request.POST = query_dict
        self.post_request.user = self.admin
        response = delete_false_label_from_scraper(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_check_if_scraper_new_label_is_valid_true_label_valid(self):
        Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        random_label = ['accurate', 'correct', 'mostly correct']
        self.new_label_for_scraper['scraper_label'] = random_label[random.randint(0, 2)]
        self.assertTrue(check_if_scraper_new_label_is_valid(self.new_label_for_scraper, True)[0])

    def test_check_if_scraper_new_label_is_valid_true_label_invalid_label(self):
        Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        random_label = ['صحيح', 'ճիշտ', 'सत्य']
        self.new_label_for_scraper['scraper_label'] = random_label[random.randint(0, 2)]
        self.assertFalse(check_if_scraper_new_label_is_valid(self.new_label_for_scraper, True)[0])

    def test_check_if_scraper_new_label_is_valid_true_label_invalid_scraper_id(self):
        Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        random_label = ['accurate', 'correct', 'mostly correct']
        self.new_label_for_scraper['scraper_id'] = self.num_of_saved_users + random.randint(1, 10)
        self.new_label_for_scraper['scraper_label'] = random_label[random.randint(0, 2)]
        self.assertFalse(check_if_scraper_new_label_is_valid(self.new_label_for_scraper, True)[0])

    def test_check_if_scraper_new_label_is_valid_true_label_already_exists(self):
        scraper = Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        Scrapers.objects.filter(id=scraper.id).update(true_labels='true,correct,mostly correct')
        random_label = ['true', 'correct', 'mostly correct']
        self.new_label_for_scraper['scraper_label'] = random_label[random.randint(0, 2)]
        self.assertFalse(check_if_scraper_new_label_is_valid(self.new_label_for_scraper, True)[0])

    def test_check_if_scraper_new_label_is_valid_false_label_valid(self):
        Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        random_label = ['fiction', 'not correct', 'mostly fake']
        self.new_label_for_scraper['scraper_label'] = random_label[random.randint(0, 2)]
        self.assertTrue(check_if_scraper_new_label_is_valid(self.new_label_for_scraper, False)[0])

    def test_check_if_scraper_new_label_is_valid_false_label_invalid_label(self):
        Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        random_label = ['মিথ্যা', 'गलत', '假']
        self.new_label_for_scraper['scraper_label'] = random_label[random.randint(0, 2)]
        self.assertFalse(check_if_scraper_new_label_is_valid(self.new_label_for_scraper, False)[0])

    def test_check_if_scraper_new_label_is_valid_false_label_invalid_scraper_id(self):
        Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        random_label = ['fiction', 'not correct', 'mostly fake']
        self.new_label_for_scraper['scraper_id'] = self.num_of_saved_users + random.randint(1, 10)
        self.new_label_for_scraper['scraper_label'] = random_label[random.randint(0, 2)]
        self.assertFalse(check_if_scraper_new_label_is_valid(self.new_label_for_scraper, False)[0])

    def test_check_if_scraper_new_label_is_valid_false_label_already_exists(self):
        scraper = Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        Scrapers.objects.filter(id=scraper.id).update(false_labels='false,not correct,mostly fake')
        random_label = ['false', 'not correct', 'mostly fake']
        self.new_label_for_scraper['scraper_label'] = random_label[random.randint(0, 2)]
        self.assertFalse(check_if_scraper_new_label_is_valid(self.new_label_for_scraper, False)[0])

    def test_check_if_scraper_label_delete_is_valid_true_label_valid(self):
        scraper = Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        Scrapers.objects.filter(id=scraper.id).update(true_labels='true,correct,mostly correct')
        random_label = ['true', 'correct', 'mostly correct']
        self.new_label_for_scraper['scraper_label[]'] = random_label[random.randint(0, 2)]
        self.assertTrue(check_if_scraper_label_delete_is_valid(self.new_label_for_scraper)[0])

    def test_check_if_scraper_label_delete_is_valid_true_label_invalid_scraper_id(self):
        scraper = Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        Scrapers.objects.filter(id=scraper.id).update(true_labels='true,correct,mostly correct')
        random_label = ['accurate', 'correct', 'mostly correct']
        self.new_label_for_scraper['scraper_id'] = self.num_of_saved_users + random.randint(1, 10)
        self.new_label_for_scraper['scraper_label[]'] = random_label[random.randint(0, 2)]
        self.assertFalse(check_if_scraper_label_delete_is_valid(self.new_label_for_scraper)[0])

    def test_check_if_scraper_label_delete_is_valid_false_label_invalid_scraper_id(self):
        scraper = Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        Scrapers.objects.filter(id=scraper.id).update(false_labels='false,not correct,mostly fake')
        random_label = ['false', 'not correct', 'mostly fake']
        self.new_label_for_scraper['scraper_id'] = self.num_of_saved_users + random.randint(1, 10)
        self.new_label_for_scraper['scraper_label'] = random_label[random.randint(0, 2)]
        self.assertFalse(check_if_scraper_label_delete_is_valid(self.new_label_for_scraper)[0])

    def test_check_if_scraper_labels_already_exist_true_labels_exist(self):
        scraper = Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        Scrapers.objects.filter(id=scraper.id).update(true_labels='true,correct,mostly correct')
        true_labels = ['true', 'correct']
        self.assertTrue(check_if_scraper_labels_already_exist(self.new_scraper.id,
                                                              true_labels,
                                                              True)[0])

    def test_check_if_scraper_labels_already_exist_true_labels_do_not_exist(self):
        scraper = Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        Scrapers.objects.filter(id=scraper.id).update(true_labels='true,correct,mostly correct')
        true_labels = ['accurate', str(random.randint(5, 10))]
        self.assertFalse(check_if_scraper_labels_already_exist(self.new_scraper.id,
                                                               true_labels,
                                                               True)[0])

    def test_check_if_scraper_labels_already_exist_false_labels_exist(self):
        scraper = Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        Scrapers.objects.filter(id=scraper.id).update(false_labels='false,not correct,mostly fake')
        false_labels = ['false', 'mostly fake']
        self.assertTrue(check_if_scraper_labels_already_exist(self.new_scraper.id,
                                                              false_labels,
                                                              False)[0])

    def test_check_if_scraper_labels_already_exist_false_labels_do_not_exist(self):
        scraper = Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        Scrapers.objects.filter(id=scraper.id).update(false_labels='false,not correct,mostly fake')
        false_labels = ['fiction', 'fake']
        self.assertFalse(check_if_scraper_labels_already_exist(self.new_scraper.id,
                                                               false_labels,
                                                               False)[0])

    def test_update_scrapers_comments_verdicts_adding_true_label(self):
        Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        random_label = ['accurate', 'correct', 'mostly correct'][random.randint(0, 2)]
        self.new_label_for_scraper['scraper_label'] = random_label
        Comment.objects.filter(id=self.comment_1.id).update(label=random_label)
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.new_label_for_scraper)
        self.post_request.POST = query_dict
        self.post_request.user = self.admin
        self.assertTrue(add_true_label_to_scraper(self.post_request).status_code == 200)
        self.assertTrue(Comment.objects.filter(id=self.comment_1.id).first().system_label == 'True')

    def test_update_scrapers_comments_verdicts_adding_false_label(self):
        Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        random_label = ['not accurate', 'not correct', 'mostly fake'][random.randint(0, 2)]
        self.new_label_for_scraper['scraper_label'] = random_label
        Comment.objects.filter(id=self.comment_1.id).update(label=random_label)
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.new_label_for_scraper)
        self.post_request.POST = query_dict
        self.post_request.user = self.admin
        self.assertTrue(add_false_label_to_scraper(self.post_request).status_code == 200)
        self.assertTrue(Comment.objects.filter(id=self.comment_1.id).first().system_label == 'False')

    def test_update_scrapers_comments_verdicts_deleting_true_label(self):
        scraper = Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        Scrapers.objects.filter(id=scraper.id).update(true_labels='true,correct,mostly correct')
        random_label = [['true', 'correct', 'mostly correct'][random.randint(0, 2)]]
        self.delete_label_for_scraper.setlist('scraper_label[]', random_label)
        Comment.objects.filter(id=self.comment_1.id).update(label=random_label)
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.delete_label_for_scraper)
        self.post_request.POST = query_dict
        self.post_request.user = self.admin
        self.assertTrue(delete_true_label_from_scraper(self.post_request).status_code == 200)
        self.assertTrue(Comment.objects.filter(id=self.comment_1.id).first().system_label == 'Unknown')

    def test_update_scrapers_comments_verdicts_deleting_false_label(self):
        scraper = Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        Scrapers.objects.filter(id=scraper.id).update(false_labels='false,not correct,mostly false')
        random_label = [['false', 'not correct', 'mostly false'][random.randint(0, 2)]]
        self.delete_label_for_scraper.setlist('scraper_label[]', random_label)
        Comment.objects.filter(id=self.comment_1.id).update(label=random_label)
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.delete_label_for_scraper)
        self.post_request.POST = query_dict
        self.post_request.user = self.admin
        self.assertTrue(delete_false_label_from_scraper(self.post_request).status_code == 200)
        self.assertTrue(Comment.objects.filter(id=self.comment_1.id).first().system_label == 'Unknown')

    def test_update_scrapers_comments_verdicts_invalid_scraper(self):
        self.assertTrue(update_scrapers_comments_verdicts(self.num_of_saved_users + random.randint(1, 10)).status_code == self.error_code)

    def test_check_if_user_is_scraper(self):
        Scrapers.objects.create(scraper=self.new_scraper)
        self.assertTrue(check_if_user_is_scraper(self.new_scraper.id))

    def test_check_if_user_is_scraper_invalid_user(self):
        self.assertFalse(check_if_user_is_scraper(self.num_of_saved_users + random.randint(1, 10)))

    def test_check_if_user_is_scraper_not_scraper(self):
        self.assertFalse(check_if_user_is_scraper(self.user_1.id))

    def test_upload_user_img(self):
        Users_Images.objects.create(user=self.user_2)
        user_image = {'user_id': self.user_2.id}
        self.post_request.FILES['profile_img'] = self.image_file_test
        self.post_request.user = self.user_2
        query_dict = QueryDict('', mutable=True)
        query_dict.update(user_image)
        self.post_request.POST = query_dict
        self.assertTrue(upload_user_img(self.post_request).status_code == 200)
        self.assertTrue(Users_Images.objects.filter(user=self.user_2).first().profile_img.url ==
                        '/media/images/2/2_image')
        self.post_request = HttpRequest()
        self.post_request.method = 'POST'
        self.post_request.user = self.user_2
        self.image_file_test = SimpleUploadedFile(name="profile_default_image_test.jpg", content=open(
            'users/profile_default_image_test.jpg', 'rb').read(), content_type='image/jpeg')
        self.post_request.FILES['profile_img'] = self.image_file_test
        self.post_request.POST = query_dict
        self.assertTrue(upload_user_img(self.post_request).status_code == 200)
        self.assertTrue(Users_Images.objects.filter(user=self.user_2).first().profile_img.url ==
                        '/media/images/2/2_image')

    def test_upload_user_img_missing_image(self):
        Users_Images.objects.create(user=self.user_2)
        user_image = {'user_id': self.user_2.id}
        self.post_request.FILES['profile_img'] = ''
        self.post_request.user = self.user_2
        query_dict = QueryDict('', mutable=True)
        query_dict.update(user_image)
        self.post_request.POST = query_dict

        middleware = SessionMiddleware()
        middleware.process_request(self.post_request)
        self.post_request.session.save()

        middleware = MessageMiddleware()
        middleware.process_request(self.post_request)
        self.post_request.session.save()

        response = upload_user_img(self.post_request)
        self.assertTrue(response.status_code == 302)
        self.assertTrue(response.url == '/users/' + str(self.user_2.id))
        self.assertTrue(Users_Images.objects.filter(user=self.user_2).first().image_url() ==
                        'https://wtfact.ise.bgu.ac.il/media/profile_default_image.jpg')

    def test_upload_user_img_invalid_image(self):
        Users_Images.objects.create(user=self.user_2)
        user_image = {'user_id': self.user_2.id}
        self.post_request.FILES['profile_img'] = self.image_file_test_invalid
        self.post_request.user = self.user_2
        query_dict = QueryDict('', mutable=True)
        query_dict.update(user_image)
        self.post_request.POST = query_dict

        middleware = SessionMiddleware()
        middleware.process_request(self.post_request)
        self.post_request.session.save()

        middleware = MessageMiddleware()
        middleware.process_request(self.post_request)
        self.post_request.session.save()

        response = upload_user_img(self.post_request)
        self.assertTrue(response.status_code == 302)
        self.assertTrue(response.url == '/users/' + str(self.user_2.id))
        self.assertTrue(Users_Images.objects.filter(user=self.user_2).first().image_url() ==
                        'https://wtfact.ise.bgu.ac.il/media/profile_default_image.jpg')

    def test_upload_user_img_user_not_authenticated(self):
        Users_Images.objects.create(user=self.user_2)
        user_image = {'user_id': self.user_2.id}
        self.post_request.FILES['profile_img'] = self.image_file_test
        self.post_request.user = AnonymousUser()
        query_dict = QueryDict('', mutable=True)
        query_dict.update(user_image)
        self.post_request.POST = query_dict
        self.assertRaises(PermissionDenied, upload_user_img, self.post_request)
        self.assertTrue(Users_Images.objects.filter(user=self.user_2).first().image_url() ==
                        'https://wtfact.ise.bgu.ac.il/media/profile_default_image.jpg')

    def test_notifications_page(self):
        self.get_request.user = self.user_1
        self.assertTrue(notifications_page(self.get_request).status_code == 200)

    def test_notifications_page_by_anonymous_user(self):
        self.get_request.user = AnonymousUser()
        self.assertRaises(PermissionDenied, notifications_page, self.get_request)

    def test_notifications_page_invalid_request(self):
        self.post_request.user = self.user_1
        self.assertRaises(PermissionDenied, notifications_page, self.post_request)

    def test_read_all_notifications(self):
        notify.send(self.user_1, recipient=self.user_2, verb='some msg 2')
        for notification in Notification.objects.filter(recipient=self.user_2):
            notification.mark_as_unread()
        self.assertTrue(len(Notification.objects.filter(recipient=self.user_2).read()) == 0)
        self.assertTrue(len(Notification.objects.filter(recipient=self.user_2).unread()) == 2)
        query_dict = QueryDict('', mutable=True)
        self.post_request.POST = query_dict
        self.post_request.user = self.user_2
        self.assertTrue(read_all_notifications(self.post_request).status_code == 200)
        self.assertTrue(len(Notification.objects.filter(recipient=self.user_2).read()) == 2)
        self.assertTrue(len(Notification.objects.filter(recipient=self.user_2).unread()) == 0)

    def test_read_all_notifications_user_not_authenticated(self):
        user = AnonymousUser()
        query_dict = QueryDict('', mutable=True)
        self.post_request.POST = query_dict
        self.post_request.user = user
        self.assertRaises(PermissionDenied, read_all_notifications, self.post_request)

    def test_read_notification(self):
        self.notification.mark_as_unread()
        self.assertTrue(len(Notification.objects.filter(id=self.notification.id).read()) == 0)
        notification_info = {'notification_id': self.notification.id}
        query_dict = QueryDict('', mutable=True)
        query_dict.update(notification_info)
        self.post_request.POST = query_dict
        self.post_request.user = self.user_2
        self.assertTrue(read_notification(self.post_request).status_code == 200)
        self.assertTrue(len(Notification.objects.filter(id=self.notification.id).read()) == 1)

    def test_read_notification_missing_notification_id(self):
        self.notification.mark_as_unread()
        self.assertTrue(len(Notification.objects.filter(id=self.notification.id).read()) == 0)
        query_dict = QueryDict('', mutable=True)
        query_dict.update({})
        self.post_request.POST = query_dict
        self.post_request.user = self.user_2
        response = read_notification(self.post_request)
        self.assertTrue(response.status_code == self.error_code)
        self.assertTrue(len(Notification.objects.filter(id=self.notification.id).read()) == 0)

    def test_read_notification_invalid_notification_id(self):
        self.notification.mark_as_unread()
        self.assertTrue(len(Notification.objects.filter(id=self.notification.id).read()) == 0)
        notification_info = {'notification_id': self.num_of_saved_notifications + random.randint(1, 10)}
        query_dict = QueryDict('', mutable=True)
        query_dict.update(notification_info)
        self.post_request.POST = query_dict
        self.post_request.user = self.user_2
        response = read_notification(self.post_request)
        self.assertTrue(response.status_code == self.error_code)
        self.assertTrue(len(Notification.objects.filter(id=self.notification.id).read()) == 0)

    def test_read_notification_by_anonymous_user(self):
        self.notification.mark_as_unread()
        self.assertTrue(len(Notification.objects.filter(id=self.notification.id).read()) == 0)
        notification_info = {'notification_id': self.notification.id}
        query_dict = QueryDict('', mutable=True)
        query_dict.update(notification_info)
        self.post_request.POST = query_dict
        self.post_request.user = AnonymousUser()
        self.assertRaises(PermissionDenied, read_notification, self.post_request)
        self.assertTrue(len(Notification.objects.filter(id=self.notification.id).read()) == 0)

    def test_read_notification_invalid_request(self):
        self.notification.mark_as_unread()
        self.assertTrue(len(Notification.objects.filter(id=self.notification.id).read()) == 0)
        notification_info = {'notification_id': self.notification.id}
        query_dict = QueryDict('', mutable=True)
        query_dict.update(notification_info)
        self.get_request.POST = query_dict
        self.get_request.user = self.user_2
        self.assertRaises(PermissionDenied, read_notification, self.get_request)
        self.assertTrue(len(Notification.objects.filter(id=self.notification.id).read()) == 0)

    def test_delete_notification(self):
        self.assertTrue(len(Notification.objects.filter(id=self.notification.id)) == 1)
        notification_info = {'notification_id': self.notification.id}
        query_dict = QueryDict('', mutable=True)
        query_dict.update(notification_info)
        self.post_request.POST = query_dict
        self.post_request.user = self.user_2
        self.assertTrue(delete_notification(self.post_request).status_code == 200)
        self.assertTrue(len(Notification.objects.filter(id=self.notification.id)) == 0)

    def test_delete_notification_missing_notification_id(self):
        self.assertTrue(len(Notification.objects.filter(id=self.notification.id)) == 1)
        query_dict = QueryDict('', mutable=True)
        query_dict.update({})
        self.post_request.POST = query_dict
        self.post_request.user = self.user_2
        response = delete_notification(self.post_request)
        self.assertTrue(response.status_code == self.error_code)
        self.assertTrue(len(Notification.objects.filter(id=self.notification.id)) == 1)

    def test_delete_notification_invalid_notification_id(self):
        self.assertTrue(len(Notification.objects.filter(id=self.notification.id)) == 1)
        notification_info = {'notification_id': self.num_of_saved_notifications + random.randint(1, 10)}
        query_dict = QueryDict('', mutable=True)
        query_dict.update(notification_info)
        self.post_request.POST = query_dict
        self.post_request.user = self.user_2
        response = delete_notification(self.post_request)
        self.assertTrue(response.status_code == self.error_code)
        self.assertTrue(len(Notification.objects.filter(id=self.notification.id)) == 1)

    def test_delete_notification_by_anonymous_user(self):
        self.assertTrue(len(Notification.objects.filter(id=self.notification.id)) == 1)
        notification_info = {'notification_id': self.notification.id}
        query_dict = QueryDict('', mutable=True)
        query_dict.update(notification_info)
        self.post_request.POST = query_dict
        self.post_request.user = AnonymousUser()
        self.assertRaises(PermissionDenied, delete_notification, self.post_request)
        self.assertTrue(len(Notification.objects.filter(id=self.notification.id)) == 1)

    def test_delete_notification_invalid_request(self):
        self.assertTrue(len(Notification.objects.filter(id=self.notification.id)) == 1)
        notification_info = {'notification_id': self.notification.id}
        query_dict = QueryDict('', mutable=True)
        query_dict.update(notification_info)
        self.get_request.POST = query_dict
        self.get_request.user = self.user_2
        self.assertRaises(PermissionDenied, delete_notification, self.get_request)
        self.assertTrue(len(Notification.objects.filter(id=self.notification.id)) == 1)

    def test_check_if_notification_is_valid(self):
        self.assertTrue(check_if_notification_is_valid(self.notification_info)[0])

    def test_check_if_notification_is_valid_missing_notification_id(self):
        del self.notification_info['notification_id']
        self.assertFalse(check_if_notification_is_valid(self.notification_info)[0])

    def test_check_if_notification_is_valid_invalid_notification_id(self):
        self.notification_info['notification_id'] = self.num_of_saved_notifications + random.randint(1, 10)
        self.assertFalse(check_if_notification_is_valid(self.notification_info)[0])

    def test_check_if_notification_is_valid_missing_user_id(self):
        del self.notification_info['user_id']
        self.assertFalse(check_if_notification_is_valid(self.notification_info)[0])

    def test_check_if_notification_is_valid_invalid_user_id(self):
        self.notification_info['user_id'] = self.num_of_saved_users + random.randint(1, 10)
        self.assertFalse(check_if_notification_is_valid(self.notification_info)[0])

    def test_check_if_notification_is_valid_notification_of_another_user(self):
        self.notification_info['user_id'] = self.user_3.id
        self.assertFalse(check_if_notification_is_valid(self.notification_info)[0])

    def test_change_username(self):
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.user_info)
        self.post_request.POST = query_dict
        self.post_request.user = self.user_1
        self.assertTrue(change_username(self.post_request).status_code == 200)
        self.assertTrue(User.objects.filter(id=self.user_info['user_id']).first().username
                        == self.user_info['new_username'])

    def test_change_username_of_another_user(self):
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.user_info)
        self.post_request.POST = query_dict
        self.post_request.user = self.user_2
        response = change_username(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_change_username_of_another_user_by_admin(self):
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.user_info)
        self.post_request.POST = query_dict
        self.post_request.user = self.admin
        self.assertTrue(change_username(self.post_request).status_code == 200)
        self.assertTrue(User.objects.filter(id=self.user_info['user_id']).first().username
                        == self.user_info['new_username'])

    def test_change_username_missing_user_id(self):
        del self.user_info['user_id']
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.user_info)
        self.post_request.POST = query_dict
        self.post_request.user = self.user_1
        response = change_username(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_change_username_invalid_user_id(self):
        self.user_info['user_id'] = self.num_of_saved_users + random.randint(1, 10)
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.user_info)
        self.post_request.POST = query_dict
        self.post_request.user = self.user_1
        response = change_username(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_change_username_missing_new_username(self):
        del self.user_info['new_username']
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.user_info)
        self.post_request.POST = query_dict
        self.post_request.user = self.user_1
        response = change_username(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_change_username_by_anonymous_user(self):
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.user_info)
        self.post_request.POST = query_dict
        self.post_request.user = AnonymousUser()
        self.assertRaises(PermissionDenied, change_username, self.post_request)

    def test_change_username_invalid_request(self):
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.user_info)
        self.get_request.POST = query_dict
        self.get_request.user = self.user_1
        self.assertRaises(PermissionDenied, change_username, self.get_request)

    def test_change_username_missing_args(self):
        del self.user_info['request_user_id']
        del self.user_info['is_superuser']
        for i in range(10):
            dict_copy = self.user_info.copy()
            args_to_remove = []
            for j in range(random.randint(1, len(self.user_info.keys()) - 1)):
                args_to_remove.append(list(self.user_info.keys())[j])
            for j in range(len(args_to_remove)):
                del self.user_info[args_to_remove[j]]
            len_users = len(User.objects.all())
            query_dict = QueryDict('', mutable=True)
            query_dict.update(self.user_info)
            self.post_request.POST = query_dict
            self.post_request.user = self.user_1
            response = change_username(self.post_request)
            self.assertTrue(response.status_code == self.error_code)
            self.assertTrue(len(User.objects.all()) == len_users)
            self.user_info = dict_copy.copy()

    def test_check_if_user_info_is_valid(self):
        self.assertTrue(check_if_user_info_is_valid(self.user_info)[0])

    def test_check_if_user_info_is_valid_missing_user_id(self):
        del self.user_info['user_id']
        self.assertFalse(check_if_user_info_is_valid(self.user_info)[0])

    def test_check_if_user_info_is_valid_invalid_user_id(self):
        self.user_info['user_id'] = self.num_of_saved_users + random.randint(1, 10)
        self.assertFalse(check_if_user_info_is_valid(self.user_info)[0])

    def test_check_if_user_info_is_valid_missing_new_username(self):
        del self.user_info['new_username']
        self.assertFalse(check_if_user_info_is_valid(self.user_info)[0])

    def test_check_if_user_info_is_valid_missing_request_user_id(self):
        del self.user_info['request_user_id']
        self.assertFalse(check_if_user_info_is_valid(self.user_info)[0])

    def test_check_if_user_info_is_valid_invalid_request_user_id(self):
        self.user_info['request_user_id'] = self.num_of_saved_users + random.randint(1, 10)
        self.assertFalse(check_if_user_info_is_valid(self.user_info)[0])

    def test_check_if_user_info_is_valid_missing_user_type(self):
        del self.user_info['is_superuser']
        self.assertFalse(check_if_user_info_is_valid(self.user_info)[0])

    def test_check_if_user_info_is_valid_by_another_user(self):
        self.user_info['request_user_id'] = self.user_2.id
        self.assertFalse(check_if_user_info_is_valid(self.user_info)[0])

    def test_check_if_user_info_is_valid_by_admin_user(self):
        self.user_info['request_user_id'] = self.admin.id
        self.user_info['is_superuser'] = True
        self.assertTrue(check_if_user_info_is_valid(self.user_info)[0])

    ################
    # Models Tests #
    ################

    def test_get_user_image(self):
        user_1_img = Users_Images(user=self.user_1)
        user_1_img.save()
        self.assertTrue(self.user_1.get_user_image() == user_1_img)
        self.assertTrue(len(Users_Images.objects.filter(user=self.user_2)) == 0)
        self.assertTrue(self.user_2.get_user_image() ==
                        Users_Images.objects.filter(user=self.user_2).first())

    def test_get_user_rep(self):
        self.assertTrue(self.user_1.get_user_rep() == self.user_1_rep)
        self.assertTrue(len(Users_Reputations.objects.filter(user=self.user_2)) == 0)
        self.assertTrue(self.user_2.get_user_rep() == Users_Reputations.objects.filter(user=self.user_2).first())

    def test_get_scraper(self):
        self.assertTrue(self.user_1.get_scraper() is None)
        self.assertTrue(self.user_2.get_scraper() is None)
        self.assertTrue(self.new_scraper.get_scraper() == Scrapers.objects.filter(scraper=self.new_scraper).first())

    def test_get_notifications(self):
        self.assertTrue(len(self.user_1.get_notifications()) == 0)
        self.assertTrue(len(self.user_2.get_notifications()) == 1)

    def test_upload_to(self):
        user_1_img = Users_Images(user=self.user_1)
        user_1_img.save()
        from users.models import upload_to
        file = 'file' + str(random.randint(1, 10))
        self.assertTrue(upload_to(user_1_img, file) ==
                        "images/" + str(self.user_1.id) + "/" + str(self.user_1.id) + '_image')

    def test_image_url(self):
        default_media = 'https://wtfact.ise.bgu.ac.il/media/profile_default_image.jpg'
        import tempfile
        image = tempfile.NamedTemporaryFile(suffix=".jpg").name
        user_1_img = Users_Images(user=self.user_1, profile_img=image)
        user_1_img.save()
        self.assertTrue(user_1_img.image_url() == user_1_img.profile_img.url)
        user_2_img = Users_Images(user=self.user_2)
        user_2_img.save()
        self.assertTrue(user_2_img.image_url() == default_media)

    def test_user_image_str(self):
        user_1_img = Users_Images(user=self.user_1)
        user_1_img.save()
        self.assertTrue(user_1_img.__str__() == self.user_1.username)

    def test_get_reputation(self):
        import math
        self.assertTrue(self.user_1_rep.get_reputation() == math.ceil(self.rep / 20))

    def test_user_reputation_str(self):
        self.assertTrue(self.user_1_rep.__str__() == self.user_1.username + ' - ' + str(self.rep))

    def test_get_true_labels_for_user(self):
        scraper = Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        true_labels = scraper.get_true_labels()
        self.assertTrue(len(true_labels) == 1)
        self.assertTrue(true_labels[0] == 'true')

        random_label = ['accurate', 'correct', 'mostly correct']
        index = random.randint(0, 2)
        self.new_label_for_scraper['scraper_label'] = random_label[index]
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.new_label_for_scraper)
        self.post_request.POST = query_dict
        self.post_request.user = self.admin
        self.assertTrue(add_true_label_to_scraper(self.post_request).status_code == 200)
        true_labels = Scrapers.objects.filter(scraper=self.new_scraper).first().get_true_labels()
        self.assertTrue(len(true_labels) == 2)
        self.assertTrue(true_labels[0] == 'true')
        self.assertTrue(true_labels[1] == random_label[index])

    def test_get_false_labels_for_user(self):
        scraper = Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        false_labels = scraper.get_false_labels()
        self.assertTrue(len(false_labels) == 1)
        self.assertTrue(false_labels[0] == 'false')

        random_label = ['mostly false', 'incorrect', 'mostly incorrect']
        index = random.randint(0, 2)
        self.new_label_for_scraper['scraper_label'] = random_label[index]
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.new_label_for_scraper)
        self.post_request.POST = query_dict
        self.post_request.user = self.admin
        self.assertTrue(add_false_label_to_scraper(self.post_request).status_code == 200)
        false_labels = Scrapers.objects.filter(scraper=self.new_scraper).first().get_false_labels()
        self.assertTrue(len(false_labels) == 2)
        self.assertTrue(false_labels[0] == 'false')
        self.assertTrue(false_labels[1] == random_label[index])

    def test_scraper_str(self):
        scraper = Scrapers.objects.create(scraper=self.new_scraper, scraper_name=self.new_scraper.username)
        self.assertTrue(scraper.__str__() == self.new_scraper.username)
