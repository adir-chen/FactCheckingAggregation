from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, QueryDict
from django.test import TestCase
from contact_us.views import contact_us_page, send_email, check_if_email_is_valid, check_for_spam
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

        self.error_code = 404

    def tearDown(self):
        pass

    def test_contact_us_page(self):
        self.assertTrue(contact_us_page(self.post_request).status_code == 200)

    def test_send_email(self):
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.data)
        self.post_request.POST = query_dict
        self.post_request.user = self.user_1
        self.assertTrue(send_email(self.post_request).status_code == 200)

    def test_send_email_invalid_email(self):
        query_dict = QueryDict('', mutable=True)
        self.data['user_email'] = ''.join(random.choices(string.ascii_uppercase, k=10))
        query_dict.update(self.data)
        self.post_request.POST = query_dict
        self.post_request.user = self.user_1
        response = send_email(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_send_email_invalid_email_user_not_authenticated(self):
        from django.contrib.auth.models import AnonymousUser
        query_dict = QueryDict('', mutable=True)
        self.data['user_email'] = ''.join(random.choices(string.ascii_uppercase, k=10))
        query_dict.update(self.data)
        self.post_request.POST = query_dict
        self.post_request.user = AnonymousUser()
        response = send_email(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_send_email_invalid_request(self):
        query_dict = QueryDict('', mutable=True)
        self.post_request.method = 'GET'
        query_dict.update(self.data)
        self.post_request.POST = query_dict
        self.post_request.user = self.user_1
        self.assertRaises(PermissionDenied, send_email, self.post_request)

    def test_send_email_invalid_request_user_not_authenticated(self):
        from django.contrib.auth.models import AnonymousUser
        query_dict = QueryDict('', mutable=True)
        self.post_request.method = 'GET'
        query_dict.update(self.data)
        self.post_request.POST = query_dict
        self.post_request.user = AnonymousUser()
        self.assertRaises(PermissionDenied, send_email, self.post_request)

    def test_send_email_missing_args(self):
        from django.contrib.auth.models import AnonymousUser
        for i in range(10):
            dict_copy = self.data.copy()
            args_to_remove = []
            for j in range(random.randint(1, len(self.data.keys()) - 1)):
                args_to_remove.append(list(self.data.keys())[j])
            for j in range(len(args_to_remove)):
                del self.data[args_to_remove[j]]
            query_dict = QueryDict('', mutable=True)
            query_dict.update(self.data)
            self.post_request.POST = query_dict
            rand_num = random.randint(1, 2)
            if rand_num == 1:
                self.post_request.user = self.user_1
            else:
                self.post_request.user = AnonymousUser()
            response = send_email(self.post_request)
            self.assertTrue(response.status_code == self.error_code)
            self.data = dict_copy.copy()

    def test_check_if_email_is_valid(self):
        ip = '127.0.0.1'
        self.data['ip'] = ip
        self.assertTrue(check_if_email_is_valid(self.data)[0])

    def test_check_if_email_is_valid_missing_user_mail(self):
        del self.data['user_email']
        self.assertFalse(check_if_email_is_valid(self.data)[0])

    def test_check_if_mail_is_valid_invalid_user_mail(self):
        self.data['user_email'] = self.user_1.username
        self.assertFalse(check_if_email_is_valid(self.data)[0])

    def test_check_if_email_is_valid_missing_subject(self):
        del self.data['subject']
        self.assertFalse(check_if_email_is_valid(self.data)[0])

    def test_check_if_email_is_valid_missing_description(self):
        del self.data['description']
        self.assertFalse(check_if_email_is_valid(self.data)[0])

    def test_check_if_email_is_valid_spam(self):
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.data)
        self.post_request.POST = query_dict
        ip = '127.0.0.1'
        self.post_request.META['HTTP_X_FORWARDED_FOR'] = ip
        self.post_request.user = self.user_1
        for i in range(5):
            send_email(self.post_request)
        self.data['ip'] = ip
        self.assertFalse(check_if_email_is_valid(self.data)[0])

    def test_check_for_spam_not_spam(self):
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.data)
        self.post_request.POST = query_dict
        ip = '127.0.0.1'
        self.post_request.META['HTTP_X_FORWARDED_FOR'] = ip
        self.post_request.user = self.user_1
        send_email(self.post_request)
        self.assertFalse(check_for_spam(ip))

    def test_check_for_spam_spam(self):
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.data)
        self.post_request.POST = query_dict
        ip = '127.0.0.1'
        self.post_request.META['HTTP_X_FORWARDED_FOR'] = ip
        self.post_request.user = self.user_1
        for i in range(5):
            self.assertFalse(check_for_spam(ip))
            send_email(self.post_request)
        self.assertTrue(check_for_spam(ip))
