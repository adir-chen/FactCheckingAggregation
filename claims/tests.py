from django.http import HttpRequest, QueryDict
from django.test import TestCase
from claims.models import Claim
from claims.views import add_claim, get_all_claims, reset_claims, get_claim_by_id, get_newest_claims
from users.models import User


class ClaimTests(TestCase):
    def setUp(self):
        self.claim_1 = Claim(title='claim1', category='category1', authentic_grade=-1)
        self.claim_2 = Claim(title='claim2', category='category2', authentic_grade=-1)
        self.claim_3 = Claim(title='claim3', category='category3', authentic_grade=-1)
        self.claim_1.save()
        self.claim_2.save()
        self.claim_3.save()

    def tearDown(self):
        pass

    def test_get_all_claims_test_1(self):
        self.assertTrue(len(get_all_claims()) == 3)

    def test_get_all_claims_test_2(self):
        len_claims = len(get_all_claims())
        claim_4 = Claim(title='claim4', category='category4', authentic_grade=-1)
        claim_4.save()
        self.assertTrue(len(Claim.objects.all()) == len_claims + 1)

    def test_reset_claims(self):
        reset_claims()
        self.assertTrue(len(get_all_claims()) == 0)

    def test_get_claim_by_id_test_1(self):
        claim_1 = get_claim_by_id(1)
        self.assertTrue(claim_1.title == self.claim_1.title)
        self.assertTrue(claim_1.category == self.claim_1.category)
        self.assertTrue(claim_1.authentic_grade == self.claim_1.authentic_grade)

        claim_2 = get_claim_by_id(2)
        self.assertTrue(claim_2.title == self.claim_2.title)
        self.assertTrue(claim_2.category == self.claim_2.category)
        self.assertTrue(claim_2.authentic_grade == self.claim_2.authentic_grade)

        claim_3 = get_claim_by_id(3)
        self.assertTrue(claim_3.title == self.claim_3.title)
        self.assertTrue(claim_3.category == self.claim_3.category)
        self.assertTrue(claim_3.authentic_grade == self.claim_3.authentic_grade)

        self.assertTrue(get_claim_by_id(4) is None)

    def test_get_claim_by_id_test_2(self):
        claim_4 = Claim(title='claim4', category='category4', authentic_grade=-1)
        claim_4.save()
        claim_4_info = get_claim_by_id(4)
        self.assertTrue(claim_4_info.title == claim_4.title)
        self.assertTrue(claim_4_info.category == claim_4.category)
        self.assertTrue(claim_4_info.authentic_grade == claim_4_info.authentic_grade)

    def test_add_claim(self):
        user = User(username="User1", email='user1@gmail.com', state='Regular', reputation=-1)
        user.save()
        len_claims = len(Claim.objects.all())
        claim = Claim(title='claim4', category='category4', authentic_grade=-1, image_src='img-src')
        request = HttpRequest()
        request.method = 'POST'
        dict = {'username':'User1', 'claim':claim.title, 'title':'title', 'description':'description',
                        'url':'url', 'verdict_date':'10.10.2010', 'tags':'tags',
                        'label':'label', 'category':claim.category, 'img_src': claim.image_src}
        query_dict = QueryDict('', mutable=True)
        query_dict.update(dict)
        request.POST = query_dict
        add_claim(request)
        self.assertTrue(len(Claim.objects.all()) == len_claims + 1)
        claim_4 = get_claim_by_id(4)
        self.assertTrue(claim_4.title == 'claim4')
        self.assertTrue(claim_4.category == 'category4')
        self.assertTrue(claim_4.authentic_grade == -1)

    def test_get_newest_claims(self):
        for i in range(4, 24):
            claim = Claim(title='claim' + str(i), category='category ' + str(i), authentic_grade=-1)
            claim.save()
        for claim in get_newest_claims():
            self.assertFalse(claim.title == self.claim_1.title)
            self.assertFalse(claim.category == self.claim_1.category)
            self.assertFalse(claim.title == self.claim_2.title)
            self.assertFalse(claim.category == self.claim_2.category)
            self.assertFalse(claim.title == self.claim_3.title)
            self.assertFalse(claim.category == self.claim_3.category)
        self.assertTrue(len(get_newest_claims()) == 20)

    #ToDo: test view_claim, view_home, add_claim