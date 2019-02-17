from django.contrib.auth.models import User
from django.http import HttpRequest, QueryDict
from django.test import TestCase
from contact_us.views import send_email, check_if_email_is_valid, contact_us_page
import random
import string

class ContactUsTest(TestCase):
    def setUp(self):
        self.user_1 = User(username="User1", email='user1@gmail.com')
        self.user_1.save()
        self.post_request = HttpRequest()
        self.post_request.method = 'POST'
        self.data = {'user_email': self.user_1.email,
                     'subject': 'subject',
                     'description': 'description'}

    def tearDown(self):
        pass

    def test_send_email(self):
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.data)
        self.post_request.POST = query_dict
        self.assertTrue(send_email(self.post_request).status_code == 200)

    def test_send_email_invalid_email(self):
        query_dict = QueryDict('', mutable=True)
        self.data['user_email'] = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        query_dict.update(self.data)
        self.post_request.POST = query_dict
        self.assertRaises(Exception, send_email, self.post_request)

    def test_send_email_invalid_request(self):
        query_dict = QueryDict('', mutable=True)
        self.post_request.method = 'GET'
        query_dict.update(self.data)
        self.post_request.POST = query_dict
        self.assertRaises(Exception, send_email, self.post_request)

    def test_check_if_email_is_valid(self):
        self.assertTrue(check_if_email_is_valid(self.data)[0])

    def test_check_if_email_is_valid_missing_user_mail(self):
        del self.data['user_email']
        self.assertFalse(check_if_email_is_valid(self.data)[0])

    def test_check_if_email_is_valid_missing_subject(self):
        del self.data['subject']
        self.assertFalse(check_if_email_is_valid(self.data)[0])

    def test_check_if_email_is_valid_missing_description(self):
        del self.data['description']
        self.assertFalse(check_if_email_is_valid(self.data)[0])

    def test_check_if_mail_is_valid_invalid_user_mail(self):
        self.data['user_email'] = self.user_1.username
        self.assertFalse(check_if_email_is_valid(self.data)[0])

    def test_contact_us_page(self):
        self.assertTrue(contact_us_page(self.post_request).status_code == 200)
