from django.http import HttpRequest, QueryDict, Http404
from django.test import TestCase
from claims.models import Claim
from claims.views import view_claim, view_home, add_claim, get_all_claims, reset_claims, get_claim_by_id, get_newest_claims, is_valid_verdict_date, check_if_claim_is_valid
from comments.models import Comment
from users.models import User


class ClaimTests(TestCase):
    def setUp(self):
        self.claim_1 = Claim(claim='claim1', category='category1', authentic_grade=-1)
        self.claim_2 = Claim(claim='claim2', category='category2', authentic_grade=-1)
        self.claim_3 = Claim(claim='claim3', category='category3', authentic_grade=-1)
        self.claim_1.save()
        self.claim_2.save()
        self.claim_3.save()
        self.user = User(username="User1", email='user1@gmail.com', state='Regular', reputation=-1)
        self.user.save()
        self.dict = {'username': 'User1', 'claim': 'claim4', 'title': 'title', 'description': 'description',
                        'url': 'url', 'verdict_date': '10/10/2010', 'tags': 'tags',
                        'label': 'label', 'category': 'category4', 'img_src': 'img_src'}

    def tearDown(self):
        pass

    def test_get_all_claims(self):
        self.assertTrue(len(get_all_claims()) == 3)

    def test_get_all_claims_after_add_claim(self):
        len_claims = len(get_all_claims())
        claim_4 = Claim(claim='claim4', category='category4', authentic_grade=-1)
        claim_4.save()
        self.assertTrue(len(Claim.objects.all()) == len_claims + 1)

    def test_reset_claims(self):
        reset_claims()
        self.assertTrue(len(get_all_claims()) == 0)

    def test_get_claim_by_id(self):
        claim_1 = get_claim_by_id(1)
        self.assertTrue(claim_1.claim == self.claim_1.claim)
        self.assertTrue(claim_1.category == self.claim_1.category)
        self.assertTrue(claim_1.authentic_grade == self.claim_1.authentic_grade)

        claim_2 = get_claim_by_id(2)
        self.assertTrue(claim_2.claim == self.claim_2.claim)
        self.assertTrue(claim_2.category == self.claim_2.category)
        self.assertTrue(claim_2.authentic_grade == self.claim_2.authentic_grade)

        claim_3 = get_claim_by_id(3)
        self.assertTrue(claim_3.claim == self.claim_3.claim)
        self.assertTrue(claim_3.category == self.claim_3.category)
        self.assertTrue(claim_3.authentic_grade == self.claim_3.authentic_grade)

    def test_get_claim_by_invalid_id(self):
        self.assertTrue(get_claim_by_id(4) is None)

    def test_get_claim_by_id_after_add_claim(self):
        claim_4 = Claim(claim='claim4', category='category4', authentic_grade=-1)
        claim_4.save()
        claim_4_info = get_claim_by_id(4)
        self.assertTrue(claim_4_info.claim == claim_4.claim)
        self.assertTrue(claim_4_info.category == claim_4.category)
        self.assertTrue(claim_4_info.authentic_grade == claim_4_info.authentic_grade)

    def test_add_claim(self):
        len_claims = len(Claim.objects.all())
        request = HttpRequest()
        request.method = 'POST'
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.dict)
        request.POST = query_dict
        add_claim(request)
        self.assertTrue(len(Claim.objects.all()) == len_claims + 1)
        claim_4 = get_claim_by_id(4)
        self.assertTrue(claim_4.claim == self.dict['claim'])
        self.assertTrue(claim_4.category == self.dict['category'])
        self.assertTrue(claim_4.authentic_grade == -1)

    def test_add_claim_by_invalid_user(self):
        len_claims = len(Claim.objects.all())
        request = HttpRequest()
        request.method = 'POST'
        self.dict['username'] = 'User2'
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.dict)
        request.POST = query_dict
        self.assertRaises(Exception, add_claim, request)
        self.assertTrue(len(Claim.objects.all()) == len_claims)
        self.assertTrue(get_claim_by_id(4) is None)

    def test_add_existing_claim(self):
        len_claims = len(Claim.objects.all())
        request = HttpRequest()
        request.method = 'POST'
        self.dict['claim'] = 'claim1'
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.dict)
        request.POST = query_dict
        self.assertRaises(Exception, add_claim, request)
        self.assertTrue(len(Claim.objects.all()) == len_claims)
        self.assertTrue(get_claim_by_id(4) is None)

    def test_add_claim_missing_args(self):
        del self.dict['username']
        del self.dict['claim']
        del self.dict['title']
        len_claims = len(Claim.objects.all())
        request = HttpRequest()
        request.method = 'POST'
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.dict)
        request.POST = query_dict
        self.assertRaises(Exception, add_claim, request)
        self.assertTrue(len(Claim.objects.all()) == len_claims)
        self.assertTrue(get_claim_by_id(4) is None)

    def test_get_newest_claims_many_claims(self):
        for i in range(4, 24):
            claim = Claim(claim='claim' + str(i), category='category ' + str(i), authentic_grade=-1)
            claim.save()
        for claim in get_newest_claims():
            self.assertFalse(claim.claim == self.claim_1.claim)
            self.assertFalse(claim.category == self.claim_1.category)
            self.assertFalse(claim.claim == self.claim_2.claim)
            self.assertFalse(claim.category == self.claim_2.category)
            self.assertFalse(claim.claim == self.claim_3.claim)
            self.assertFalse(claim.category == self.claim_3.category)
        self.assertTrue(len(get_newest_claims()) == 20)

    def test_get_newest_claims_not_many_claims(self):
        result = get_newest_claims()
        self.assertTrue(result[0].claim == self.claim_3.claim)
        self.assertTrue(result[0].category == self.claim_3.category)
        self.assertTrue(result[1].claim == self.claim_2.claim)
        self.assertTrue(result[1].category == self.claim_2.category)
        self.assertTrue(result[2].claim == self.claim_1.claim)
        self.assertTrue(result[2].category == self.claim_1.category)
        self.assertTrue(len(get_newest_claims()) == 3)

    def test_is_valid_verdict_date_valid(self):
        self.assertTrue(is_valid_verdict_date('10/10/2015'))

    def test_is_valid_verdict_date_invalid_format(self):
        self.assertFalse(is_valid_verdict_date('10.10.2015'))

    def test_is_valid_verdict_date_invalid_datetime(self):
        self.assertFalse(is_valid_verdict_date('15/15/2025'))

    def test_check_if_claim_is_valid(self):
        self.assertTrue(check_if_claim_is_valid(self.dict))

    def test_check_if_claim_is_valid_missing_username(self):
        del self.dict['username']
        self.assertFalse(check_if_claim_is_valid(self.dict)[0])

    def test_check_if_claim_is_valid_missing_claim(self):
        del self.dict['claim']
        self.assertFalse(check_if_claim_is_valid(self.dict)[0])

    def test_check_if_claim_is_valid_missing_title(self):
        del self.dict['title']
        self.assertFalse(check_if_claim_is_valid(self.dict)[0])

    def test_check_if_claim_is_valid_missing_description(self):
        del self.dict['description']
        self.assertFalse(check_if_claim_is_valid(self.dict)[0])

    def test_check_if_claim_is_valid_missing_url(self):
        del self.dict['url']
        self.assertFalse(check_if_claim_is_valid(self.dict)[0])

    def test_check_if_claim_is_valid_missing_verdict_date(self):
        del self.dict['verdict_date']
        self.assertFalse(check_if_claim_is_valid(self.dict)[0])

    def test_check_if_claim_is_valid_invalid_verdict_date(self):
        self.dict['verdict_date'] = '1.5.2090'
        self.assertFalse(check_if_claim_is_valid(self.dict)[0])

    def test_check_if_claim_is_valid_missing_tags(self):
        del self.dict['tags']
        self.assertFalse(check_if_claim_is_valid(self.dict)[0])

    def test_check_if_claim_is_valid_missing_label(self):
        del self.dict['label']
        self.assertFalse(check_if_claim_is_valid(self.dict)[0])

    def test_check_if_claim_is_valid_missing_category(self):
        del self.dict['category']
        self.assertFalse(check_if_claim_is_valid(self.dict)[0])

    def test_check_if_claim_is_valid_missing_img_src(self):
        del self.dict['img_src']
        self.assertFalse(check_if_claim_is_valid(self.dict)[0])

    def test_add_claim_get(self):
        request = HttpRequest()
        request.method = 'GET'
        self.assertRaises(Http404, add_claim, request)

    def test_view_claim_valid(self):
        request = HttpRequest()
        request.method = 'GET'
        response = view_claim(request, self.claim_1.id)
        self.assertTrue(response.status_code == 200)

    def test_view_claim_with_comment(self):
        comment_1 = Comment(claim_id=self.claim_1.id, user_id=self.user.id, title=self.claim_1.claim,
                                 description='description1', url='url1', verdict_date='verdict_date1',
                                 tags='tags1', label='label1', pos_votes=0, neg_votes=0)
        comment_1.save()
        request = HttpRequest()
        request.method = 'GET'
        response = view_claim(request, self.claim_1.id)
        self.assertTrue(response.status_code == 200)

    def test_view_claim_invalid(self):
        request = HttpRequest()
        request.method = 'GET'
        self.assertRaises(Http404, view_claim, request, 4)

    def test_view_home_valid(self):
        request = HttpRequest()
        request.method = 'GET'
        response = view_home(request)
        self.assertTrue(response.status_code == 200)
