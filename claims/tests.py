from django.http import HttpRequest, QueryDict, Http404
from django.test import TestCase, Client
from claims.models import Claim
from claims.views import add_claim, check_if_claim_is_valid, check_if_input_format_is_valid, is_english_input, \
    post_above_limit, get_all_claims, get_newest_claims, get_claim_by_id, get_category_for_claim, get_tags_for_claim,\
    view_claim, get_users_details_for_comments, get_user_img_and_rep, view_home, get_users_images_for_claims, logout_view, add_claim_page, export_claims_page, \
    edit_claim, check_claim_new_fields, delete_claim, check_if_delete_claim_is_valid, \
    handler_400, handler_403, handler_404, handler_500, about_page, report_spam, check_if_spam_report_is_valid, \
    return_get_request_to_user
from comments.models import Comment
from users.models import User, Users_Images, Scrapers, Users_Reputations
import random
import datetime
import string
import math


class ClaimTests(TestCase):
    def setUp(self):
        self.user = User(username='User1', email='user1@gmail.com')
        self.user.save()
        self.password = User.objects.make_random_password()
        self.scraper = User.objects.create_user(username='Scraper', password=self.password)
        self.user_image = Users_Images(user_id=self.user, user_img='user_img')
        self.user_image.save()
        self.rep = random.randint(1, 50)
        self.user_rep = Users_Reputations(user_id=self.user, user_rep=self.rep)
        self.user_rep.save()

        self.scraper_image = Users_Images(user_id=self.scraper, user_img='scraper_img')
        self.scraper_image.save()
        self.scraper_details = Scrapers(scraper_name=self.scraper.username, scraper_id=self.scraper)
        self.scraper_details.save()

        self.num_of_saved_users = 2
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
        self.comment_1 = Comment(claim_id=self.claim_1.id,
                                 user_id=self.claim_1.user_id,
                                 title='title1',
                                 description='description1',
                                 url='url1',
                                 verdict_date=datetime.date.today() - datetime.timedelta(days=random.randint(0, 10)),
                                 label='True')
        self.comment_2 = Comment(claim_id=self.claim_2.id,
                                 user_id=self.claim_2.user_id,
                                 title='title2',
                                 description='description2',
                                 url='url2',
                                 verdict_date=datetime.date.today() - datetime.timedelta(days=random.randint(0, 10)),
                                 label='False')
        self.comment_3 = Comment(claim_id=self.claim_3.id,
                                 user_id=self.claim_3.user_id,
                                 title='title3',
                                 description='description3',
                                 url='url3',
                                 verdict_date=datetime.date.today() - datetime.timedelta(days=random.randint(0, 10)),
                                 label='Unknown')

        self.comment_1.save()
        self.comment_2.save()
        self.comment_3.save()
        self.num_of_saved_comments = 3
        self.new_claim_details = {'claim': self.claim_4.claim,
                                  'title': 'title4',
                                  'description': 'description4',
                                  'url': 'url4',
                                  'add_comment': "true",
                                  'verdict_date': datetime.datetime.strptime(str(datetime.date.today() - datetime.timedelta(days=random.randint(0, 10))), '%Y-%m-%d').strftime('%d/%m/%Y'),
                                  'tags': self.claim_4.tags,
                                  'category': self.claim_4.category,
                                  'label': 'False',
                                  'image_src': self.claim_4.image_src}
        self.post_request = HttpRequest()
        self.post_request.method = 'POST'
        self.get_request = HttpRequest()
        self.get_request.method = 'GET'
        self.update_claim_details = {'claim_id': self.claim_1.id,
                                     'claim': 'newClaim1',
                                     'category': 'newCategory1',
                                     'tags': 'newTag1,newTag2,newTag3,newTag4',
                                     'image_src': 'image1'}

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
        self.assertTrue(claim_4.tags == ','.join(self.new_claim_details['tags'].split()))
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
        self.assertTrue(check_if_claim_is_valid(self.new_claim_details)[0])

    def test_check_if_claim_is_valid_invalid_format_for_tags(self):
        invalid_input = 'tag1,'
        for i in range(random.randint(1, 10)):
            invalid_input += ' '
        invalid_input += ',tag2'
        self.new_claim_details['user_id'] = self.user.id
        self.new_claim_details['tags'] = invalid_input
        self.assertFalse(check_if_claim_is_valid(self.new_claim_details)[0])

    def test_check_if_claim_is_valid_missing_img_src(self):
        self.new_claim_details['user_id'] = self.user.id
        del self.new_claim_details['image_src']
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

    def test_check_if_claim_is_valid_invalid_input_for_claim(self):
        self.new_claim_details['user_id'] = self.user.id
        self.new_claim_details['claim'] = 'קלט בשפה שאינה אנגלית'
        self.assertFalse(check_if_claim_is_valid(self.new_claim_details)[0])

    def test_check_if_claim_is_valid_invalid_input_for_category(self):
        self.new_claim_details['user_id'] = self.user.id
        self.new_claim_details['category'] = 'المدخلات بلغة غير الإنجليزية'
        self.assertFalse(check_if_claim_is_valid(self.new_claim_details)[0])

    def test_check_if_claim_is_valid_invalid_input_for_tags(self):
        self.new_claim_details['user_id'] = self.user.id
        self.new_claim_details['category'] = '输入英语以外的语言 输入英语以外的语言'
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

    def test_view_claim_valid(self):
        self.get_request.user = self.user
        response = view_claim(self.get_request, self.claim_1.id)
        self.assertTrue(response.status_code == 200)

    def test_view_claim_invalid_request(self):
        self.post_request.user = self.user
        self.assertRaises(Http404, view_claim, self.post_request, self.claim_1.id)

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

    def test_get_users_details_for_comments_for_user(self):
        user_1_comment = Comment.objects.filter(claim_id=self.claim_1.id, user_id=self.user.id).first()
        user_2_comment = Comment.objects.filter(claim_id=self.claim_2.id, user_id=self.user.id).first()
        user_3_comment = Comment.objects.filter(claim_id=self.claim_3.id, user_id=self.user.id).first()
        comments_with_details = get_users_details_for_comments(Comment.objects.filter(user_id=self.user.id).order_by('-id'))
        self.assertTrue(len(comments_with_details) == self.num_of_saved_comments)
        self.assertTrue(comments_with_details[user_3_comment]['user'] == self.user)
        self.assertTrue(comments_with_details[user_3_comment]['user_img'] == self.user_image)
        self.assertTrue(comments_with_details[user_3_comment]['user_rep'] == math.ceil(self.rep / 20))

        self.assertTrue(comments_with_details[user_2_comment]['user'] == self.user)
        self.assertTrue(comments_with_details[user_2_comment]['user_img'] == self.user_image)
        self.assertTrue(comments_with_details[user_2_comment]['user_rep'] == math.ceil(self.rep / 20))

        self.assertTrue(comments_with_details[user_1_comment]['user'] == self.user)
        self.assertTrue(comments_with_details[user_1_comment]['user_img'] == self.user_image)
        self.assertTrue(comments_with_details[user_1_comment]['user_rep'] == math.ceil(self.rep / 20))

    def test_get_users_details_for_comments_with_new_user_and_comment(self):
        user_2 = User(username='User2', email='user2@gmail.com')
        user_2.save()
        new_user_comment = Comment(claim_id=self.claim_1.id,
                                   user_id=user_2.id,
                                   title='title2',
                                   description='description2',
                                   url='url2',
                                   verdict_date=datetime.date.today() - datetime.timedelta(days=random.randint(0, 10)),
                                   label='False')
        new_user_comment.save()
        user_1_comment = Comment.objects.filter(claim_id=self.claim_1.id, user_id=self.user.id).first()
        from django.db.models import Q
        comments_with_details = get_users_details_for_comments(Comment.objects.filter(claim_id=self.claim_1.id).filter(
            Q(user_id=self.user.id) | Q(user_id=user_2.id)).order_by('-id'))
        self.assertTrue(len(comments_with_details) == 2)
        user_2_img = Users_Images.objects.filter(user_id=user_2).first()
        self.assertTrue(comments_with_details[new_user_comment]['user'] == user_2)
        self.assertTrue(comments_with_details[new_user_comment]['user_img'] == user_2_img)
        self.assertTrue(comments_with_details[new_user_comment]['user_rep'] == 1)
        self.assertTrue(comments_with_details[user_1_comment]['user'] == self.user)
        self.assertTrue(comments_with_details[user_1_comment]['user_img'] == self.user_image)
        self.assertTrue(comments_with_details[user_1_comment]['user_rep'] == math.ceil(self.rep / 20))

    def test_get_users_details_for_empty_comments(self):
        Comment.objects.all().delete()
        comments_with_details = get_users_details_for_comments(Comment.objects.all())
        self.assertTrue(len(comments_with_details) == 0)

    def test_get_user_img_and_rep_for_not_authenticated_user(self):
        from django.contrib.auth.models import AnonymousUser
        self.get_request.user = AnonymousUser()
        user_img, user_rep = get_user_img_and_rep(self.get_request)
        self.assertTrue(user_img is None)
        self.assertTrue(user_rep is None)

    def test_get_user_img_and_rep_for_new_user(self):
        user_2 = User(username='User2', email='user2@gmail.com')
        user_2.save()
        self.get_request.user = user_2
        user_img, user_rep = get_user_img_and_rep(self.get_request)

        self.assertTrue(user_img == Users_Images.objects.filter(user_id=user_2).first().user_img)
        self.assertTrue(user_rep == math.ceil((Users_Reputations.objects.filter(user_id=user_2).first().user_rep) / 20))

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
        self.assertRaises(Http404, view_home, self.post_request)

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
        self.get_request.user = self.user
        response = add_claim_page(self.get_request)
        self.assertTrue(response.status_code == 200)

    def test_add_claim_page_user_not_authenticated(self):
        from django.contrib.auth.models import AnonymousUser
        self.get_request.user = AnonymousUser()
        self.assertRaises(Http404, add_claim_page, self.get_request)

    def test_export_claims_page(self):
        self.get_request.user = self.user
        response = export_claims_page(self.get_request)
        self.assertTrue(response.status_code == 200)

    def test_export_claims_page_user_not_authenticated(self):
        from django.contrib.auth.models import AnonymousUser
        self.get_request.user = AnonymousUser()
        self.assertRaises(Http404, export_claims_page, self.get_request)

    def test_edit_claim_valid_with_different_claim(self):
        self.update_claim_details['claim'] = self.claim_1.claim + '_new'
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.update_claim_details)
        self.post_request.POST = query_dict
        self.post_request.user = self.user
        self.assertTrue(edit_claim(self.post_request).status_code == 200)
        self.assertTrue(Claim.objects.filter(id=self.update_claim_details['claim_id'])[0].claim == self.claim_1.claim + '_new')

    def test_edit_claim_with_existing_claim(self):
        self.update_claim_details['claim'] = self.claim_2
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.update_claim_details)
        self.post_request.POST = query_dict
        self.post_request.user = self.user
        self.assertRaises(Exception, edit_claim, self.post_request)

    def test_edit_claim_with_user_not_authenticated(self):
        from django.contrib.auth.models import AnonymousUser
        self.post_request.POST = self.update_claim_details
        self.post_request.user = AnonymousUser()
        self.assertRaises(Http404, edit_claim, self.post_request)

    def test_edit_claim_with_invalid_user(self):
        guest = User(id=self.num_of_saved_users + random.randint(1, 10), username='guest')
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.update_claim_details)
        self.post_request.POST = query_dict
        self.post_request.user = guest
        self.assertRaises(Exception, edit_claim, self.post_request)

    def test_edit_claim_invalid_request(self):
        self.get_request.user = self.user
        self.assertRaises(Http404, edit_claim, self.get_request)

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
            self.assertRaises(Exception, edit_claim, self.post_request)
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
        self.assertFalse(check_claim_new_fields(self.update_claim_details)[0])
        self.update_claim_details['is_superuser'] = True
        self.assertFalse(check_claim_new_fields(self.update_claim_details)[0])

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
                                                        datetime.timedelta(minutes=6))
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

    def test_delete_claim_invalid_request(self):
        self.get_request.user = self.user
        self.assertRaises(Http404, delete_claim, self.get_request)

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
        self.assertRaises(Exception, report_spam, self.post_request)

    def test_report_spam_user_not_authenticated(self):
        from django.contrib.auth.models import AnonymousUser
        claim_to_report_spam = {'claim_id': self.claim_1.id}
        self.post_request.POST = claim_to_report_spam
        self.post_request.user = AnonymousUser()
        self.assertRaises(Exception, report_spam, self.post_request)

    def test_report_spam_invalid_request(self):
        self.get_request.user = self.user
        self.assertRaises(Exception, report_spam, self.get_request)

    def test_report_spam_missing_claim_id(self):
        self.post_request.POST = {}
        self.post_request.user = self.scraper
        self.assertRaises(Exception, report_spam, self.post_request)

    def test_report_spam_invalid_user(self):
        guest = User(id=self.num_of_saved_users + random.randint(1, 10), username='guest')
        claim_to_report_spam = {'claim_id': self.claim_1.id}
        self.post_request.POST = claim_to_report_spam
        self.post_request.user = guest
        self.assertRaises(Exception, report_spam, self.post_request)

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

    def test_return_get_request_to_user(self):
        request = return_get_request_to_user(self.user)
        self.assertTrue(request.user == self.user)
        self.assertTrue(request.method == 'GET')

