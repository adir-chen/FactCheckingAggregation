from django.http import HttpRequest
from django.test import TestCase
from search.views import search
import random
import string


class SearchTest(TestCase):
    def setUp(self):
        self.request = HttpRequest()
        self.request.method = 'GET'
        if not self.request.GET._mutable:
            self.request.GET._mutable = True

    def tearDown(self):
        pass

    def test_serach(self):
        self.request.GET['search_keywords'] = 'claim'
        response = search(self.request)
        self.assertEqual(response.status_code, 200)

    def test_invalid_serach(self):
        letters = string.ascii_lowercase
        rand_search = ''.join(random.choice(letters) for i in range(15))
        self.request.GET['search_keywords'] = rand_search
        response = search(self.request)
        self.assertEqual(response.status_code, 200)

