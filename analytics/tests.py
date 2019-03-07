from django.contrib.auth.models import User
from django.http import HttpRequest, Http404
from django.test import TestCase
from analytics.views import view_analytics


class Analytics(TestCase):
    def setUp(self):
        self.user_1 = User(username="User1", email='user1@gmail.com')
        self.user_1.save()
        self.get_request = HttpRequest()
        self.get_request.method = 'GET'

    def tearDown(self):
        pass

    def test_view_analytics_valid_user(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        admin = User.objects.create_superuser('admin', 'admin@gmail.com', 'admin')
        self.get_request.user = admin
        self.assertTrue(view_analytics(self.get_request).status_code == 200)

    def test_view_analytics_invalid_user(self):
        self.get_request.user = self.user_1
        self.assertRaises(Http404, view_analytics, self.get_request)
