from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, Http404, QueryDict
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils.datastructures import MultiValueDict
from claims.models import Claim
from tweets.views import add_tweet, build_tweet, check_if_tweet_is_valid, \
    delete_tweet, check_if_delete_tweet_is_valid, \
    export_to_csv, check_if_csv_fields_are_valid, check_if_fields_list_valid, create_df_for_tweets, \
    export_tweets_page, download_tweets_for_claims
from tweets.models import Tweet
from users.models import User
import datetime
import string
import random


class CommentTests(TestCase):
    def setUp(self):
        self.password = 'admin'
        self.admin = User.objects.create_superuser(username="admin", password=self.password, email='admin@gmail.com')
        self.user = User(username="User1", email='user1@gmail.com')
        self.user.save()
        self.num_of_saved_users = 2

        self.claim_1 = Claim(user_id=self.admin.id,
                             claim='claim1',
                             category='category1',
                             tags='tag1,tag2',
                             authenticity_grade=0)
        self.claim_2 = Claim(user_id=self.user.id,
                             claim='claim2',
                             category='category2',
                             tags='tag3,tag4',
                             authenticity_grade=0)
        self.claim_1.save()
        self.claim_2.save()
        self.num_of_saved_claims = 2

        self.tweet_1 = Tweet(claim_id=self.claim_1.id,
                             tweet_link='tweet_link1')
        self.tweet_2 = Tweet(claim_id=self.claim_2.id,
                             tweet_link='tweet_link2')
        self.tweet_3 = Tweet(claim_id=self.claim_2.id,
                             tweet_link='tweet_link3')

        self.tweet_1.save()
        self.tweet_2.save()
        self.num_of_saved_tweets = 2
        self.num_of_saved_authors = 3
        self.tweet_link = 'https://twitter.com/Israel/status/1112580470003458054'
        self.author_name = 'Israel'
        self.new_tweet_details = {'claim_id': self.claim_1.id,
                                  'tweet_link': self.tweet_link}

        self.post_request = HttpRequest()
        self.post_request.method = 'POST'
        self.get_request = HttpRequest()
        self.get_request.method = 'GET'

        self.csv_fields = MultiValueDict({
            'fields_to_export[]': ["Claim", "Tweet Link"],
            'date_start': [str(datetime.date.today() - datetime.timedelta(days=20))],
            'date_end': [str(datetime.date.today())]})

        self.test_file_data = {'claim_id': self.claim_1.id,
                               'tweet_link': 'tweet_link'}
        self.test_file = SimpleUploadedFile("tests.csv", open(
            'tweets/tests.csv', 'r', encoding='utf-8-sig').read().encode())
        self.test_file_invalid_header = SimpleUploadedFile("tests_invalid.csv", open(
            'tweets/tests_invalid.csv', 'r', encoding='utf-8-sig').read().encode())

        self.error_code = 404

    def test_add_tweet(self):
        len_tweets = len(Tweet.objects.filter(claim_id=self.claim_1.id))
        add_tweet(self.new_tweet_details)
        self.assertTrue(len(Tweet.objects.filter(claim_id=self.claim_1.id)) == len_tweets + 1)
        new_tweet = Tweet.objects.all().order_by('-id').first()
        self.assertTrue(new_tweet.id == self.num_of_saved_tweets + 1)
        self.assertTrue(new_tweet.claim_id == self.new_tweet_details['claim_id'])
        self.assertTrue(new_tweet.tweet_link == self.new_tweet_details['tweet_link'])

    def test_add_tweet_missing_claim_id(self):
        del self.new_tweet_details['claim_id']
        response = add_tweet(self.new_tweet_details)
        self.assertTrue(response.status_code == self.error_code)

    def test_add_comment_missing_tweet_link(self):
        del self.new_tweet_details['tweet_link']
        response = add_tweet(self.new_tweet_details)
        self.assertTrue(response.status_code == self.error_code)

    def test_add_tweet_missing_args(self):
        for i in range(10):
            dict_copy = self.new_tweet_details.copy()
            args_to_remove = []
            for j in range(0, (random.randint(1, len(self.new_tweet_details.keys()) - 1))):
                args_to_remove.append(list(self.new_tweet_details.keys())[j])
            for j in range(len(args_to_remove)):
                del self.new_tweet_details[args_to_remove[j]]
            len_tweets = len(Tweet.objects.filter(claim_id=self.claim_1.id))
            response = add_tweet(self.new_tweet_details)
            self.assertTrue(response.status_code == self.error_code)
            self.assertTrue(len(Tweet.objects.filter(claim_id=self.claim_1.id)) == len_tweets)
            self.new_tweet_details = dict_copy.copy()

    def test_build_tweet_by_user(self):
        len_tweets = len(Tweet.objects.all())
        build_tweet(self.tweet_3.claim_id, self.tweet_3.tweet_link)
        self.assertTrue(len(Tweet.objects.all()) == len_tweets + 1)
        new_tweet = Tweet.objects.all().order_by('-id').first()
        self.assertTrue(new_tweet.id == self.num_of_saved_tweets + 1)
        self.assertTrue(new_tweet.claim_id == self.tweet_3.claim_id)
        self.assertTrue(new_tweet.tweet_link == self.tweet_3.tweet_link)

    def test_build_tweet_by_added_user(self):
        len_tweets = len(Tweet.objects.all())
        user_2 = User(username="User2", email='user2@gmail.com')
        user_2.save()
        self.tweet_3.user_id = user_2.id
        build_tweet(self.tweet_3.claim_id, self.tweet_3.tweet_link)
        self.assertTrue(len(Tweet.objects.all()) == len_tweets + 1)
        new_tweet = Tweet.objects.all().order_by('-id').first()
        self.assertTrue(new_tweet.id == self.num_of_saved_tweets + 1)
        self.assertTrue(new_tweet.claim_id == self.tweet_3.claim_id)
        self.assertTrue(new_tweet.tweet_link == self.tweet_3.tweet_link)

    def test_check_if_tweet_is_valid(self):
        self.assertTrue(check_if_tweet_is_valid(self.new_tweet_details))

    def test_check_if_tweet_is_valid_missing_claim_id(self):
        del self.new_tweet_details['claim_id']
        self.assertFalse(check_if_tweet_is_valid(self.new_tweet_details)[0])

    def test_check_if_tweet_is_valid_missing_tweet_link(self):
        del self.new_tweet_details['tweet_link']
        self.assertFalse(check_if_tweet_is_valid(self.new_tweet_details)[0])

    def test_check_if_tweet_is_valid_invalid_tweet_link(self):
        letters = string.ascii_lowercase
        self.new_tweet_details['tweet_link'] = ''.join(random.choice(letters) for i in range(random.randint(1, 10)))
        self.assertFalse(check_if_tweet_is_valid(self.new_tweet_details)[0])

    def test_check_if_tweet_is_valid_invalid_claim_id(self):
        self.new_tweet_details['claim_id'] = str(self.num_of_saved_claims + random.randint(1, 10))
        self.assertFalse(check_if_tweet_is_valid(self.new_tweet_details)[0])

    def test_delete_tweet_by_user(self):
        tweet_to_delete = {'tweet_id': self.tweet_2.id}
        self.post_request.POST = tweet_to_delete
        self.post_request.user = self.admin
        len_tweets = len(Tweet.objects.all())
        response = delete_tweet(self.post_request)
        self.assertTrue(len(Tweet.objects.all()) == len_tweets - 1)
        self.assertTrue(response.status_code == 200)

    def test_delete_tweet_by_user_not_admin_user(self):
        tweet_to_delete = {'tweet_id': self.tweet_1.id}
        self.post_request.POST = tweet_to_delete
        self.post_request.user = self.user
        len_tweets = len(Tweet.objects.all())
        self.assertRaises(PermissionDenied, delete_tweet, self.post_request)
        self.assertTrue(len(Tweet.objects.all()) == len_tweets)

    def test_delete_tweet_by_invalid_tweet_id(self):
        tweet_to_delete = {'tweet_id': self.num_of_saved_tweets + random.randint(1, 10)}
        self.post_request.POST = tweet_to_delete
        self.post_request.user = self.admin
        len_tweets = len(Tweet.objects.all())
        response = delete_tweet(self.post_request)
        self.assertTrue(response.status_code == self.error_code)
        self.assertTrue(len(Tweet.objects.all()) == len_tweets)

    def test_delete_tweet_invalid_request(self):
        tweet_to_delete = {'tweet_id': self.tweet_1.id}
        self.get_request.POST = tweet_to_delete
        self.get_request.user = self.admin
        len_tweets = len(Tweet.objects.all())
        self.assertRaises(PermissionDenied, delete_tweet, self.get_request)
        self.assertTrue(len(Tweet.objects.all()) == len_tweets)

    def test_check_if_delete_tweet_is_valid(self):
        tweet_to_delete = {'tweet_id': self.tweet_2.id}
        self.post_request.POST = tweet_to_delete
        self.post_request.user = self.admin
        self.assertTrue(check_if_delete_tweet_is_valid(self.post_request)[0])

    def test_check_if_delete_tweet_is_valid_missing_tweet_id(self):
        self.post_request.user = self.admin
        self.assertFalse(check_if_delete_tweet_is_valid(self.post_request)[0])

    def test_check_if_delete_tweet_is_valid_invalid_tweet_id(self):
        tweet_to_delete = {'tweet_id': self.num_of_saved_tweets + random.randint(1, 10)}
        self.post_request.POST = tweet_to_delete
        self.post_request.user = self.admin
        self.assertFalse(check_if_delete_tweet_is_valid(self.post_request)[0])

    def test_export_to_csv(self):
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.csv_fields)
        self.post_request.POST = query_dict
        self.post_request.user = self.admin
        res = export_to_csv(self.post_request)
        self.assertTrue(res.status_code == 200)
        expected_info = 'Claim Id,Claim,Tweet Link\r\n'\
                        '' + str(self.tweet_1.claim_id) + ',' + self.tweet_1.claim.claim + ',' + \
                        '' + self.tweet_1.tweet_link + '\r\n' + \
                        '' + str(self.tweet_2.claim_id) + ',' + self.tweet_2.claim.claim + ',' + \
                        '' + self.tweet_2.tweet_link + '\r\n'
        self.assertEqual(res.content.decode('utf-8'), expected_info)

    def test_export_to_csv_invalid_arg_for_fields(self):
        import string
        fields_to_export = self.csv_fields.getlist('fields_to_export[]')
        fields_to_export.append(''.join(random.choices(string.ascii_uppercase + string.digits, k=random.randint(1, 20))))
        self.csv_fields.setlist('fields_to_export[]', fields_to_export)
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.csv_fields)
        self.post_request.POST = query_dict
        self.post_request.user = self.admin
        response = export_to_csv(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_export_to_csv_missing_args(self):
        for i in range(10):
            dict_copy = self.csv_fields.copy()
            args_to_remove = []
            for j in range(0, (random.randint(1, len(self.csv_fields.keys()) - 1))):
                args_to_remove.append(list(self.csv_fields.keys())[j])
            for j in range(len(args_to_remove)):
                del self.csv_fields[args_to_remove[j]]
            query_dict = QueryDict('', mutable=True)
            query_dict.update(self.csv_fields)
            self.post_request.POST = query_dict
            self.post_request.user = self.admin
            response = export_to_csv(self.post_request)
            self.assertTrue(response.status_code == self.error_code)
            self.csv_fields = dict_copy.copy()

    def test_export_to_csv_empty(self):
        self.post_request.user = self.admin
        Tweet.objects.all().delete()
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.csv_fields)
        self.post_request.POST = query_dict
        res = export_to_csv(self.post_request)
        self.assertTrue(res.status_code == 200)
        self.assertTrue(res.content.decode('utf-8') == 'Claim Id,Claim,Tweet Link\r\n')

    def test_export_to_csv_user_not_authenticated(self):
        from django.contrib.auth.models import AnonymousUser
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.csv_fields)
        self.post_request.POST = query_dict
        self.post_request.user = AnonymousUser()
        self.assertRaises(PermissionDenied, export_to_csv, self.post_request)

    def test_export_to_csv_not_admin_user(self):
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.csv_fields)
        self.post_request.POST = query_dict
        self.post_request.user = self.user
        self.assertRaises(PermissionDenied, export_to_csv, self.post_request)

    def test_check_if_csv_fields_are_valid(self):
        self.assertTrue(check_if_csv_fields_are_valid(self.csv_fields)[0])

    def test_check_if_csv_fields_are_valid_missing_actions_to_export(self):
        del self.csv_fields['fields_to_export[]']
        self.assertFalse(check_if_csv_fields_are_valid(self.csv_fields)[0])

    def test_check_if_csv_fields_are_valid_missing_date_start(self):
        del self.csv_fields['date_start']
        self.assertFalse(check_if_csv_fields_are_valid(self.csv_fields)[0])

    def test_check_if_csv_fields_are_valid_missing_date_end(self):
        del self.csv_fields['date_end']
        self.assertFalse(check_if_csv_fields_are_valid(self.csv_fields)[0])

    def test_check_if_csv_fields_are_valid_invalid_format_date_start(self):
        self.csv_fields['date_start'] = datetime.datetime.strftime(datetime.datetime.now() - datetime.timedelta(days=1),'%d.%m.%Y')
        self.assertFalse(check_if_csv_fields_are_valid(self.csv_fields)[0])
        self.csv_fields['date_start'] = datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=7),'%d/%m/%Y')
        self.assertFalse(check_if_csv_fields_are_valid(self.csv_fields)[0])
        self.csv_fields['date_start'] = datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=7),'%d/%m/%y')
        self.assertFalse(check_if_csv_fields_are_valid(self.csv_fields)[0])
        self.csv_fields['date_start'] = datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=7),'%Y/%m/%d')
        self.assertFalse(check_if_csv_fields_are_valid(self.csv_fields)[0])
        year = str(random.randint(2000, 2018))
        month = str(random.randint(1, 12))
        day = str(random.randint(1, 28))
        self.csv_fields['date_start'] = year + '--' + month + '-' + day
        self.assertFalse(check_if_csv_fields_are_valid(self.csv_fields)[0])
        self.csv_fields['date_start'] = year + '-' + month + '--' + day
        self.assertFalse(check_if_csv_fields_are_valid(self.csv_fields)[0])

    def test_check_if_csv_fields_are_valid_invalid_format_date_end(self):
        self.csv_fields['date_end'] = datetime.datetime.strftime(datetime.datetime.now() - datetime.timedelta(days=1),'%d.%m.%Y')
        self.assertFalse(check_if_csv_fields_are_valid(self.csv_fields)[0])
        self.csv_fields['date_end'] = datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=7),'%d/%m/%Y')
        self.assertFalse(check_if_csv_fields_are_valid(self.csv_fields)[0])
        self.csv_fields['date_end'] = datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=7),'%d/%m/%y')
        self.assertFalse(check_if_csv_fields_are_valid(self.csv_fields)[0])
        self.csv_fields['date_end'] = datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=7),'%Y/%m/%d')
        self.assertFalse(check_if_csv_fields_are_valid(self.csv_fields)[0])
        year = str(random.randint(2000, 2018))
        month = str(random.randint(1, 12))
        day = str(random.randint(1, 28))
        self.csv_fields['date_end'] = year + '--' + month + '-' + day
        self.assertFalse(check_if_csv_fields_are_valid(self.csv_fields)[0])
        self.csv_fields['date_end'] = year + '-' + month + '--' + day
        self.assertFalse(check_if_csv_fields_are_valid(self.csv_fields)[0])

    def test_check_if_fields_list_valid(self):
        self.assertTrue(check_if_fields_list_valid(self.csv_fields.getlist('fields_to_export[]'))[0])

    def test_check_if_fields_list_valid_invalid_field(self):
        import string
        new_fields = self.csv_fields.getlist('fields_to_export[]')
        new_fields.append(''.join(random.choices(string.ascii_uppercase + string.digits, k=random.randint(1, 20))))
        self.csv_fields.setlist('fields_to_export[]', new_fields)
        self.assertFalse(check_if_fields_list_valid(self.csv_fields.getlist('fields_to_export[]'))[0])

    def test_check_if_fields_list_valid_invalid_fields(self):
        import string
        new_fields = self.csv_fields.getlist('fields_to_export[]')
        for i in range(random.randint(1, 10)):
            new_fields.append(''.join(random.choices(string.ascii_uppercase + string.digits, k=random.randint(1, 20))))
        self.csv_fields.setlist('fields_to_export[]', new_fields)
        self.assertFalse(check_if_fields_list_valid(self.csv_fields.getlist('fields_to_export[]'))[0])

    def test_create_df_for_tweets(self):
        df_tweets = create_df_for_tweets(self.csv_fields.getlist('fields_to_export[]'),
                                         datetime.datetime.strptime(datetime.datetime.strptime(self.csv_fields.get('date_start'),
                                                                    '%Y-%m-%d').strftime('%d/%m/%Y'), '%d/%m/%Y').date(),
                                         datetime.datetime.strptime(datetime.datetime.strptime(self.csv_fields.get('date_end'),
                                                                    '%Y-%m-%d').strftime('%d/%m/%Y'), '%d/%m/%Y').date())
        self.assertTrue(len(df_tweets) == self.num_of_saved_tweets)
        for index, row in df_tweets.iterrows():
            if index == 0:
                self.assertTrue(row['Claim Id'] == self.tweet_1.claim.id)
                self.assertTrue(row['Claim'] == self.tweet_1.claim.claim)
                self.assertTrue(row['Tweet Link'] == self.tweet_1.tweet_link)
            elif index == 1:
                self.assertTrue(row['Claim Id'] == self.tweet_2.claim.id)
                self.assertTrue(row['Claim'] == self.tweet_2.claim.claim)
                self.assertTrue(row['Tweet Link'] == self.tweet_2.tweet_link)

    def test_export_claims_page(self):
        self.get_request.user = self.admin
        response = export_tweets_page(self.get_request)
        self.assertTrue(response.status_code == 200)

    def test_export_claims_page_user_not_authenticated(self):
        from django.contrib.auth.models import AnonymousUser
        self.get_request.user = AnonymousUser()
        self.assertRaises(PermissionDenied, export_tweets_page, self.get_request)

    def test_export_claims_page_invalid_request(self):
        self.post_request.user = self.admin
        self.assertRaises(PermissionDenied, export_tweets_page, self.post_request)

    def test_download_tweets_for_claims(self):
        self.post_request.FILES['csv_file'] = self.test_file
        self.post_request.user = self.admin
        len_tweets = len(Tweet.objects.filter(claim_id=self.claim_1.id))
        self.assertTrue(download_tweets_for_claims(self.post_request).status_code == 200)
        self.assertTrue(len(Tweet.objects.filter(claim_id=self.claim_1.id)) == len_tweets + 1)
        new_tweet = Tweet.objects.all().order_by('-id').first()
        self.assertTrue(new_tweet.id == self.num_of_saved_tweets + 1)
        self.assertTrue(new_tweet.claim_id == self.test_file_data['claim_id'])
        self.assertTrue(new_tweet.tweet_link == self.test_file_data['tweet_link'])

    def test_download_tweets_for_claims_not_admin_user(self):
        self.post_request.FILES['csv_file'] = self.test_file
        self.post_request.user = self.user
        len_tweets = len(Tweet.objects.all())
        self.assertRaises(PermissionDenied, download_tweets_for_claims, self.post_request)
        self.assertTrue(len(Tweet.objects.all()) == len_tweets)

    def test_download_tweets_for_claims_user_not_authenticated(self):
        from django.contrib.auth.models import AnonymousUser
        self.post_request.FILES['csv_file'] = self.test_file
        self.post_request.user = AnonymousUser()
        len_tweets = len(Tweet.objects.all())
        self.assertRaises(PermissionDenied, download_tweets_for_claims, self.post_request)
        self.assertTrue(len(Tweet.objects.all()) == len_tweets)

    def test_download_tweets_for_claims_user_authenticated(self):
        from django.contrib.auth.models import AnonymousUser
        details = {'username': self.admin.username, 'password': self.password}
        self.post_request.POST = details
        self.post_request.FILES['csv_file'] = self.test_file
        self.post_request.user = AnonymousUser()
        len_tweets = len(Tweet.objects.filter(claim_id=self.claim_1.id))
        self.assertTrue(download_tweets_for_claims(self.post_request).status_code == 200)
        self.assertTrue(len(Tweet.objects.filter(claim_id=self.claim_1.id)) == len_tweets + 1)
        new_tweet = Tweet.objects.all().order_by('-id').first()
        self.assertTrue(new_tweet.id == self.num_of_saved_tweets + 1)
        self.assertTrue(new_tweet.claim_id == self.test_file_data['claim_id'])
        self.assertTrue(new_tweet.tweet_link == self.test_file_data['tweet_link'])

    def test_download_tweets_for_claims_invalid_request(self):
        self.get_request.FILES['csv_file'] = self.test_file
        self.get_request.user = self.admin
        len_tweets = len(Tweet.objects.all())
        self.assertRaises(PermissionDenied, download_tweets_for_claims, self.get_request)
        self.assertTrue(len(Tweet.objects.all()) == len_tweets)

    def test_download_tweets_for_claims_invalid_file(self):
        self.post_request.user = self.admin
        len_tweets = len(Tweet.objects.all())
        self.assertRaises(PermissionDenied, download_tweets_for_claims, self.post_request)
        self.assertTrue(len(Tweet.objects.all()) == len_tweets)

    def test_download_tweets_for_claims_invalid_headers_in_file(self):
        self.post_request.FILES['csv_file'] = self.test_file_invalid_header
        self.post_request.user = self.admin
        len_tweets = len(Tweet.objects.all())
        self.assertRaises(Http404, download_tweets_for_claims, self.post_request)
        self.assertTrue(len(Tweet.objects.all()) == len_tweets)
