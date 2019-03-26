from django.contrib.auth.models import User
from django.http import HttpRequest, Http404
from django.test import TestCase
from analytics.views import view_analytics


class Analytics(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser('admin', 'admin@gmail.com', 'admin')
        self.user_1 = User(username="User1", email='user1@gmail.com')
        self.user_1.save()
        self.get_request = HttpRequest()
        self.get_request.method = 'GET'
        self.post_request = HttpRequest()
        self.post_request.method = 'POST'

    def tearDown(self):
        pass

    def test_view_analytics_valid_user(self):
        self.get_request.user = self.admin
        self.assertTrue(view_analytics(self.get_request).status_code == 200)

    def test_view_analytics_invalid_user(self):
        self.get_request.user = self.user_1
        self.assertRaises(Http404, view_analytics, self.get_request)

    def test_view_analytics_invalid_request(self):
        self.post_request.user = self.admin
        self.assertRaises(Http404, view_analytics, self.post_request)
