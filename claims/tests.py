from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpRequest, QueryDict, Http404
from django.core.exceptions import PermissionDenied
from django.test import TestCase, Client
from claims.models import Claim, Merging_Suggestions
from claims.views import add_claim, check_if_claim_is_valid, check_if_input_format_is_valid, is_english_input, \
    post_above_limit, edit_claim, check_claim_new_fields, delete_claim, check_if_delete_claim_is_valid, \
    report_spam, check_if_spam_report_is_valid, download_claims, \
    merging_claims, check_if_suggestion_is_valid, switching_claims, delete_suggestion_for_merging_claims, \
    view_home, view_claims, sort_claims_by_comments, sort_claims_by_controversial, \
    view_claim, get_all_claims, get_newest_claims, get_claim_by_id, \
    get_category_for_claim, get_tags_for_claim, logout_view, add_claim_page, \
    export_claims_page, post_claims_tweets_page, merging_claims_page, about_page,\
    handler_400, handler_403, handler_404, handler_500, \
    return_get_request_to_user
from comments.models import Comment
from users.models import User, Users_Images, Scrapers, Users_Reputations
import random
import datetime
import string


class ClaimTests(TestCase):
    def setUp(self):
        self.password = 'admin'
        self.admin = User.objects.create_superuser(username='admin', password=self.password, email='admin@gmail.com')
        self.user = User(username='User1', email='user1@gmail.com')
        self.user.save()
        self.password = User.objects.make_random_password()
        self.scraper = User.objects.create_user(username='Scraper', password=self.password)
        self.user_image = Users_Images(user=self.user)
        self.user_image.save()
        self.rep = random.randint(1, 50)
        self.user_rep = Users_Reputations(user=self.user, reputation=self.rep)
        self.user_rep.save()

        self.scraper_image = Users_Images(user=self.scraper)
        self.scraper_image.save()
        self.scraper_details = Scrapers(scraper_name=self.scraper.username, scraper=self.scraper)
        self.scraper_details.save()

        self.num_of_saved_users = 3
        self.claim_1 = Claim(user_id=self.user.id,
                             claim='claim1',
                             category='category1',
                             tags='tag1,tag2,tag3',
                             authenticity_grade=0,
                             image_src='image1')
        self.claim_2 = Claim(user_id=self.user.id,
                             claim='claim2',
                             category='category2',
                             tags='tag4,tag5',
                             authenticity_grade=0,
                             image_src='image2')
        self.claim_3 = Claim(user_id=self.user.id,
                             claim='claim3',
                             category='category3',
                             tags='tag6,tag7,tag8,tag9',
                             authenticity_grade=0,
                             image_src='image3')
        self.claim_4 = Claim(user_id=self.user.id,
                             claim='claim4',
                             category='category4',
                             tags='tag10,tag11',
                             authenticity_grade=0,
                             image_src='image4')
        self.claim_1.save()
        self.claim_2.save()
        self.claim_3.save()
        self.num_of_saved_claims = 3
        self.url = 'https://www.snopes.com/fact-check/page/'
        self.comment_1 = Comment(claim_id=self.claim_1.id,
                                 user_id=self.claim_1.user_id,
                                 title='title1',
                                 description='description1',
                                 url=self.url + str(random.randint(1, 10)),
                                 verdict_date=datetime.date.today() - datetime.timedelta(days=random.randint(0, 10)),
                                 label='True')
        self.comment_2 = Comment(claim_id=self.claim_2.id,
                                 user_id=self.claim_2.user_id,
                                 title='title2',
                                 description='description2',
                                 url=self.url + str(random.randint(1, 10)),
                                 verdict_date=datetime.date.today() - datetime.timedelta(days=random.randint(0, 10)),
                                 label='False')
        self.comment_3 = Comment(claim_id=self.claim_3.id,
                                 user_id=self.claim_3.user_id,
                                 title='title3',
                                 description='description3',
                                 url=self.url + str(random.randint(1, 10)),
                                 verdict_date=datetime.date.today() - datetime.timedelta(days=random.randint(0, 10)),
                                 label='Unknown')

        self.comment_1.save()
        self.comment_2.save()
        self.comment_3.save()
        self.num_of_saved_comments = 3
        self.SITE_KEY_TEST = '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI'
        self.new_claim_details = {'claim': self.claim_4.claim,
                                  'title': 'title4',
                                  'description': 'description4',
                                  'url': self.url + str(random.randint(1, 10)),
                                  'add_comment': "true",
                                  'verdict_date': datetime.datetime.strptime(str(datetime.date.today() - datetime.timedelta(days=random.randint(0, 10))), '%Y-%m-%d').strftime('%d/%m/%Y'),
                                  'tags': self.claim_4.tags,
                                  'category': self.claim_4.category,
                                  'label': 'False',
                                  'image_src': self.claim_4.image_src,
                                  'g_recaptcha_response': self.SITE_KEY_TEST}
        self.post_request = HttpRequest()
        self.post_request.method = 'POST'
        self.get_request = HttpRequest()
        self.get_request.method = 'GET'
        self.update_claim_details = {'claim_id': self.claim_1.id,
                                     'claim': 'newClaim1',
                                     'category': 'newCategory1',
                                     'tags': 'newTag1,newTag2,newTag3,newTag4',
                                     'image_src': 'image1'}

        self.test_file_data = {'claim': 'Nancy Pelosi announced a "scheme" to "take down Donald Trump in 2020" '
                                        'by lowering the voting age.',
                               'category': 'Politics',
                               'tags': 'Nancy Pelosi,Donald Trump',
                               'image_src': 'https://www.snopes.com/tachyon/2017/08/vote_election_2016_fb.jpg',
                               'add_comment': 'true',
                               'title': 'Did U. S. House Speaker Nancy Pelosi Announce a '
                                        '‘New Scheme to Take Down Donald Trump in 2020’?',
                               'description': 'The supposed "scheme" entailed lowering '
                                              'the federal minimum voting age to 16.',
                               'url': 'https://www.snopes.com/fact-check/nancy-pelosi-voting-age/',
                               'verdict_date': '23/03/2019',
                               'label': 'Mostly False'}

        self.test_file = SimpleUploadedFile("tests.csv", open(
            'claims/tests.csv', 'r', encoding='utf-8-sig').read().encode())
        self.test_file_invalid_header = SimpleUploadedFile("tests_invalid.csv", open(
            'claims/tests_invalid.csv', 'r', encoding='utf-8-sig').read().encode())

        suggestion = Merging_Suggestions.objects.create(claim_id=self.claim_1.id,
                                                        claim_to_merge_id=self.claim_2.id)
        self.num_of_saved_suggestions = 1
        self.merging_claims = {'suggestion_id': suggestion.id,
                               'user_id': self.admin.id,
                               'is_superuser': True}
        self.error_code = 404

    def tearDown(self):
        pass

    def test_add_claim(self):
        len_claims = len(Claim.objects.all())
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.new_claim_details)
        self.post_request.POST = query_dict
        self.post_request.user = self.user
        self.assertTrue(add_claim(self.post_request).status_code == 200)
        self.assertTrue(len(Claim.objects.all()) == len_claims + 1)
        self.assertFalse(get_claim_by_id(self.num_of_saved_claims + 1) is None)
        claim_4 = get_claim_by_id(self.num_of_saved_claims + 1)
        self.assertTrue(claim_4.claim == self.new_claim_details['claim'])
        self.assertTrue(claim_4.category == self.new_claim_details['category'])
        self.assertTrue(claim_4.tags == ','.join(self.new_claim_details['tags'].split(',')))

    def test_add_claim_by_user_not_authenticated(self):
        from django.contrib.auth.models import AnonymousUser
        len_claims = len(Claim.objects.all())
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.new_claim_details)
        self.post_request.POST = query_dict
        self.post_request.user = AnonymousUser()
        self.assertRaises(PermissionDenied, add_claim, self.post_request)
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
        response = add_claim(self.post_request)
        self.assertTrue(response.status_code == self.error_code)
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
            response = add_claim(self.post_request)
            self.assertTrue(response.status_code == self.error_code)
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
            response = add_claim(self.post_request)
            self.assertTrue(response.status_code == self.error_code)
            self.assertTrue(len(Claim.objects.all()) == len_claims)
            self.assertTrue(get_claim_by_id(self.num_of_saved_claims + 1) is None)
            self.new_claim_details = dict_copy.copy()

    def test_add_claim_invalid_request(self):
        self.get_request.user = self.user
        self.assertRaises(PermissionDenied, add_claim, self.get_request)

    def test_check_if_claim_is_valid(self):
        self.new_claim_details['user_id'] = self.user.id
        self.new_claim_details['is_superuser'] = False
        self.assertTrue(check_if_claim_is_valid(self.new_claim_details))
        self.new_claim_details['is_superuser'] = True
        self.assertTrue(check_if_claim_is_valid(self.new_claim_details))

    def test_check_if_claim_is_valid_missing_user_id(self):
        self.new_claim_details['is_superuser'] = False
        self.assertFalse(check_if_claim_is_valid(self.new_claim_details)[0])
        self.new_claim_details['is_superuser'] = True
        self.assertFalse(check_if_claim_is_valid(self.new_claim_details)[0])

    def test_check_if_claim_is_valid_missing_user_type(self):
        self.new_claim_details['user_id'] = self.user.id
        self.assertFalse(check_if_claim_is_valid(self.new_claim_details)[0])

    def test_check_if_claim_is_valid_missing_claim(self):
        self.new_claim_details['user_id'] = self.user.id
        self.new_claim_details['is_superuser'] = False
        del self.new_claim_details['claim']
        self.assertFalse(check_if_claim_is_valid(self.new_claim_details)[0])
        self.new_claim_details['is_superuser'] = True
        self.assertFalse(check_if_claim_is_valid(self.new_claim_details)[0])

    def test_check_if_claim_is_valid_missing_category(self):
        self.new_claim_details['user_id'] = self.user.id
        self.new_claim_details['is_superuser'] = False
        del self.new_claim_details['category']
        self.assertFalse(check_if_claim_is_valid(self.new_claim_details)[0])
        self.new_claim_details['is_superuser'] = True
        self.assertFalse(check_if_claim_is_valid(self.new_claim_details)[0])

    def test_check_if_claim_is_valid_missing_tags(self):
        self.new_claim_details['user_id'] = self.user.id
        self.new_claim_details['is_superuser'] = False
        del self.new_claim_details['tags']
        self.assertTrue(check_if_claim_is_valid(self.new_claim_details)[0])
        self.new_claim_details['is_superuser'] = True
        self.assertTrue(check_if_claim_is_valid(self.new_claim_details)[0])

    def test_check_if_claim_is_valid_invalid_format_for_tags(self):
        invalid_input = 'tag1,'
        for i in range(random.randint(1, 10)):
            invalid_input += ' '
        invalid_input += ',tag2'
        self.new_claim_details['user_id'] = self.user.id
        self.new_claim_details['tags'] = invalid_input
        self.new_claim_details['is_superuser'] = False
        self.assertFalse(check_if_claim_is_valid(self.new_claim_details)[0])
        self.new_claim_details['is_superuser'] = True
        self.assertFalse(check_if_claim_is_valid(self.new_claim_details)[0])

    def test_check_if_claim_is_valid_missing_img_src(self):
        self.new_claim_details['user_id'] = self.user.id
        self.new_claim_details['is_superuser'] = False
        del self.new_claim_details['image_src']
        self.assertTrue(check_if_claim_is_valid(self.new_claim_details)[0])
        self.new_claim_details['is_superuser'] = True
        self.assertTrue(check_if_claim_is_valid(self.new_claim_details)[0])

    def test_check_if_claim_is_valid_missing_add_comment(self):
        self.new_claim_details['user_id'] = self.user.id
        self.new_claim_details['is_superuser'] = False
        del self.new_claim_details['add_comment']
        self.assertFalse(check_if_claim_is_valid(self.new_claim_details)[0])
        self.new_claim_details['is_superuser'] = True
        self.assertFalse(check_if_claim_is_valid(self.new_claim_details)[0])

    def test_check_if_claim_is_valid_existing_claim(self):
        self.new_claim_details['user_id'] = self.user.id
        self.new_claim_details['is_superuser'] = False
        self.new_claim_details['claim'] = self.claim_1.claim
        self.assertFalse(check_if_claim_is_valid(self.new_claim_details)[0])
        self.new_claim_details['is_superuser'] = True
        self.assertFalse(check_if_claim_is_valid(self.new_claim_details)[0])

    def test_check_if_claim_is_valid_invalid_user_id(self):
        self.new_claim_details['user_id'] = self.num_of_saved_users + random.randint(1, 10)
        self.new_claim_details['is_superuser'] = False
        self.assertFalse(check_if_claim_is_valid(self.new_claim_details)[0])
        self.new_claim_details['is_superuser'] = True
        self.assertFalse(check_if_claim_is_valid(self.new_claim_details)[0])

    def test_check_if_claim_is_valid_invalid_input_for_claim(self):
        self.new_claim_details['user_id'] = self.user.id
        self.new_claim_details['is_superuser'] = False
        self.new_claim_details['claim'] = 'קלט בשפה שאינה אנגלית'
        self.assertFalse(check_if_claim_is_valid(self.new_claim_details)[0])
        self.new_claim_details['is_superuser'] = True
        self.assertFalse(check_if_claim_is_valid(self.new_claim_details)[0])

    def test_check_if_claim_is_valid_invalid_input_for_category(self):
        self.new_claim_details['user_id'] = self.user.id
        self.new_claim_details['is_superuser'] = False
        self.new_claim_details['category'] = 'المدخلات بلغة غير الإنجليزية'
        self.assertFalse(check_if_claim_is_valid(self.new_claim_details)[0])
        self.new_claim_details['is_superuser'] = True
        self.assertFalse(check_if_claim_is_valid(self.new_claim_details)[0])

    def test_check_if_claim_is_valid_invalid_input_for_tags(self):
        self.new_claim_details['user_id'] = self.user.id
        self.new_claim_details['is_superuser'] = False
        self.new_claim_details['category'] = '输入英语以外的语言 输入英语以外的语言'
        self.assertFalse(check_if_claim_is_valid(self.new_claim_details)[0])
        self.new_claim_details['is_superuser'] = True
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
        self.new_claim_details['is_superuser'] = False
        self.new_claim_details['claim'] = 'claim_10'
        self.assertFalse(check_if_claim_is_valid(self.new_claim_details)[0])
        self.new_claim_details['is_superuser'] = True
        self.assertTrue(check_if_claim_is_valid(self.new_claim_details)[0])

    def test_check_if_input_format_is_valid_empty_input(self):
        self.assertTrue(check_if_input_format_is_valid(''))

    def test_check_if_input_format_is_valid_with_valid_input(self):
        letters = string.ascii_lowercase
        valid_input = []
        for i in range(random.randint(1, 10)):
            valid_input.append(''.join(random.choice(letters) for i in range(random.randint(1, 10))))
        valid_input = ','.join(valid_input)
        self.assertTrue(check_if_input_format_is_valid(valid_input))
        self.assertTrue(check_if_input_format_is_valid(valid_input))

    def test_check_if_input_format_is_valid_with_invalid_input(self):
        not_allowed_input = set(string.punctuation)
        not_allowed_input.remove('\'')
        not_allowed_input.remove('`')
        not_allowed_input.remove('.')
        letters = ''.join(not_allowed_input)
        for j in range(random.randint(10, 20)):
            invalid_input = ','.join('tag' + str(i) + random.choice(letters) for i in range(random.randint(2, 10)))
            self.assertFalse(check_if_input_format_is_valid(invalid_input))
        self.assertFalse(check_if_input_format_is_valid('tag1,tag2, ' + letters[random.randint(1, len(letters) - 1)]))
        self.assertFalse(check_if_input_format_is_valid(letters[random.randint(1, len(letters) - 1)] + 'tag1,tag2'))
        invalid_input = 'tag1,'
        for i in range(random.randint(1, 10)):
            invalid_input += ' '
        invalid_input += ',tag2'
        self.assertFalse(check_if_input_format_is_valid(invalid_input))
        invalid_input = 'tag1,'
        for i in range(random.randint(1, 10)):
            invalid_input += ','
        invalid_input += 'tag2'
        self.assertFalse(check_if_input_format_is_valid(invalid_input))

    def test_is_english_input_valid(self):
        self.assertTrue(is_english_input(''.join(random.choices(string.ascii_uppercase + string.digits, k=random.randint(10, 20)))))

    def test_is_english_input_invalid(self):
        self.assertFalse(is_english_input('בדיקה'))
        self.assertFalse(is_english_input('فحص'))
        self.assertFalse(is_english_input('检查'))

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

    def test_edit_claim_valid_with_different_claim(self):
        self.update_claim_details['claim'] = self.claim_1.claim + '_new'
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.update_claim_details)
        self.post_request.POST = query_dict
        self.post_request.user = self.user
        self.assertTrue(edit_claim(self.post_request).status_code == 200)
        self.assertTrue(Claim.objects.filter(id=self.update_claim_details['claim_id'])[0].claim == self.claim_1.claim + '_new')

    def test_edit_claim_with_existing_claim(self):
        self.update_claim_details['claim'] = self.claim_2.claim
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.update_claim_details)
        self.post_request.POST = query_dict
        self.post_request.user = self.user
        response = edit_claim(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_edit_claim_with_user_not_authenticated(self):
        from django.contrib.auth.models import AnonymousUser
        self.post_request.POST = self.update_claim_details
        self.post_request.user = AnonymousUser()
        self.assertRaises(PermissionDenied, edit_claim, self.post_request)

    def test_edit_claim_with_invalid_user(self):
        guest = User(id=self.num_of_saved_users + random.randint(1, 10), username='guest')
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.update_claim_details)
        self.post_request.POST = query_dict
        self.post_request.user = guest
        response = edit_claim(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_edit_claim_invalid_request(self):
        self.get_request.user = self.user
        self.assertRaises(PermissionDenied, edit_claim, self.get_request)

    def test_edit_claim_valid_with_different_category(self):
        self.update_claim_details['category'] = self.claim_2.category
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.update_claim_details)
        self.post_request.POST = query_dict
        self.post_request.user = self.user
        self.assertTrue(edit_claim(self.post_request).status_code == 200)
        self.assertTrue(Claim.objects.filter(id=self.update_claim_details['claim_id'])[0].category == self.claim_2.category)

    def test_edit_claim_valid_with_different_tags(self):
        self.update_claim_details['tags'] = 'newTag1,newTag2,newTag3'
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.update_claim_details)
        self.post_request.POST = query_dict
        self.post_request.user = self.user
        self.assertTrue(edit_claim(self.post_request).status_code == 200)
        self.assertTrue(Claim.objects.filter(id=self.update_claim_details['claim_id'])[0].tags == ','.join('newTag1 newTag2 newTag3'.split()))

    def test_edit_claim_valid_with_different_image_src(self):
        self.update_claim_details['image_src'] = self.claim_2.image_src
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.update_claim_details)
        self.post_request.POST = query_dict
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
            query_dict = QueryDict('', mutable=True)
            query_dict.update(self.update_claim_details)
            self.post_request.POST = query_dict
            self.post_request.user = self.user
            response = edit_claim(self.post_request)
            self.assertTrue(response.status_code == self.error_code)
            self.update_claim_details = data_copy.copy()

    def test_check_claim_new_fields(self):
        self.update_claim_details['user_id'] = self.user.id
        self.update_claim_details['is_superuser'] = False
        self.assertTrue(check_claim_new_fields(self.update_claim_details)[0])
        self.update_claim_details['is_superuser'] = True
        self.assertTrue(check_claim_new_fields(self.update_claim_details)[0])

    def test_check_claim_new_fields_invalid_claim_id(self):
        self.update_claim_details['user_id'] = self.user.id
        self.update_claim_details['claim_id'] = self.num_of_saved_claims + random.randint(1, 10)
        self.update_claim_details['is_superuser'] = False
        self.assertFalse(check_claim_new_fields(self.update_claim_details)[0])
        self.update_claim_details['is_superuser'] = True
        self.assertFalse(check_claim_new_fields(self.update_claim_details)[0])

    def test_check_claim_new_fields_missing_claim_id(self):
        self.update_claim_details['claim_id'] = self.user.id
        self.update_claim_details['is_superuser'] = False
        del self.update_claim_details['category']
        self.assertFalse(check_claim_new_fields(self.update_claim_details)[0])
        self.update_claim_details['is_superuser'] = True
        self.assertFalse(check_claim_new_fields(self.update_claim_details)[0])

    def test_check_claim_new_fields_missing_user_type(self):
        self.update_claim_details['comment_id'] = str(self.comment_1.id)
        self.update_claim_details['user_id'] = str(self.user.id)
        self.assertFalse(check_claim_new_fields(self.update_claim_details)[0])

    def test_check_claim_new_fields_missing_claim(self):
        self.update_claim_details['user_id'] = self.user.id
        self.update_claim_details['is_superuser'] = False
        del self.update_claim_details['claim']
        self.assertFalse(check_claim_new_fields(self.update_claim_details)[0])
        self.update_claim_details['is_superuser'] = True
        self.assertFalse(check_claim_new_fields(self.update_claim_details)[0])

    def test_check_claim_new_fields_missing_category(self):
        self.update_claim_details['user_id'] = self.user.id
        self.update_claim_details['is_superuser'] = False
        del self.update_claim_details['category']
        self.assertFalse(check_claim_new_fields(self.update_claim_details)[0])
        self.update_claim_details['is_superuser'] = True
        self.assertFalse(check_claim_new_fields(self.update_claim_details)[0])

    def test_check_claim_new_fields_missing_tags(self):
        self.update_claim_details['user_id'] = self.user.id
        self.update_claim_details['is_superuser'] = False
        del self.update_claim_details['tags']
        self.assertTrue(check_claim_new_fields(self.update_claim_details)[0])
        self.update_claim_details['is_superuser'] = True
        self.assertTrue(check_claim_new_fields(self.update_claim_details)[0])

    def test_check_claim_new_fields_missing_image_src(self):
        self.update_claim_details['user_id'] = self.user.id
        self.update_claim_details['is_superuser'] = False
        del self.update_claim_details['image_src']
        self.assertTrue(check_claim_new_fields(self.update_claim_details)[0])
        self.update_claim_details['is_superuser'] = True
        self.assertTrue(check_claim_new_fields(self.update_claim_details)[0])

    def test_check_claim_new_fields_claim_does_not_belong_to_user(self):
        user_3 = User(username='User3')
        user_3.save()
        new_claim = Claim(user_id=user_3.id,
                          claim='newClaim',
                          category='newCategory',
                          tags='tag1 tag2 tag3',
                          authenticity_grade=0,
                          image_src='image')
        new_claim.save()
        self.update_claim_details['claim_id'] = new_claim.id
        self.update_claim_details['is_superuser'] = False
        self.assertFalse(check_claim_new_fields(self.update_claim_details)[0])
        self.update_claim_details['is_superuser'] = True
        self.assertFalse(check_claim_new_fields(self.update_claim_details)[0])

    def test_check_claim_new_fields_existing_claim(self):
        self.update_claim_details['user_id'] = self.user.id
        self.update_claim_details['claim'] = self.claim_2.claim
        self.update_claim_details['is_superuser'] = False
        self.assertFalse(check_claim_new_fields(self.update_claim_details)[0])
        self.update_claim_details['is_superuser'] = True
        self.assertFalse(check_claim_new_fields(self.update_claim_details)[0])

    def test_check_claim_new_fields_edit_after_five_minutes(self):
        self.update_claim_details['user_id'] = self.user.id
        self.update_claim_details['is_superuser'] = False
        Claim.objects.filter(id=self.claim_1.id).update(timestamp=datetime.datetime.now() -
                                                        datetime.timedelta(minutes=11))
        self.assertFalse(check_claim_new_fields(self.update_claim_details)[0])
        self.update_claim_details['is_superuser'] = True
        self.assertTrue(check_claim_new_fields(self.update_claim_details)[0])

    def test_check_claim_new_fields_invalid_input_for_claim(self):
        self.update_claim_details['user_id'] = self.user.id
        self.update_claim_details['is_superuser'] = False
        self.update_claim_details['claim'] = 'קלט בשפה שאינה אנגלית'
        self.assertFalse(check_claim_new_fields(self.update_claim_details)[0])
        self.update_claim_details['is_superuser'] = True
        self.assertFalse(check_claim_new_fields(self.update_claim_details)[0])

    def test_check_claim_new_fields_invalid_input_for_category(self):
        self.update_claim_details['user_id'] = self.user.id
        self.update_claim_details['is_superuser'] = False
        self.update_claim_details['category'] = 'المدخلات بلغة غير الإنجليزية'
        self.assertFalse(check_claim_new_fields(self.update_claim_details)[0])
        self.update_claim_details['is_superuser'] = True
        self.assertFalse(check_claim_new_fields(self.update_claim_details)[0])

    def test_check_claim_new_fields_invalid_input_for_tags(self):
        self.update_claim_details['user_id'] = self.user.id
        self.update_claim_details['is_superuser'] = False
        self.update_claim_details['category'] = '输入英语以外的语言 输入英语以外的语言'
        self.assertFalse(check_claim_new_fields(self.update_claim_details)[0])
        self.update_claim_details['is_superuser'] = True
        self.assertFalse(check_claim_new_fields(self.update_claim_details)[0])

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
        response = delete_claim(self.post_request)
        self.assertTrue(response.status_code == self.error_code)
        self.assertTrue(len(Claim.objects.all()), old_length)

    def test_delete_claim_valid_claim_invalid_user(self):
        user = User(id=self.num_of_saved_users + random.randint(1, 10), email="user@gmail.com")
        claim_to_delete = {'claim_id': self.claim_4.id}
        self.post_request.POST = claim_to_delete
        self.post_request.user = user
        old_length = len(Claim.objects.all())
        response = delete_claim(self.post_request)
        self.assertTrue(response.status_code == self.error_code)
        self.assertTrue(len(Claim.objects.all()), old_length)

    def test_delete_claim_user_not_authenticated(self):
        from django.contrib.auth.models import AnonymousUser
        claim_to_delete = {'claim_id': self.claim_1.id}
        self.post_request.POST = claim_to_delete
        self.post_request.user = AnonymousUser()
        old_length = len(Claim.objects.all())
        self.assertRaises(PermissionDenied, delete_claim, self.post_request)
        self.assertTrue(len(Claim.objects.all()), old_length)

    def test_delete_claim_invalid_request(self):
        self.get_request.user = self.user
        self.assertRaises(PermissionDenied, delete_claim, self.get_request)

    def test_delete_claim_of_another_user(self):
        self.user_2 = User(username="User2", email='user1@gmail.com')
        self.user_2.save()
        claim_to_delete = {'claim_id': self.claim_4.id}
        self.post_request.POST = claim_to_delete
        self.post_request.user = self.user_2
        old_length = len(Claim.objects.all())
        response = delete_claim(self.post_request)
        self.assertTrue(response.status_code == self.error_code)
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

    def test_report_spam_for_claim(self):
        claim_to_report_spam = {'claim_id': self.claim_1.id}
        self.post_request.POST = claim_to_report_spam
        self.post_request.user = self.scraper
        response = report_spam(self.post_request)
        self.assertTrue(response.status_code == 200)

    def test_report_spam_for_claim_twice(self):
        claim_to_report_spam = {'claim_id': self.claim_1.id}
        self.post_request.POST = claim_to_report_spam
        self.post_request.user = self.scraper
        self.assertTrue(report_spam(self.post_request).status_code == 200)
        response = report_spam(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_report_spam_user_not_authenticated(self):
        from django.contrib.auth.models import AnonymousUser
        claim_to_report_spam = {'claim_id': self.claim_1.id}
        self.post_request.POST = claim_to_report_spam
        self.post_request.user = AnonymousUser()
        self.assertRaises(PermissionDenied, report_spam, self.post_request)

    def test_report_spam_invalid_request(self):
        self.get_request.user = self.user
        self.assertRaises(PermissionDenied, report_spam, self.get_request)

    def test_report_spam_missing_claim_id(self):
        self.post_request.POST = {}
        self.post_request.user = self.scraper
        response = report_spam(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_report_spam_invalid_user(self):
        guest = User(id=self.num_of_saved_users + random.randint(1, 10), username='guest')
        claim_to_report_spam = {'claim_id': self.claim_1.id}
        self.post_request.POST = claim_to_report_spam
        self.post_request.user = guest
        response = report_spam(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_check_if_spam_report_is_valid(self):
        claim_to_report_spam = {'claim_id': self.claim_1.id}
        self.post_request.POST = claim_to_report_spam
        self.post_request.user = self.scraper
        self.assertTrue(check_if_spam_report_is_valid(self.post_request)[0])

    def test_check_if_spam_report_is_valid_missing_claim_id(self):
        self.post_request.POST = {}
        self.post_request.user = self.scraper
        self.assertFalse(check_if_spam_report_is_valid(self.post_request)[0])

    def test_check_if_spam_report_is_valid_invalid_claim_id(self):
        self.post_request.POST = {'claim_id': self.num_of_saved_claims + random.randint(1, 10)}
        self.post_request.user = self.scraper
        self.assertFalse(check_if_spam_report_is_valid(self.post_request)[0])

    def test_check_if_spam_report_is_valid_invalid_user(self):
        guest = User(id=self.num_of_saved_users + random.randint(1, 10), username='guest')
        claim_to_report_spam = {'claim_id': self.claim_1.id}
        self.post_request.POST = claim_to_report_spam
        self.post_request.user = guest
        self.assertFalse(check_if_spam_report_is_valid(self.post_request)[0])

    def test_check_if_spam_report_is_valid_duplicate_spam(self):
        claim_to_report_spam = {'claim_id': self.claim_1.id}
        self.post_request.POST = claim_to_report_spam
        self.post_request.user = self.scraper
        self.assertTrue(check_if_spam_report_is_valid(self.post_request)[0])
        self.assertTrue(report_spam(self.post_request).status_code == 200)
        self.assertFalse(check_if_spam_report_is_valid(self.post_request)[0])

    def test_test_download_claims(self):
        self.post_request.FILES['csv_file'] = self.test_file
        self.post_request.user = self.admin
        len_claims = len(Claim.objects.all())
        self.assertTrue(download_claims(self.post_request).status_code == 200)
        self.assertTrue(len(Claim.objects.all()) == len_claims + 1)
        new_claim = Claim.objects.all().order_by('-id').first()
        self.assertTrue(new_claim.id == self.num_of_saved_claims + 1)
        self.assertTrue(new_claim.claim == self.test_file_data['claim'])
        self.assertTrue(new_claim.category == self.test_file_data['category'])
        self.assertTrue(new_claim.tags == self.test_file_data['tags'])
        self.assertTrue(new_claim.image_src == self.test_file_data['image_src'])

    def test_download_claims_not_admin_user(self):
        self.post_request.FILES['csv_file'] = self.test_file
        self.post_request.user = self.user
        len_claims = len(Claim.objects.all())
        self.assertRaises(PermissionDenied, download_claims, self.post_request)
        self.assertTrue(len(Claim.objects.all()) == len_claims)

    def test_download_claims_user_not_authenticated(self):
        from django.contrib.auth.models import AnonymousUser
        self.post_request.FILES['csv_file'] = self.test_file
        self.post_request.user = AnonymousUser()
        len_claims = len(Claim.objects.all())
        self.assertRaises(PermissionDenied, download_claims, self.post_request)
        self.assertTrue(len(Claim.objects.all()) == len_claims)

    def test_download_claims_invalid_request(self):
        self.get_request.FILES['csv_file'] = self.test_file
        self.get_request.user = self.admin
        len_claims = len(Claim.objects.all())
        self.assertRaises(PermissionDenied, download_claims, self.get_request)
        self.assertTrue(len(Claim.objects.all()) == len_claims)

    def test_download_claims_invalid_file(self):
        self.post_request.user = self.admin
        len_claims = len(Claim.objects.all())
        self.assertRaises(PermissionDenied, download_claims, self.post_request)
        self.assertTrue(len(Claim.objects.all()) == len_claims)

    def test_download_claims_invalid_headers_in_file(self):
        self.post_request.FILES['csv_file'] = self.test_file_invalid_header
        self.post_request.user = self.admin
        len_claims = len(Claim.objects.all())
        self.assertRaises(Http404, download_claims, self.post_request)
        self.assertTrue(len(Claim.objects.all()) == len_claims)

    def test_merging_claims(self):
        claim_2_id = self.claim_2.id
        self.post_request.POST = self.merging_claims
        self.post_request.user = self.admin
        response = merging_claims(self.post_request)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(len(Claim.objects.filter(id=claim_2_id)) == 0)
        self.assertTrue(len(Comment.objects.filter(claim_id=self.claim_1.id)) == 2)

    def test_merging_claims_by_not_admin_user(self):
        self.post_request.POST = self.merging_claims
        self.post_request.user = self.user
        self.assertRaises(PermissionDenied, merging_claims, self.post_request)

    def test_merging_claims_invalid_request(self):
        self.get_request.POST = self.merging_claims
        self.get_request.user = self.admin
        self.assertRaises(PermissionDenied, merging_claims, self.get_request)

    def test_merging_claims_invalid_suggestion_id(self):
        self.merging_claims['suggestion_id'] = self.num_of_saved_suggestions + random.randint(1, 10)
        self.post_request.POST = self.merging_claims
        self.post_request.user = self.admin
        response = merging_claims(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_check_if_suggestion_is_valid(self):
        self.assertTrue(check_if_suggestion_is_valid(self.merging_claims)[0])

    def test_check_if_suggestion_is_valid_missing_suggestion_id(self):
        del self.merging_claims['suggestion_id']
        self.assertFalse(check_if_suggestion_is_valid(self.merging_claims)[0])

    def test_check_if_suggestion_is_valid_invalid_suggestion_id(self):
        self.merging_claims['suggestion_id'] = self.num_of_saved_suggestions + random.randint(1, 10)
        self.assertFalse(check_if_suggestion_is_valid(self.merging_claims)[0])

    def test_check_if_suggestion_is_valid_missing_user_id(self):
        del self.merging_claims['user_id']
        self.assertFalse(check_if_suggestion_is_valid(self.merging_claims)[0])

    def test_check_if_suggestion_is_valid_invalid_user_id(self):
        self.merging_claims['user_id'] = self.num_of_saved_users + random.randint(1, 10)
        self.assertFalse(check_if_suggestion_is_valid(self.merging_claims)[0])

    def test_check_if_suggestion_is_valid_missing_user_type(self):
        del self.merging_claims['is_superuser']
        self.assertFalse(check_if_suggestion_is_valid(self.merging_claims)[0])

    def test_check_if_suggestion_is_valid_not_admin_user(self):
        self.merging_claims['user_id'] = self.user.id
        self.merging_claims['is_superuser'] = False
        self.assertFalse(check_if_suggestion_is_valid(self.merging_claims)[0])

    def test_switching_claims(self):
        self.assertTrue(len(Merging_Suggestions.objects.filter(claim_id=self.claim_2.id,
                                                               claim_to_merge_id=self.claim_1.id)) == 0)
        self.post_request.POST = self.merging_claims
        self.post_request.user = self.admin
        response = switching_claims(self.post_request)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(len(Merging_Suggestions.objects.filter(claim_id=self.claim_2.id,
                                                               claim_to_merge_id=self.claim_1.id)) == 1)

    def test_switching_claims_by_not_admin_user(self):
        self.post_request.POST = self.merging_claims
        self.post_request.user = self.user
        self.assertRaises(PermissionDenied, switching_claims, self.post_request)

    def test_switching_claims_invalid_request(self):
        self.get_request.POST = self.merging_claims
        self.get_request.user = self.admin
        self.assertRaises(PermissionDenied, switching_claims, self.get_request)

    def test_switching_claims_missing_suggestion_id(self):
        del self.merging_claims['suggestion_id']
        self.post_request.POST = self.merging_claims
        self.post_request.user = self.admin
        response = switching_claims(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_switching_claims_invalid_suggestion_id(self):
        self.merging_claims['suggestion_id'] = self.num_of_saved_suggestions + random.randint(1, 10)
        self.post_request.POST = self.merging_claims
        self.post_request.user = self.admin
        response = switching_claims(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_delete_suggestion_for_merging_claims(self):
        claim_2_id = self.claim_2.id
        self.post_request.POST = self.merging_claims
        self.post_request.user = self.admin
        response = delete_suggestion_for_merging_claims(self.post_request)
        self.assertTrue(response.status_code == 200)
        self.assertTrue(len(Claim.objects.filter(id=claim_2_id)) == 1)
        self.assertTrue(len(Claim.objects.filter(id=self.claim_1.id)) == 1)
        self.assertTrue(len(Comment.objects.filter(claim_id=self.claim_1.id)) == 1)
        self.assertTrue(len(Comment.objects.filter(claim_id=claim_2_id)) == 1)

    def test_delete_suggestion_for_merging_claims_by_not_admin_user(self):
        self.post_request.POST = self.merging_claims
        self.post_request.user = self.user
        self.assertRaises(PermissionDenied, delete_suggestion_for_merging_claims, self.post_request)

    def test_delete_suggestion_for_merging_claims_invalid_request(self):
        self.get_request.POST = self.merging_claims
        self.get_request.user = self.admin
        self.assertRaises(PermissionDenied, merging_claims, self.get_request)

    def test_delete_suggestion_for_merging_claims_missing_suggestion_id(self):
        del self.merging_claims['suggestion_id']
        self.post_request.POST = self.merging_claims
        self.post_request.user = self.admin
        response = delete_suggestion_for_merging_claims(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_delete_suggestion_for_merging_claims_invalid_suggestion_id(self):
        self.merging_claims['suggestion_id'] = self.num_of_saved_suggestions + random.randint(1, 10)
        self.post_request.POST = self.merging_claims
        self.post_request.user = self.admin
        response = delete_suggestion_for_merging_claims(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_view_home_many_claims(self):
        for i in range(4, 24):
            claim = Claim(user_id=self.user.id,
                          claim='claim' + str(i),
                          category='category' + str(i),
                          tags='tag' + str(i),
                          authenticity_grade=0,
                          image_src='image' + str(i))
            claim.save()
            comment = Comment(claim_id=claim.id,
                              user_id=claim.user.id,
                              title='title' + str(i),
                              description='description' + str(i),
                              url='url' + str(i),
                              verdict_date=datetime.date.today() - datetime.timedelta(days=random.randint(0, 10)),
                              label='label' + str(i))
            comment.save()
        self.get_request.user = self.user
        response = view_home(self.get_request)
        self.assertTrue(response.status_code == 200)

    def test_view_home_valid_user_authenticated(self):
        client = Client()
        user_1 = User.objects.create_user(username='user1', email='user1@gmail.com', password='user1')
        client.login(username='user1', password='user1')
        self.get_request.user = user_1
        self.get_request.session = client.session
        self.assertTrue(view_home(self.get_request).status_code == 200)

    def test_view_home_valid_user_not_authenticated(self):
        response = view_home(self.get_request)
        self.assertTrue(response.status_code == 200)

    def test_view_home_not_valid_request(self):
        self.assertRaises(PermissionDenied, view_home, self.post_request)

    def test_view_claims_sort_claims_by_newest(self):
        response = view_claims(self.get_request)
        self.assertTrue(response.status_code == 200)

    def test_view_claims_sort_claims_by_comments(self):
        self.get_request.GET['sort_method'] = 'Most commented'
        response = view_claims(self.get_request)
        self.assertTrue(response.status_code == 200)

    def test_view_claims_sort_claims_by_controversial(self):
        self.get_request.GET['sort_method'] = 'Most controversial'
        response = view_claims(self.get_request)
        self.assertTrue(response.status_code == 200)

    def test_sort_claims_by_comments(self):
        comment_1 = Comment(claim_id=self.claim_1.id,
                            user_id=self.claim_1.user_id,
                            title='title1',
                            description='description1',
                            url=self.url + str(random.randint(1, 10)),
                            verdict_date=datetime.date.today() - datetime.timedelta(days=random.randint(0, 10)),
                            label='True')
        comment_1.save()
        comment_2 = Comment(claim_id=self.claim_1.id,
                            user_id=self.claim_1.user_id,
                            title='title1',
                            description='description1',
                            url=self.url + str(random.randint(1, 10)),
                            verdict_date=datetime.date.today() - datetime.timedelta(days=random.randint(0, 10)),
                            label='True')
        comment_2.save()
        comment_3 = Comment(claim_id=self.claim_2.id,
                            user_id=self.claim_2.user_id,
                            title='title2',
                            description='description2',
                            url=self.url + str(random.randint(1, 10)),
                            verdict_date=datetime.date.today() - datetime.timedelta(days=random.randint(0, 10)),
                            label='False')
        comment_3.save()
        result = sort_claims_by_comments()
        self.assertTrue(result[0] == self.claim_1)
        self.assertTrue(result[1] == self.claim_2)
        self.assertTrue(result[2] == self.claim_3)

    def test_sort_claims_by_controversial(self):
        Claim.objects.filter(id=self.claim_1.id).update(authenticity_grade=50)
        Claim.objects.filter(id=self.claim_2.id).update(authenticity_grade=90)
        Claim.objects.filter(id=self.claim_3.id).update(authenticity_grade=30)
        result = sort_claims_by_controversial()
        self.assertTrue(result[0] == self.claim_1)
        self.assertTrue(result[1] == self.claim_3)
        self.assertTrue(result[2] == self.claim_2)

    def test_view_claim_valid(self):
        self.get_request.user = self.user
        response = view_claim(self.get_request, self.claim_1.id)
        self.assertTrue(response.status_code == 200)

    def test_view_claim_invalid_request(self):
        self.post_request.user = self.user
        self.assertRaises(PermissionDenied, view_claim, self.post_request, self.claim_1.id)

    def test_view_claim_valid_user_not_authenticated(self):
        from django.contrib.auth.models import AnonymousUser
        self.get_request.user = AnonymousUser()
        response = view_claim(self.get_request, self.claim_1.id)
        self.assertTrue(response.status_code == 200)

    def test_view_claim_with_comment(self):
        comment_1 = Comment(claim_id=self.claim_1.id,
                            user_id=self.user.id,
                            title='title1',
                            description='description1',
                            url='url1',
                            tags='tag1',
                            verdict_date=datetime.date.today() - datetime.timedelta(days=random.randint(0, 10)),
                            label='label1')
        comment_1.save()
        self.get_request.user = self.user
        response = view_claim(self.get_request, self.claim_1.id)
        self.assertTrue(response.status_code == 200)

    def test_view_claim_invalid_claim(self):
        self.get_request.user = self.user
        self.assertRaises(Http404, view_claim, self.get_request, self.num_of_saved_claims + random.randint(1, 10))

    def test_get_all_claims(self):
        self.assertTrue(len(get_all_claims()) == self.num_of_saved_claims)

    def test_get_all_claims_after_add_claim(self):
        len_claims = len(get_all_claims())
        self.claim_4.save()
        self.assertTrue(len(Claim.objects.all()) == len_claims + 1)

    def test_get_newest_claims_many_claims(self):
        for i in range(4, 24):
            claim = Claim(user_id=self.user.id, claim='claim' + str(i), category='category ' + str(i),
                          tags='tag' + str(i) + ' tag' + str(i + 1), authenticity_grade=0)
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
        self.assertTrue(result[0].tags == self.claim_3.tags)
        self.assertTrue(result[1].claim == self.claim_2.claim)
        self.assertTrue(result[1].category == self.claim_2.category)
        self.assertTrue(result[1].tags == self.claim_2.tags)
        self.assertTrue(result[2].claim == self.claim_1.claim)
        self.assertTrue(result[2].category == self.claim_1.category)
        self.assertTrue(result[2].tags == self.claim_1.tags)
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
        self.assertFalse(get_claim_by_id(self.num_of_saved_claims + 1) is None)
        claim_4_info = get_claim_by_id(self.num_of_saved_claims + 1)
        self.assertTrue(claim_4_info.claim == self.claim_4.claim)
        self.assertTrue(claim_4_info.category == self.claim_4.category)
        self.assertTrue(claim_4_info.tags == self.claim_4.tags)
        self.assertTrue(claim_4_info.authenticity_grade == self.claim_4.authenticity_grade)

    def test_get_claim_by_invalid_id(self):
        self.assertTrue(get_claim_by_id(self.num_of_saved_claims + 1) is None)

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

    def test_get_tags_after_adding_new_claim(self):
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.new_claim_details)
        self.post_request.POST = query_dict
        self.post_request.user = self.user
        self.assertTrue(add_claim(self.post_request).status_code == 200)
        self.assertTrue(get_tags_for_claim(self.num_of_saved_claims + 1) == ','.join(self.new_claim_details['tags'].split()))

    def test_get_tags_for_claim_invalid_claim(self):
        self.assertTrue(get_tags_for_claim(self.num_of_saved_claims + 1) is None)

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
        self.get_request.user = self.user
        response = add_claim_page(self.get_request)
        self.assertTrue(response.status_code == 200)

    def test_add_claim_page_user_not_authenticated(self):
        from django.contrib.auth.models import AnonymousUser
        self.get_request.user = AnonymousUser()
        self.assertRaises(PermissionDenied, add_claim_page, self.get_request)

    def test_export_claims_page(self):
        self.get_request.user = self.admin
        response = export_claims_page(self.get_request)
        self.assertTrue(response.status_code == 200)

    def test_export_claims_page_user_not_authenticated(self):
        from django.contrib.auth.models import AnonymousUser
        self.get_request.user = AnonymousUser()
        self.assertRaises(PermissionDenied, export_claims_page, self.get_request)

    def test_export_claims_page_invalid_request(self):
        self.post_request.user = self.user
        self.assertRaises(PermissionDenied, export_claims_page, self.post_request)

    def test_post_claims_tweets_page(self):
        self.get_request.user = self.user
        response = post_claims_tweets_page(self.get_request)
        self.assertTrue(response.status_code == 200)

    def test_post_claims_tweets_page_user_not_authenticated(self):
        from django.contrib.auth.models import AnonymousUser
        self.get_request.user = AnonymousUser()
        self.assertRaises(PermissionDenied, post_claims_tweets_page, self.get_request)

    def test_post_claims_tweets_page_invalid_request(self):
        self.post_request.user = self.user
        self.assertRaises(PermissionDenied, post_claims_tweets_page, self.post_request)

    def test_merging_claims_page(self):
        self.get_request.user = self.admin
        response = merging_claims_page(self.get_request)
        self.assertTrue(response.status_code == 200)

    def test_merging_claims_page_user_not_admin(self):
        self.get_request.user = self.user
        self.assertRaises(PermissionDenied, merging_claims_page, self.get_request)

    def test_merging_claims_page_user_not_authenticated(self):
        from django.contrib.auth.models import AnonymousUser
        self.get_request.user = AnonymousUser()
        self.assertRaises(PermissionDenied, merging_claims_page, self.get_request)

    def test_merging_claims_page_invalid_request(self):
        self.post_request.user = self.admin
        self.assertRaises(PermissionDenied, merging_claims_page, self.post_request)

    def test_about_page(self):
        self.assertTrue(about_page(HttpRequest()).status_code == 200)

    def test_handler_400(self):
        self.assertTrue(handler_400(HttpRequest(), 'error_msg').status_code == 400)

    def test_handler_403(self):
        self.assertTrue(handler_403(HttpRequest(), 'error_msg').status_code == 403)

    def test_handler_404(self):
        self.assertTrue(handler_404(HttpRequest(), 'error_msg').status_code == 404)

    def test_handler_500(self):
        self.assertTrue(handler_500(HttpRequest()).status_code == 500)

    def test_return_get_request_to_user(self):
        request = return_get_request_to_user(self.user)
        self.assertTrue(request.user == self.user)
        self.assertTrue(request.method == 'GET')

    ################
    # Models Tests #
    ################

    def test_claim_str(self):
        self.assertTrue(self.claim_1.__str__() == self.claim_1.user.username + ' - ' + self.claim_1.claim)
        self.assertTrue(self.claim_2.__str__() == self.claim_2.user.username + ' - ' + self.claim_2.claim)
        self.assertTrue(self.claim_3.__str__() == self.claim_3.user.username + ' - ' + self.claim_3.claim)

    def test_get_comments_for_claim(self):
        claim_1_comments = self.claim_1.get_comments_for_claim()
        self.assertTrue(len(claim_1_comments) == 1)
        comment = claim_1_comments.first()
        self.assertTrue(comment.id == self.comment_1.id)
        self.assertTrue(comment.claim_id == self.comment_1.claim_id)
        self.assertTrue(comment.user_id == self.comment_1.user_id)
        self.assertTrue(comment.title == self.comment_1.title)
        self.assertTrue(comment.description == self.comment_1.description)
        self.assertTrue(comment.url == self.comment_1.url)
        self.assertTrue(comment.verdict_date == self.comment_1.verdict_date)
        self.assertTrue(comment.label == self.comment_1.label)

        claim_2_comments = self.claim_2.get_comments_for_claim()
        self.assertTrue(len(claim_2_comments) == 1)
        comment = claim_2_comments.first()
        self.assertTrue(comment.id == self.comment_2.id)
        self.assertTrue(comment.claim_id == self.comment_2.claim_id)
        self.assertTrue(comment.user_id == self.comment_2.user_id)
        self.assertTrue(comment.title == self.comment_2.title)
        self.assertTrue(comment.description == self.comment_2.description)
        self.assertTrue(comment.url == self.comment_2.url)
        self.assertTrue(comment.verdict_date == self.comment_2.verdict_date)
        self.assertTrue(comment.label == self.comment_2.label)

        claim_3_comments = self.claim_3.get_comments_for_claim()
        self.assertTrue(len(claim_3_comments) == 1)
        comment = claim_3_comments.first()
        self.assertTrue(comment.id == self.comment_3.id)
        self.assertTrue(comment.claim_id == self.comment_3.claim_id)
        self.assertTrue(comment.user_id == self.comment_3.user_id)
        self.assertTrue(comment.title == self.comment_3.title)
        self.assertTrue(comment.description == self.comment_3.description)
        self.assertTrue(comment.url == self.comment_3.url)
        self.assertTrue(comment.verdict_date == self.comment_3.verdict_date)
        self.assertTrue(comment.label == self.comment_3.label)

    def test_get_tweets_for_claim(self):
        from tweets.models import Tweet
        tweet_link = 'https://twitter.com/'
        tweet_1 = Tweet.objects.create(claim=self.claim_1,
                                       tweet_link=tweet_link)
        tweet_2 = Tweet.objects.create(claim=self.claim_2,
                                       tweet_link=tweet_link)
        claim_1_tweets = self.claim_1.get_tweets_for_claim()
        self.assertTrue(len(claim_1_tweets) == 1)
        tweet = claim_1_tweets.first()
        self.assertTrue(tweet.id == tweet_1.id)
        self.assertTrue(tweet.tweet_link == tweet_link)

        claim_2_tweets = self.claim_2.get_tweets_for_claim()
        self.assertTrue(len(claim_2_tweets) == 1)
        tweet = claim_2_tweets.first()
        self.assertTrue(tweet.id == tweet_2.id)
        self.assertTrue(tweet.tweet_link == tweet_link)

        claim_3_tweets = self.claim_3.get_tweets_for_claim()
        self.assertTrue(len(claim_3_tweets) == 0)

    def test_users_commented_ids(self):
        user_2 = User(username='User2', email='user2@gmail.com')
        user_2.save()
        user_3 = User(username='User3', email='user3@gmail.com')
        user_3.save()
        user_4 = User(username='User4', email='user4@gmail.com')
        user_4.save()
        for i in range(5):
            comment = Comment(claim_id=self.claim_1.id,
                              user_id=user_2.id,
                              title='title' + str(i),
                              description='description' + str(i),
                              url=self.url + str(random.randint(1, 10)),
                              verdict_date=datetime.date.today() - datetime.timedelta(days=random.randint(0, 10)),
                              label='True')
            comment.save()
            comment = Comment(claim_id=self.claim_1.id,
                              user_id=user_3.id,
                              title='title' + str(i),
                              description='description' + str(i),
                              url=self.url + str(random.randint(1, 10)),
                              verdict_date=datetime.date.today() - datetime.timedelta(days=random.randint(0, 10)),
                              label='True')
            comment.save()
            comment = Comment(claim_id=self.claim_2.id,
                              user_id=user_3.id,
                              title='title' + str(i),
                              description='description' + str(i),
                              url=self.url + str(random.randint(1, 10)),
                              verdict_date=datetime.date.today() - datetime.timedelta(days=random.randint(0, 10)),
                              label='True')
            comment.save()
            if i % 2 == 0:
                comment = Comment(claim_id=self.claim_2.id,
                                  user_id=user_4.id,
                                  title='title' + str(i),
                                  description='description' + str(i),
                                  url=self.url + str(random.randint(1, 10)),
                                  verdict_date=datetime.date.today() - datetime.timedelta(days=random.randint(0, 10)),
                                  label='True')
                comment.save()
        claim_1_users_commented_ids = self.claim_1.users_commented_ids()
        self.assertTrue(len(claim_1_users_commented_ids) == 2)
        self.assertTrue(user_2.id in claim_1_users_commented_ids)
        self.assertTrue(user_3.id in claim_1_users_commented_ids)

        claim_2_users_commented_ids = self.claim_2.users_commented_ids()
        self.assertTrue(len(claim_2_users_commented_ids) == 1)
        self.assertTrue(user_3.id in claim_2_users_commented_ids)

        claim_3_users_commented_ids = self.claim_3.users_commented_ids()
        self.assertTrue(len(claim_3_users_commented_ids) == 0)

    def test_num_of_true_comments(self):
        Comment.objects.filter(id=self.comment_1.id).update(system_label='True')
        Comment.objects.filter(id=self.comment_2.id).update(system_label='False')
        self.assertTrue(self.claim_1.num_of_true_comments() == 1)
        self.assertTrue(self.claim_2.num_of_true_comments() == 0)

    def test_num_of_false_comments(self):
        Comment.objects.filter(id=self.comment_1.id).update(system_label='True')
        Comment.objects.filter(id=self.comment_2.id).update(system_label='False')
        self.assertTrue(self.claim_1.num_of_false_comments() == 0)
        self.assertTrue(self.claim_2.num_of_false_comments() == 1)

    def test_claim_report_str(self):
        from claims.models import Claims_Reports
        report_id = random.randint(1, 10)
        claim_report = Claims_Reports.objects.create(claim=self.claim_1, report_id=report_id)
        self.assertTrue(claim_report.__str__() == str(self.claim_1.id) + ' - ' + str(report_id))

    def test_merging_suggestion_str(self):
        from claims.models import Merging_Suggestions
        merging_suggestion = Merging_Suggestions.objects.create(claim=self.claim_1, claim_to_merge=self.claim_2)
        self.assertTrue(merging_suggestion.__str__() == str(self.claim_1.id) + ' - ' + str(self.claim_2.id))