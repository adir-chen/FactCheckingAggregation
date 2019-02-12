from django.http import HttpRequest, QueryDict, Http404
from django.test import TestCase
from claims.models import Claim
from claims.views import add_claim, check_if_claim_is_valid, is_valid_verdict_date, \
    get_all_claims, get_newest_claims, get_category_for_claim, get_tags_for_claim,\
    get_claim_by_id, view_claim, view_home, logout_view
from comments.models import Comment
from users.models import User
import random
import datetime


class ClaimTests(TestCase):
    def setUp(self):
        self.claim_1 = Claim(claim='Sniffing rosemary increases human memory by up to 75 percent',
                             category='Science',
                             tags="sniffing human memory",
                             authenticity_grade=0)
        self.claim_2 = Claim(claim='A photograph shows the largest U.S. flag ever made, displayed in front of Hoover Dam',
                             category='Fauxtography',
                             tags="photograph U.S. flag",
                             authenticity_grade=0)
        self.claim_3 = Claim(claim='Virginia Gov. Ralph Northam "stated he would execute a baby after birth',
                             category='Politics',
                             tags="Virginia baby birth",
                             authenticity_grade=0)
        self.claim_4 = Claim(claim='Kurt Russell once claimed Democrats had vowed to abolish several constitutional amendments and labelled them "enemies of the state',
                             category='Junk News',
                             tags="Kurt Russell constitutional democrat",
                             authenticity_grade=0)
        self.claim_1.save()
        self.claim_2.save()
        self.claim_3.save()
        self.user = User(username="User1", email='user1@gmail.com')
        self.user.save()
        self.dict = {'user_id': self.user.id,
                     'claim': self.claim_4.claim,
                     'title': 'Did Kurt Russell Say Democrats Should Be Declared ‘Enemies of the State’?',
                     'description': 'A notorious producer of junk news recycled an old quotation attributed to the veteran Hollywood actor.',
                     'url': "https://www.snopes.com/fact-check/kurt-russell-democrats/",
                     'verdict_date': '11/02/2019',
                     'tags': self.claim_4.tags,
                     'category': self.claim_4.category,
                     'label': 'False',
                     'img_src': 'img_src'}

    def tearDown(self):
        pass

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
        self.assertTrue(claim_4.claim == self.claim_4.claim)
        self.assertTrue(claim_4.category == self.claim_4.category)
        self.claim_4.tags = "Kurt, Russell, constitutional, democrat"
        self.assertTrue(claim_4.tags == self.claim_4.tags)
        self.assertTrue(claim_4.authenticity_grade == 0)

    def test_add_claim_by_invalid_user(self):
        len_claims = len(Claim.objects.all())
        request = HttpRequest()
        request.method = 'POST'
        self.dict['user_id'] = 2
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
        self.dict['claim'] = self.claim_1.claim
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.dict)
        request.POST = query_dict
        self.assertRaises(Exception, add_claim, request)
        self.assertTrue(len(Claim.objects.all()) == len_claims)
        self.assertTrue(get_claim_by_id(4) is None)

    def test_add_claim_missing_args(self):
        for i in range(10):
            dict_copy = self.dict
            args_to_remove = []
            for j in range(random.randint(0, len(self.dict.keys()) - 1)):
                args_to_remove.append(list(self.dict.keys())[j])
            for j in range(len(args_to_remove)):
                del self.dict[args_to_remove[j]]
            len_claims = len(Claim.objects.all())
            request = HttpRequest()
            request.method = 'POST'
            query_dict = QueryDict('', mutable=True)
            query_dict.update(self.dict)
            request.POST = query_dict
            self.assertRaises(Http404, add_claim, request)
            self.assertTrue(len(Claim.objects.all()) == len_claims)
            self.assertTrue(get_claim_by_id(4) is None)
            self.dict = dict_copy

    def test_add_claim_get(self):
        request = HttpRequest()
        request.method = 'GET'
        self.assertRaises(Http404, add_claim, request)

    def test_check_if_claim_is_valid(self):
        self.assertTrue(check_if_claim_is_valid(self.dict))

    def test_check_if_claim_is_valid_missing_username(self):
        del self.dict['user_id']
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
        self.dict['verdict_date'] = datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=7),'%d/%m/%Y')
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

    def test_is_valid_verdict_date_valid(self):
        self.assertTrue(is_valid_verdict_date(datetime.datetime.strftime(datetime.datetime.now() - datetime.timedelta(days=1),'%d/%m/%Y')))

    def test_is_valid_verdict_date_invalid_format(self):
        self.assertFalse(is_valid_verdict_date(datetime.datetime.strftime(datetime.datetime.now() - datetime.timedelta(days=1),'%d.%m.%Y')))

    def test_is_valid_verdict_date_invalid_datetime(self):
        self.assertFalse(is_valid_verdict_date(datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=7),'%d/%m/%Y')))

    def test_get_all_claims(self):
        self.assertTrue(len(get_all_claims()) == 3)

    def test_get_all_claims_after_add_claim(self):
        len_claims = len(get_all_claims())
        self.claim_4.save()
        self.assertTrue(len(Claim.objects.all()) == len_claims + 1)

    def test_get_newest_claims_many_claims(self):
        for i in range(4, 24):
            claim = Claim(claim='claim' + str(i), category='category ' + str(i),
                          tags='claim' + str(i), authenticity_grade=0)
            claim.save()
        for claim in get_newest_claims():
            self.assertFalse(claim.claim == self.claim_1.claim)
            self.assertFalse(claim.category == self.claim_1.category)
            self.assertFalse(claim.tags == self.claim_1.tags)

            self.assertFalse(claim.claim == self.claim_2.claim)
            self.assertFalse(claim.category == self.claim_2.category)
            self.assertFalse(claim.tags == self.claim_2.tags)

            self.assertFalse(claim.claim == self.claim_3.claim)
            self.assertFalse(claim.category == self.claim_1.category)
            self.assertFalse(claim.tags == self.claim_3.tags)
        self.assertTrue(len(get_newest_claims()) == 20)

    def test_get_newest_claims_not_many_claims(self):
        result = get_newest_claims()
        self.assertTrue(result[0].claim == self.claim_3.claim)
        self.assertTrue(result[0].category == self.claim_3.category)
        self.claim_3.tags = 'Virginia, baby, birth'
        self.assertFalse(result[0].tags == self.claim_3.tags)
        self.assertTrue(result[1].claim == self.claim_2.claim)
        self.assertTrue(result[1].category == self.claim_2.category)
        self.claim_2.tags = 'photograph, U.S., flag'
        self.assertFalse(result[1].tags == self.claim_2.tags)
        self.assertTrue(result[2].claim == self.claim_1.claim)
        self.assertTrue(result[2].category == self.claim_1.category)
        self.claim_1.tags = 'sniffing, human ,memory'
        self.assertFalse(result[2].tags == self.claim_1.tags)
        self.assertTrue(len(get_newest_claims()) == 3)

    def test_get_category_for_claim(self):
        self.assertTrue(get_category_for_claim(self.claim_1.id) == self.claim_1.category)
        self.assertTrue(get_category_for_claim(self.claim_2.id) == self.claim_2.category)
        self.assertTrue(get_category_for_claim(self.claim_3.id) == self.claim_3.category)

    def test_get_category_for_claim_new_claim(self):
        self.claim_4.save()
        self.assertTrue(get_category_for_claim(self.claim_4.id) == self.claim_4.category)

    def test_get_category_for_claim_invalid_claim(self):
        self.assertTrue(get_category_for_claim(self.claim_4.id) is None)

    def test_get_tags_for_claim(self):
        self.assertTrue(get_tags_for_claim(self.claim_1.id) == self.claim_1.tags)
        self.assertTrue(get_tags_for_claim(self.claim_2.id) == self.claim_2.tags)
        self.assertTrue(get_tags_for_claim(self.claim_3.id) == self.claim_3.tags)

    def test_get_tags_for_claim_new_claim(self):
        self.claim_4.save()
        self.assertTrue(get_tags_for_claim(self.claim_4.id) == self.claim_4.tags)

    def test_get_tags_for_claim_invalid_claim(self):
        self.assertTrue(get_tags_for_claim(self.claim_4.id) is None)

    def test_get_claim_by_id(self):
        claim_1 = get_claim_by_id(1)
        self.assertTrue(claim_1.claim == self.claim_1.claim)
        self.assertTrue(claim_1.category == self.claim_1.category)
        self.assertTrue(claim_1.tags == self.claim_1.tags)
        self.assertTrue(claim_1.authenticity_grade == self.claim_1.authenticity_grade)

        claim_2 = get_claim_by_id(2)
        self.assertTrue(claim_2.claim == self.claim_2.claim)
        self.assertTrue(claim_2.category == self.claim_2.category)
        self.assertTrue(claim_2.tags == self.claim_2.tags)
        self.assertTrue(claim_2.authenticity_grade == self.claim_2.authenticity_grade)

        claim_3 = get_claim_by_id(3)
        self.assertTrue(claim_3.claim == self.claim_3.claim)
        self.assertTrue(claim_3.category == self.claim_3.category)
        self.assertTrue(claim_3.tags == self.claim_3.tags)
        self.assertTrue(claim_3.authenticity_grade == self.claim_3.authenticity_grade)

    def test_get_claim_by_id_after_add_claim(self):
        self.claim_4.save()
        claim_4_info = get_claim_by_id(4)
        self.assertTrue(claim_4_info.claim == self.claim_4.claim)
        self.assertTrue(claim_4_info.category == self.claim_4.category)
        self.assertTrue(claim_4_info.tags == self.claim_4.tags)
        self.assertTrue(claim_4_info.authenticity_grade == self.claim_4.authenticity_grade)

    def test_get_claim_by_invalid_id(self):
        self.assertTrue(get_claim_by_id(4) is None)

    def test_view_claim_valid(self):
        request = HttpRequest()
        request.method = 'GET'
        response = view_claim(request, self.claim_1.id)
        self.assertTrue(response.status_code == 200)

    def test_view_claim_with_comment(self):
        comment_1 = Comment(claim_id=self.claim_1.id,
                            user_id=self.user.id,
                            title=self.claim_1.claim,
                            description='description1',
                            url='url1',
                            verdict_date='12/02/2019',
                            label='label1',
                            pos_votes=0,
                            neg_votes=0)
        comment_1.save()
        request = HttpRequest()
        request.method = 'GET'
        response = view_claim(request, self.claim_1.id)
        self.assertTrue(response.status_code == 200)

    def test_view_claim_invalid(self):
        request = HttpRequest()
        request.method = 'GET'
        self.assertRaises(Http404, view_claim, request, 4)

    # def test_view_home_valid_user_authenticated(self):
    #     return NotImplemented()

    def test_view_home_valid_user_not_authenticated(self):
        request = HttpRequest()
        request.method = 'GET'
        response = view_home(request)
        self.assertTrue(response.status_code == 200)

    # def test_logout_view(self):
    #     return NotImplemented()
