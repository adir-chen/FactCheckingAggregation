from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from django.http import HttpRequest, QueryDict
from django.core.exceptions import PermissionDenied
from django.test import TestCase
from analytics.views import view_analytics, view_customized_analytics, check_if_customized_analytics_is_valid, \
    check_valid_dates, view_top_n_claims, check_if_top_claims_is_valid, get_claim_as_json
import datetime
import random

from claims.models import Claim


class Analytics(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser('admin', 'admin@gmail.com', 'admin')
        self.user_1 = User(username="User1", email='user1@gmail.com')
        self.user_1.save()
        self.get_request = HttpRequest()
        self.get_request.method = 'GET'
        self.post_request = HttpRequest()
        self.post_request.method = 'POST'
        self.today = datetime.date.today()
        self.past = self.today - relativedelta(months=random.randint(1, 4))
        self.customized_analytics = {'start_date': str(self.past),
                                     'end_date': str(self.today)}
        self.months = 'ga:year, ga:month'
        self.days = 'ga:year, ga:month, ga:day'

        self.top_claims = {'start_date': str(self.past),
                           'end_date': str(self.today),
                           'n': str(random.randint(1, 10))}

        self.error_code = 404

    def tearDown(self):
        pass

    def test_view_analytics_valid_user(self):
        self.get_request.user = self.admin
        self.assertTrue(view_analytics(self.get_request).status_code == 200)

    def test_view_analytics_invalid_user(self):
        self.get_request.user = self.user_1
        self.assertRaises(PermissionDenied, view_analytics, self.get_request)

    def test_view_analytics_invalid_request(self):
        self.post_request.user = self.admin
        self.assertRaises(PermissionDenied, view_analytics, self.post_request)

    def test_view_customized_analytics_by_months(self):
        self.customized_analytics['dimensions'] = self.months
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.customized_analytics)
        self.post_request.POST = query_dict
        self.post_request.user = self.admin
        self.assertTrue(view_customized_analytics(self.post_request).status_code == 200)

    def test_view_customized_analytics_by_days(self):
        self.customized_analytics['dimensions'] = self.days
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.customized_analytics)
        self.post_request.POST = query_dict
        self.post_request.user = self.admin
        self.assertTrue(view_customized_analytics(self.post_request).status_code == 200)

    def test_view_customized_analytics_missing_start_date(self):
        del self.customized_analytics['start_date']
        self.customized_analytics['dimensions'] = self.days
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.customized_analytics)
        self.post_request.POST = query_dict
        self.post_request.user = self.admin
        response = view_customized_analytics(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_view_customized_analytics_missing_end_date(self):
        del self.customized_analytics['end_date']
        self.customized_analytics['dimensions'] = self.days
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.customized_analytics)
        self.post_request.POST = query_dict
        self.post_request.user = self.admin
        response = view_customized_analytics(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_view_customized_analytics_missing_dimensions(self):
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.customized_analytics)
        self.post_request.POST = query_dict
        self.post_request.user = self.admin
        response = view_customized_analytics(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_view_customized_analytics_invalid_dates_range(self):
        self.customized_analytics['start_date'] = str(self.today)
        self.customized_analytics['end_date'] = str(self.past)
        self.customized_analytics['dimensions'] = self.months
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.customized_analytics)
        self.post_request.POST = query_dict
        self.post_request.user = self.admin
        response = view_customized_analytics(self.post_request)
        self.assertTrue(response.status_code == self.error_code)
        self.customized_analytics['dimensions'] = self.days
        response = view_customized_analytics(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_view_customized_analytics_missing_args(self):
        for i in range(10):
            random_num = random.randint(1, 2)
            if random_num == 1:
                self.customized_analytics['dimensions'] = self.days
            else:
                self.customized_analytics['dimensions'] = self.months
            dict_copy = self.customized_analytics.copy()
            args_to_remove = []
            for j in range(random.randint(1, len(self.customized_analytics.keys()) - 1)):
                args_to_remove.append(list(self.customized_analytics.keys())[j])
            for j in range(len(args_to_remove)):
                del self.customized_analytics[args_to_remove[j]]
            query_dict = QueryDict('', mutable=True)
            query_dict.update(self.customized_analytics)
            self.post_request.POST = query_dict
            self.post_request.user = self.admin
            response = view_customized_analytics(self.post_request)
            self.assertTrue(response.status_code == self.error_code)
            self.customized_analytics = dict_copy.copy()

    def test_check_if_customized_analytics_is_valid(self):
        self.customized_analytics['dimensions'] = self.months
        self.assertTrue(check_if_customized_analytics_is_valid(self.customized_analytics)[0])
        self.customized_analytics['dimensions'] = self.days
        self.assertTrue(check_if_customized_analytics_is_valid(self.customized_analytics)[0])

    def test_check_if_customized_analytics_is_valid_missing_dimensions(self):
        self.assertFalse(check_if_customized_analytics_is_valid(self.customized_analytics)[0])

    def test_check_valid_dates(self):
        self.assertTrue(len(check_valid_dates(self.customized_analytics)) == 0)

    def test_check_valid_dates_missing_start_date(self):
        del self.customized_analytics['start_date']
        self.assertTrue(len(check_valid_dates(self.customized_analytics)) > 0)

    def test_check_valid_dates_missing_end_date(self):
        del self.customized_analytics['end_date']
        self.assertTrue(len(check_valid_dates(self.customized_analytics)) > 0)

    def test_check_valid_dates_invalid_dates_range(self):
        self.customized_analytics['start_date'] = str(self.today)
        self.customized_analytics['end_date'] = str(self.past)
        self.assertTrue(len(check_valid_dates(self.customized_analytics)) > 0)

    def test_view_top_n_claims(self):
        from claims.views import view_claim
        ten_claims_ids = []
        self.get_request.user = self.admin
        for i in range(random.randint(40, 50)):
            claim = Claim(user_id=self.admin.id,
                          claim='claim' + str(i),
                          category='category' + str(i),
                          authenticity_grade=random.randint(1, 100))
            claim.save()
            if not len(ten_claims_ids) == 10:
                ten_claims_ids.append(claim.id)
        for i in range(random.randint(10, 20)):
            for claim_id in ten_claims_ids:
                view_claim(self.get_request, claim_id)
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.top_claims)
        self.post_request.POST = query_dict
        self.post_request.user = self.admin
        self.assertTrue(view_top_n_claims(self.post_request).status_code == 200)

    def test_view_top_n_claims_missing_start_date(self):
        del self.top_claims['start_date']
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.top_claims)
        self.post_request.POST = query_dict
        self.post_request.user = self.admin
        response = view_top_n_claims(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_view_top_n_claims_missing_end_date(self):
        del self.top_claims['end_date']
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.top_claims)
        self.post_request.POST = query_dict
        self.post_request.user = self.admin
        response = view_top_n_claims(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_view_top_n_claims_invalid_dates_range(self):
        self.top_claims['start_date'] = str(self.today)
        self.top_claims['end_date'] = str(self.past)
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.top_claims)
        self.post_request.POST = query_dict
        self.post_request.user = self.admin
        response = view_top_n_claims(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_view_top_n_claims_missing_num_of_claims(self):
        del self.top_claims['n']
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.top_claims)
        self.post_request.POST = query_dict
        self.post_request.user = self.admin
        response = view_top_n_claims(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_view_top_n_claims_missing_args(self):
        for i in range(10):
            self.top_claims['n'] = str(random.randint(1, 10))
            dict_copy = self.top_claims.copy()
            args_to_remove = []
            for j in range(random.randint(1, len(self.top_claims.keys()) - 1)):
                args_to_remove.append(list(self.top_claims.keys())[j])
            for j in range(len(args_to_remove)):
                del self.top_claims[args_to_remove[j]]
            query_dict = QueryDict('', mutable=True)
            query_dict.update(self.top_claims)
            self.post_request.POST = query_dict
            self.post_request.user = self.admin
            response = view_top_n_claims(self.post_request)
            self.assertTrue(response.status_code == self.error_code)
            self.top_claims = dict_copy.copy()

    def test_check_if_top_claims_is_valid(self):
        self.assertTrue(check_if_top_claims_is_valid(self.top_claims)[0])

    def test_check_if_top_claims_is_valid_missing_num_of_claims(self):
        del self.top_claims['n']
        self.assertFalse(check_if_top_claims_is_valid(self.top_claims)[0])

    def test_check_if_top_claims_is_valid_invalid_format_num_of_claims(self):
        import string
        letters = string.ascii_lowercase
        self.top_claims['n'] = ''.join(random.choice(letters) for i in range(random.randint(1, 10)))
        self.assertFalse(check_if_top_claims_is_valid(self.top_claims)[0])

    def test_check_if_top_claims_is_valid_num_of_claims_invalid_value_num_of_claims(self):
        self.top_claims['n'] = str(random.randint(1, 11) * -1)
        self.assertFalse(check_if_top_claims_is_valid(self.top_claims)[0])
        self.top_claims['n'] = str(random.randint(11, 300))
        self.assertFalse(check_if_top_claims_is_valid(self.top_claims)[0])

    def test_check_if_top_claims_is_valid_invalid_dates_range(self):
        self.top_claims['start_date'] = str(self.today)
        self.top_claims['end_date'] = str(self.past)
        self.assertFalse(check_if_top_claims_is_valid(self.top_claims)[0])

    def test_get_claim_as_json(self):
        num_of_claims = random.randint(1, 10)
        claims_arr = []
        for i in range(num_of_claims):
            claim = Claim(user_id=self.admin.id,
                          claim='claim' + str(i),
                          category='category' + str(i),
                          authenticity_grade=random.randint(1, 100))
            claim.save()
            claims_arr.append(claim)
        for claim in claims_arr:
            claim_json = get_claim_as_json(claim)
            self.assertTrue(claim_json['id'] == claim.id)
            self.assertTrue(claim_json['claim'] == claim.claim)
