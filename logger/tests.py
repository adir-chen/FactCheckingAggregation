from django.contrib.auth.models import User
from django.http import HttpRequest, Http404
from django.test import TestCase
from logger.models import Logger
from logger.views import view_log, save_log_message, check_duplicate_log_for_user
import random


class LoggerTest(TestCase):
    def setUp(self):
        self.user_1 = User(username="User1", email='user1@gmail.com')
        self.user_1.save()
        self.post_request = HttpRequest()
        self.post_request.method = 'POST'

    def tearDown(self):
        pass

    def test_view_log_valid_user(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        admin = User.objects.create_superuser('admin', 'admin@gmail.com', 'admin')
        self.post_request.user = admin
        self.assertTrue(view_log(self.post_request).status_code == 200)

    def test_view_log_invalid_user(self):
        self.post_request.user = self.user_1
        self.assertRaises(Http404, view_log, self.post_request)

    def test_save_log_message_success_action(self):
        user_id = random.randint(1, 10)
        save_log_message(user_id, 'user_1', 'Adding new claim', True)
        self.assertTrue(Logger.objects.all().first().username == 'user_1')
        self.assertTrue(Logger.objects.all().first().user_id == user_id)
        self.assertTrue(Logger.objects.all().first().action == 'Adding new claim')
        self.assertTrue(Logger.objects.all().first().result)

    def test_save_log_message_failure_action(self):
        user_id = random.randint(1, 10)
        save_log_message(user_id, 'user_1', 'Adding new claim')
        self.assertTrue(Logger.objects.all().first().username == 'user_1')
        self.assertTrue(Logger.objects.all().first().user_id == user_id)
        self.assertTrue(Logger.objects.all().first().action == 'Adding new claim')
        self.assertFalse(Logger.objects.all().first().result)

    def test_save_log_message_failure_action_invalid_user(self):
        save_log_message(None, '', 'Adding new claim')
        self.assertTrue(Logger.objects.all().first().username == 'Unknown')
        self.assertTrue(Logger.objects.all().first().user_id == -1)
        self.assertTrue(Logger.objects.all().first().action == 'Adding new claim')
        self.assertFalse(Logger.objects.all().first().result)

    def test_check_duplicate_log_for_user_true(self):
        user_id = random.randint(1, 10)
        self.assertFalse(check_duplicate_log_for_user(user_id, 'Adding new claim'))

    def test_check_duplicate_log_for_user_false(self):
        user_id = random.randint(1, 10)
        save_log_message(user_id, 'user_1', 'Adding new claim')
        self.assertTrue(check_duplicate_log_for_user(user_id, 'Adding new claim'))



