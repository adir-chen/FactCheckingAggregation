from django.http import HttpRequest, QueryDict, Http404
from django.test import TestCase, Client
from claims.models import Claim
from claims.views import add_claim, check_if_claim_is_valid, post_above_limit, \
    get_all_claims, get_newest_claims, get_claim_by_id, get_category_for_claim, get_tags_for_claim,\
    view_claim, view_home, get_users_images_for_claims, logout_view, add_claim_page, export_claims_page, \
    edit_claim, check_claim_new_fields, delete_claim, check_if_delete_claim_is_valid, \
    handler_400, handler_403, handler_404, handler_500, about_page
from comments.models import Comment
from users.models import User, Users_Images, Scrapers
import random
import datetime


class ClaimTests(TestCase):
    def setUp(self):
        self.user = User(username="User1", email='user1@gmail.com')
        self.user.save()
        self.password = User.objects.make_random_password()
        self.scraper = User.objects.create_user(username="Scraper", password=self.password)
        self.user_image = Users_Images(user_id=self.user, user_img='user_img')
        self.user_image.save()

        self.scraper_image = Users_Images(user_id=self.scraper, user_img='scraper_img')
        self.scraper_image.save()
        self.scraper_details = Scrapers(scraper_name=self.scraper.username, scraper_id=self.scraper)
        self.scraper_details.save()

        self.num_of_saved_users = 2
        self.claim_1 = Claim(user_id=self.user.id,
                             claim='Sniffing rosemary increases human memory by up to 75 percent',
                             category='Science',
                             tags="sniffing human memory",
                             authenticity_grade=0,
                             image_src='image_1')
        self.claim_2 = Claim(user_id=self.user.id,
                             claim='A photograph shows the largest U.S. flag ever made, displayed in front of Hoover Dam',
                             category='Fauxtography',
                             tags="photograph U.S. flag",
                             authenticity_grade=0,
                             image_src='image_2')
        self.claim_3 = Claim(user_id=self.user.id,
                             claim='Virginia Gov. Ralph Northam "stated he would execute a baby after birth',
                             category='Politics',
                             tags="Virginia baby birth",
                             authenticity_grade=0,
                             image_src='image_3')
        self.claim_4 = Claim(user_id=self.user.id,
                             claim='Kurt Russell once claimed Democrats had vowed to abolish several constitutional amendments and labelled them "enemies of the state',
                             category='Junk News',
                             tags="Kurt Russell constitutional democrat",
                             authenticity_grade=0,
                             image_src='image_4')
        self.claim_1.save()
        self.claim_2.save()
        self.claim_3.save()
        self.comment_1 = Comment(claim_id=self.claim_1.id,
                                 user_id=self.user.id,
                                 title=self.claim_1.claim,
                                 description='description1',
                                 url='url1',
                                 verdict_date=datetime.date.today() - datetime.timedelta(days=random.randint(0, 10)),
                                 label='label1')
        self.comment_2 = Comment(claim_id=self.claim_2.id,
                                 user_id=self.user.id,
                                 title=self.claim_2.claim,
                                 description='description2',
                                 url='url2',
                                 verdict_date=datetime.date.today() - datetime.timedelta(days=random.randint(0, 10)),
                                 label='label2')
        self.comment_3 = Comment(claim_id=self.claim_3.id,
                                 user_id=self.user.id,
                                 title=self.claim_3.claim,
                                 description='description3',
                                 url='url3',
                                 verdict_date=datetime.date.today() - datetime.timedelta(days=random.randint(0, 10)),
                                 label='label3')

        self.comment_1.save()
        self.comment_2.save()
        self.comment_3.save()
        self.num_of_saved_claims = 3
        self.new_claim_details = {'claim': self.claim_4.claim,
                                  'title': 'Did Kurt Russell Say Democrats Should Be Declared ‘Enemies of the State’?',
                                  'description': 'A notorious producer of junk news recycled an old quotation attributed to the veteran Hollywood actor.',
                                  'url': "https://www.snopes.com/fact-check/kurt-russell-democrats/",
                                  'add_comment': "true",
                                  'verdict_date': datetime.datetime.strptime(str(datetime.date.today() - datetime.timedelta(days=random.randint(0, 10))), '%Y-%m-%d').strftime('%d/%m/%Y'),
                                  'tags': self.claim_4.tags,
                                  'category': self.claim_4.category,
                                  'label': 'False',
                                  'img_src': 'img_src'}
        self.post_request = HttpRequest()
        self.post_request.method = 'POST'
        self.update_claim_details = {'claim_id': self.claim_1.id,
                                     'claim': self.claim_1.claim,
                                     'category': self.claim_1.category,
                                     'tags': self.claim_1.tags,
                                     'image_src': self.claim_1.image_src}

    def tearDown(self):
        pass

    def test_add_claim(self):
        len_claims = len(Claim.objects.all())
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.new_claim_details)
        self.post_request.POST = query_dict
        self.post_request.user = self.user
        add_claim(self.post_request)
        self.assertTrue(len(Claim.objects.all()) == len_claims + 1)
        claim_4 = get_claim_by_id(4)
        self.assertTrue(claim_4.claim == self.claim_4.claim)
        self.assertTrue(claim_4.category == self.claim_4.category)
        self.claim_4.tags = "Kurt, Russell, constitutional, democrat"
        self.assertTrue(claim_4.tags == self.claim_4.tags)
        self.assertTrue(claim_4.authenticity_grade == 0)

    def test_add_claim_by_user_not_authenticated(self):
        from django.contrib.auth.models import AnonymousUser
        len_claims = len(Claim.objects.all())
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.new_claim_details)
        self.post_request.POST = query_dict
        self.post_request.user = AnonymousUser()
        self.assertRaises(Http404, add_claim, self.post_request)
        self.assertTrue(len(Claim.objects.all()) == len_claims)
        self.assertTrue(get_claim_by_id(self.num_of_saved_claims + 1) is None)

    def test_add_claim_by_scraper(self):
        from django.contrib.auth.models import AnonymousUser
        len_claims = len(Claim.objects.all())
        self.new_claim_details['user_id'] = self.scraper.id
        self.new_claim_details['username'] = self.scraper.username
        self.new_claim_details['password'] = self.password
        self.post_request.user = AnonymousUser()
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.new_claim_details)
        self.post_request.POST = query_dict
        self.assertTrue(add_claim(self.post_request).status_code == 200)
        self.assertTrue(len(Claim.objects.all()) == len_claims + 1)
        self.assertTrue(get_claim_by_id(self.num_of_saved_claims + 1))

    def test_add_existing_claim(self):
        len_claims = len(Claim.objects.all())
        self.new_claim_details['claim'] = self.claim_1.claim
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.new_claim_details)
        self.post_request.POST = query_dict
        self.post_request.user = self.user
        self.assertRaises(Exception, add_claim, self.post_request)
        self.assertTrue(len(Claim.objects.all()) == len_claims)
        self.assertTrue(get_claim_by_id(self.num_of_saved_claims + 1) is None)

    def test_add_claim_with_invalid_comment(self):
        comment_fields = ['title', 'description', 'url', 'verdict_date', 'label']
        len_claims = len(Claim.objects.all())
        for i in range(len(comment_fields)):
            del self.new_claim_details[comment_fields[i]]
            query_dict = QueryDict('', mutable=True)
            query_dict.update(self.new_claim_details)
            self.post_request.POST = query_dict
            self.post_request.user = self.user
            self.assertRaises(Exception, add_claim, self.post_request)
            self.assertTrue(len(Claim.objects.all()) == len_claims)
            self.assertTrue(get_claim_by_id(self.num_of_saved_claims + 1) is None)

    def test_add_claim_missing_args(self):
        for i in range(10):
            dict_copy = self.new_claim_details.copy()
            args_to_remove = []
            for j in range(random.randint(1, len(self.new_claim_details.keys()) - 1)):
                args_to_remove.append(list(self.new_claim_details.keys())[j])
            for j in range(len(args_to_remove)):
                del self.new_claim_details[args_to_remove[j]]
            len_claims = len(Claim.objects.all())
            query_dict = QueryDict('', mutable=True)
            query_dict.update(self.new_claim_details)
            self.post_request.POST = query_dict
            self.post_request.user = self.user
            self.assertRaises(Exception, add_claim, self.post_request)
            self.assertTrue(len(Claim.objects.all()) == len_claims)
            self.assertTrue(get_claim_by_id(self.num_of_saved_claims + 1) is None)
            self.new_claim_details = dict_copy.copy()

    def test_add_claim_get(self):
        self.post_request.method = 'GET'
        self.post_request.user = self.user
        self.assertRaises(Http404, add_claim, self.post_request)

    def test_check_if_claim_is_valid(self):
        self.new_claim_details['user_id'] = self.user.id
        self.assertTrue(check_if_claim_is_valid(self.new_claim_details))

    def test_check_if_claim_is_valid_missing_user_id(self):
        self.assertFalse(check_if_claim_is_valid(self.new_claim_details)[0])

    def test_check_if_claim_is_valid_missing_claim(self):
        self.new_claim_details['user_id'] = self.user.id
        del self.new_claim_details['claim']
        self.assertFalse(check_if_claim_is_valid(self.new_claim_details)[0])

    def test_check_if_claim_is_valid_missing_category(self):
        self.new_claim_details['user_id'] = self.user.id
        del self.new_claim_details['category']
        self.assertFalse(check_if_claim_is_valid(self.new_claim_details)[0])

    def test_check_if_claim_is_valid_missing_tags(self):
        self.new_claim_details['user_id'] = self.user.id
        del self.new_claim_details['tags']
        self.assertFalse(check_if_claim_is_valid(self.new_claim_details)[0])

    def test_check_if_claim_is_valid_missing_img_src(self):
        self.new_claim_details['user_id'] = self.user.id
        del self.new_claim_details['img_src']
        self.assertFalse(check_if_claim_is_valid(self.new_claim_details)[0])

    def test_check_if_claim_is_valid_missing_add_comment(self):
        self.new_claim_details['user_id'] = self.user.id
        del self.new_claim_details['add_comment']
        self.assertFalse(check_if_claim_is_valid(self.new_claim_details)[0])

    def test_check_if_claim_is_valid_existing_claim(self):
        self.new_claim_details['user_id'] = self.user.id
        self.new_claim_details['claim'] = self.claim_1.claim
        self.assertFalse(check_if_claim_is_valid(self.new_claim_details)[0])

    def test_check_if_claim_is_valid_invalid_user_id(self):
        self.new_claim_details['user_id'] = self.num_of_saved_users + random.randint(1, 10)
        self.assertFalse(check_if_claim_is_valid(self.new_claim_details)[0])

    def test_check_if_claim_is_valid_post_above_limit(self):
        for i in range(10):
            self.new_claim_details['claim'] = 'claim_' + str(i)
            query_dict = QueryDict('', mutable=True)
            query_dict.update(self.new_claim_details)
            self.post_request.POST = query_dict
            self.post_request.user = self.user
            add_claim(self.post_request)
        self.new_claim_details['user_id'] = self.user.id
        self.new_claim_details['claim'] = 'claim_10'
        self.assertFalse(check_if_claim_is_valid(self.new_claim_details)[0])

    def test_post_above_limit(self):
        self.new_claim_details['user_id'] = self.user.id
        for i in range(10):
            self.assertFalse(post_above_limit(self.new_claim_details['user_id']))
            self.new_claim_details['claim'] = 'claim_' + str(i)
            query_dict = QueryDict('', mutable=True)
            query_dict.update(self.new_claim_details)
            self.post_request.POST = query_dict
            self.post_request.user = self.user
            add_claim(self.post_request)
        self.assertTrue(post_above_limit(self.new_claim_details['user_id']))

    def test_get_all_claims(self):
        self.assertTrue(len(get_all_claims()) == 3)

    def test_get_all_claims_after_add_claim(self):
        len_claims = len(get_all_claims())
        self.claim_4.save()
        self.assertTrue(len(Claim.objects.all()) == len_claims + 1)

    def test_get_newest_claims_many_claims(self):
        for i in range(4, 24):
            claim = Claim(user_id=self.user.id, claim='claim' + str(i), category='category ' + str(i),
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
                            verdict_date=datetime.date.today() - datetime.timedelta(days=random.randint(0, 10)),
                            label='label1')
        comment_1.save()
        request = HttpRequest()
        request.method = 'GET'
        response = view_claim(request, self.claim_1.id)
        self.assertTrue(response.status_code == 200)

    def test_view_claim_invalid(self):
        request = HttpRequest()
        request.method = 'GET'
        self.assertRaises(Http404, view_claim, request, 4)

    def test_view_home_many_claims(self):
        for i in range(4, 24):
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
        request = HttpRequest()
        request.method = 'GET'
        response = view_home(request)
        self.assertTrue(response.status_code == 200)

    def test_view_home_valid_user_authenticated(self):
        client = Client()
        user_1 = User.objects.create_user(username='user1', email='user1@gmail.com', password='user1')
        client.login(username='user1', password='user1')
        request = HttpRequest()
        request.method = 'GET'
        request.user = user_1
        request.session = client.session
        self.assertTrue(view_home(request).status_code == 200)

    def test_view_home_valid_user_not_authenticated(self):
        request = HttpRequest()
        request.method = 'GET'
        response = view_home(request)
        self.assertTrue(response.status_code == 200)

    def test_get_users_images_for_claims_user_with_img(self):
        for claim, user_img in get_users_images_for_claims(Claim.objects.all()).items():
            self.assertTrue(user_img == self.user_image.user_img)

    def test_get_users_images_for_claims_user_without_img(self):
        len_users_images = len(Users_Images.objects.all())
        self.user_2 = User(username="User2", email='user2@gmail.com')
        self.user_2.save()
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.new_claim_details)
        self.post_request.POST = query_dict
        self.post_request.user = self.user_2
        add_claim(self.post_request)
        get_users_images_for_claims(Claim.objects.all())
        self.assertTrue(len(Users_Images.objects.all()) == len_users_images + 1)

    def test_logout_view(self):
        client = Client()
        user_1 = User.objects.create_user(username='user1', email='user1@gmail.com', password='user1')
        client.login(username='user1', password='user1')
        request = HttpRequest()
        request.method = 'GET'
        request.user = user_1
        request.session = client.session
        self.assertTrue(logout_view(request).status_code == 200)

    def test_add_claim_page(self):
        request = HttpRequest()
        request.method = 'GET'
        response = add_claim_page(request)
        self.assertTrue(response.status_code == 200)

    def test_export_claims_page(self):
        request = HttpRequest()
        request.method = 'GET'
        response = export_claims_page(request)
        self.assertTrue(response.status_code == 200)

    def test_edit_claim_valid_with_different_claim(self):
        self.update_claim_details['claim'] = self.claim_1.claim + '_new'
        self.post_request.POST = self.update_claim_details
        self.post_request.user = self.user
        self.assertTrue(edit_claim(self.post_request).status_code == 200)
        self.assertTrue(Claim.objects.filter(id=self.update_claim_details['claim_id'])[0].claim == self.claim_1.claim + '_new')

    def test_edit_claim_with_existing_claim(self):
        self.update_claim_details['claim'] = self.claim_2
        self.post_request.POST = self.update_claim_details
        self.post_request.user = self.user
        self.assertRaises(Exception, edit_claim, self.post_request)

    def test_edit_claim_with_user_not_authenticated(self):
        from django.contrib.auth.models import AnonymousUser
        self.post_request.POST = self.update_claim_details
        self.post_request.user = AnonymousUser()
        self.assertRaises(Http404, edit_claim, self.post_request)

    def test_edit_claim_with_invalid_user(self):
        guest = User(id=self.num_of_saved_users + random.randint(1, 10), username='guest')
        self.post_request.POST = self.update_claim_details
        self.post_request.user = guest
        self.assertRaises(Exception, edit_claim, self.post_request)

    def test_edit_claim_valid_with_different_category(self):
        self.update_claim_details['category'] = self.claim_2.category
        self.post_request.POST = self.update_claim_details
        self.post_request.user = self.user
        self.assertTrue(edit_claim(self.post_request).status_code == 200)
        self.assertTrue(Claim.objects.filter(id=self.update_claim_details['claim_id'])[0].category == self.claim_2.category)

    def test_edit_claim_valid_with_different_tags(self):
        self.update_claim_details['tags'] = self.claim_2.tags
        self.post_request.POST = self.update_claim_details
        self.post_request.user = self.user
        self.assertTrue(edit_claim(self.post_request).status_code == 200)
        self.assertTrue(Claim.objects.filter(id=self.update_claim_details['claim_id'])[0].tags == self.claim_2.tags)

    def test_edit_claim_valid_with_different_image_src(self):
        self.update_claim_details['image_src'] = self.claim_2.image_src
        self.post_request.POST = self.update_claim_details
        self.post_request.user = self.user
        self.assertTrue(edit_claim(self.post_request).status_code == 200)
        self.assertTrue(Claim.objects.filter(id=self.update_claim_details['claim_id'])[0].image_src == self.claim_2.image_src)

    def test_edit_claim_missing_args(self):
        for i in range(10):
            data_copy = self.update_claim_details.copy()
            args_to_remove = []
            for j in range(random.randint(1, len(self.update_claim_details.keys()) - 1)):
                args_to_remove.append(list(self.update_claim_details.keys())[j])
            for j in range(len(args_to_remove)):
                del self.update_claim_details[args_to_remove[j]]
            self.post_request.POST = self.update_claim_details
            self.post_request.user = self.user
            self.assertRaises(Exception, edit_claim, self.post_request)
            self.update_claim_details = data_copy.copy()

    def test_edit_claim_valid_with_different_tags(self):
        self.update_claim_details['tags'] = self.claim_2.tags
        self.post_request.POST = self.update_claim_details
        self.post_request.user = self.user
        self.assertTrue(edit_claim(self.post_request).status_code == 200)
        self.assertTrue(Claim.objects.filter(id=self.update_claim_details['claim_id'])[0].tags == self.claim_2.tags)

    def test_check_claim_new_fields(self):
        self.post_request.POST = self.update_claim_details
        self.post_request.user = self.user
        self.assertTrue(check_claim_new_fields(self.post_request)[0])

    def test_check_claim_new_fields_invalid_claim_id(self):
        self.update_claim_details['claim_id'] = random.randint(self.num_of_saved_claims + 1, self.num_of_saved_claims + 10)
        self.post_request.POST = self.update_claim_details
        self.post_request.user = self.user
        self.assertFalse(check_claim_new_fields(self.post_request)[0])

    def test_check_claim_new_fields_missing_claim_id(self):
        del self.update_claim_details['claim_id']
        self.post_request.POST = self.update_claim_details
        self.post_request.user = self.user
        self.assertFalse(check_claim_new_fields(self.post_request)[0])

    def test_check_claim_new_fields_user_not_authenticated(self):
        from django.contrib.auth.models import AnonymousUser
        self.post_request.POST = self.update_claim_details
        self.post_request.user = AnonymousUser()
        self.assertFalse(check_claim_new_fields(self.post_request)[0])

    def test_check_claim_new_fields_missing_claim(self):
        del self.update_claim_details['claim']
        self.post_request.POST = self.update_claim_details
        self.post_request.user = self.user
        self.assertFalse(check_claim_new_fields(self.post_request)[0])

    def test_check_claim_new_fields_missing_category(self):
        del self.update_claim_details['category']
        self.post_request.POST = self.update_claim_details
        self.post_request.user = self.user
        self.assertFalse(check_claim_new_fields(self.post_request)[0])

    def test_check_claim_new_fields_missing_tags(self):
        del self.update_claim_details['tags']
        self.post_request.POST = self.update_claim_details
        self.post_request.user = self.user
        self.assertFalse(check_claim_new_fields(self.post_request)[0])

    def test_check_claim_new_fields_missing_image_src(self):
        del self.update_claim_details['image_src']
        self.post_request.POST = self.update_claim_details
        self.post_request.user = self.user
        self.assertFalse(check_claim_new_fields(self.post_request)[0])

    def test_check_claim_new_fields_claim_does_not_belong_to_user(self):
        user_3 = User(username='User3')
        user_3.save()
        new_claim = Claim(user_id=user_3.id,
                          claim='New Claim',
                          category='new_claim_category',
                          tags="new_claims_tags",
                          authenticity_grade=0,
                          image_src='new_claim_image')
        new_claim.save()
        self.update_claim_details['claim_id'] = new_claim.id
        self.post_request.POST = self.update_claim_details
        self.post_request.user = self.user
        self.assertFalse(check_claim_new_fields(self.post_request)[0])

    def test_check_claim_new_fields_existing_claim(self):
        self.update_claim_details['claim'] = self.claim_2.claim
        self.post_request.POST = self.update_claim_details
        self.post_request.user = self.user
        self.assertFalse(check_claim_new_fields(self.post_request)[0])

    def test_check_claim_new_fields_edit_after_five_minutes(self):
        Claim.objects.filter(id=self.claim_1.id).update(timestamp=datetime.datetime.now() -
                                                            datetime.timedelta(minutes=6))
        self.post_request.POST = self.update_claim_details
        self.post_request.user = self.user
        self.assertFalse(check_claim_new_fields(self.post_request)[0])

    def test_delete_claim_valid_claim(self):
        claim_to_delete = {'claim_id': self.claim_1.id}
        self.post_request.POST = claim_to_delete
        self.post_request.user = self.user
        old_length = len(Claim.objects.all())
        self.assertTrue(delete_claim(self.post_request).status_code == 200)
        self.assertTrue(len(Claim.objects.all()), old_length - 1)
        for claim in Claim.objects.all():
            self.assertFalse(claim.claim == self.claim_1.claim)
            self.assertFalse(claim.category == self.claim_1.category)
            self.assertFalse(claim.tags == self.claim_1.tags)
            self.assertFalse(claim.image_src == self.claim_1.image_src)

    def test_delete_claim_invalid_claim(self):
        claim_to_delete = {'claim_id': self.claim_4.id}
        self.post_request.POST = claim_to_delete
        self.post_request.user = self.user
        old_length = len(Claim.objects.all())
        self.assertRaises(Exception, delete_claim, self.post_request)
        self.assertTrue(len(Claim.objects.all()), old_length)

    def test_delete_claim_valid_claim_invalid_user(self):
        user = User(id=self.num_of_saved_users + random.randint(1, 10), email="user@gmail.com")
        claim_to_delete = {'claim_id': self.claim_4.id}
        self.post_request.POST = claim_to_delete
        self.post_request.user = user
        old_length = len(Claim.objects.all())
        self.assertRaises(Exception, delete_claim, self.post_request)
        self.assertTrue(len(Claim.objects.all()), old_length)

    def test_delete_claim_valid_user_not_authenticated(self):
        from django.contrib.auth.models import AnonymousUser
        claim_to_delete = {'claim_id': self.claim_1.id}
        self.post_request.POST = claim_to_delete
        self.post_request.user = AnonymousUser()
        old_length = len(Claim.objects.all())
        self.assertRaises(Exception, delete_claim, self.post_request)
        self.assertTrue(len(Claim.objects.all()), old_length)

    def test_delete_claim_of_another_user(self):
        self.user_2 = User(username="User2", email='user1@gmail.com')
        self.user_2.save()
        claim_to_delete = {'claim_id': self.claim_4.id}
        self.post_request.POST = claim_to_delete
        self.post_request.user = self.user_2
        old_length = len(Claim.objects.all())
        self.assertRaises(Exception, delete_claim, self.post_request)
        self.assertTrue(len(Claim.objects.all()), old_length)

    def test_check_if_delete_claim_is_valid(self):
        claim_to_delete = {'claim_id': self.claim_1.id}
        self.post_request.POST = claim_to_delete
        self.post_request.user = self.user
        self.assertTrue(check_if_delete_claim_is_valid(self.post_request)[0])

    def test_check_if_delete_claim_is_valid_invalid_claim_id(self):
        claim_to_delete = {'claim_id': random.randint(self.num_of_saved_claims + 1, self.num_of_saved_claims + 10)}
        self.post_request.POST = claim_to_delete
        self.post_request.user = self.user
        self.assertFalse(check_if_delete_claim_is_valid(self.post_request)[0])

    def test_check_if_delete_claim_is_valid_missing_claim_id(self):
        self.post_request.POST = {}
        self.post_request.user = self.user
        self.assertFalse(check_if_delete_claim_is_valid(self.post_request)[0])

    def test_check_if_delete_claim_is_valid_invalid_user(self):
        guest = User(id=self.num_of_saved_users + random.randint(1, 10), username='guest')
        claim_to_delete = {'claim_id': self.claim_1.id}
        self.post_request.POST = claim_to_delete
        self.post_request.user = guest
        self.assertFalse(check_if_delete_claim_is_valid(self.post_request)[0])

    def test_check_if_delete_claim_is_valid_of_another_user(self):
        user_2 = User(username='User2')
        user_2.save()
        self.post_request.POST = {'claim_id': self.claim_1.id}
        self.post_request.user = user_2
        self.assertFalse(check_if_delete_claim_is_valid(self.post_request)[0])

    def test_handler_400(self):
        self.assertTrue(handler_400(HttpRequest()).status_code == 400)

    def test_handler_403(self):
        self.assertTrue(handler_403(HttpRequest()).status_code == 403)

    def test_handler_404(self):
        self.assertTrue(handler_404(HttpRequest()).status_code == 404)

    def test_handler_500(self):
        self.assertTrue(handler_500(HttpRequest()).status_code == 500)

    def test_about_page(self):
        self.assertTrue(about_page(HttpRequest()).status_code == 200)