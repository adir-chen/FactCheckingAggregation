from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.test import TestCase
from claims.models import Claim
from comments.models import Comment
from search.views import search
from users.models import Users_Images
import datetime
import random
import string


class SearchTest(TestCase):
    def setUp(self):
        self.request = HttpRequest()
        self.request.method = 'GET'
        self.request.GET._mutable = True

    def tearDown(self):
        pass

    def test_search(self):
        self.request.GET['search_keywords'] = 'claim'
        response = search(self.request)
        self.assertTrue(response.status_code == 200)

    def test_search_invalid_request(self):
        self.request.GET['search_keywords'] = 'claim'
        self.request.method = 'POST'
        self.assertRaises(PermissionDenied, search, self.request)

    def test_search_many_claims(self):
        self.user = User(username="User1", email='user1@gmail.com')
        self.user.save()
        self.user_image = Users_Images(user=self.user)
        self.user_image.save()
        for i in range(1, 24):
            claim = Claim(user_id=self.user.id,
                          claim='claim' + str(i),
                          category='category ' + str(i),
                          tags='claim' + str(i),
                          authenticity_grade=0,
                          image_src='claim' + str(i))
            claim.save()
            comment = Comment(claim_id=claim.id,
                              user_id=claim.user.id,
                              title=claim.claim,
                              description='description1',
                              url='url1',
                              verdict_date=datetime.date.today() - datetime.timedelta(days=random.randint(0, 10)),
                              label='label1')
            comment.save()
        self.request.GET['search_keywords'] = 'claim'
        response = search(self.request)
        self.assertTrue(response.status_code == 200)

    def test_invalid_search(self):
        letters = string.ascii_lowercase
        rand_search = ''.join(random.choice(letters) for i in range(15))
        self.request.GET['search_keywords'] = rand_search
        response = search(self.request)
        self.assertEqual(response.status_code, 200)

