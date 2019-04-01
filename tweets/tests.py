from django.http import HttpRequest, Http404, QueryDict
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils.datastructures import MultiValueDict
from claims.models import Claim
from tweets.views import add_tweet, build_tweet, build_author, check_if_tweet_is_valid, is_valid_author, \
    edit_tweet, check_tweet_new_fields, delete_tweet, check_if_delete_tweet_is_valid, up_vote, down_vote, \
    check_if_vote_is_valid, set_user_label_to_tweet, check_if_tweet_label_is_valid, \
    export_to_csv, check_if_csv_fields_are_valid, check_if_fields_list_valid, create_df_for_tweets, \
    export_tweets_page, download_tweets_for_claims
from tweets.models import Tweet, Author
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

        self.author_1 = Author(author_name='author1',
                               author_rank=20)
        self.author_1.save()
        self.tweet_1 = Tweet(claim_id=self.claim_1.id,
                             user_id=self.admin.id,
                             author=self.author_1,
                             tweet_link='tweet_link1',
                             )

        self.author_2 = Author(author_name='author2',
                               author_rank=80)
        self.author_2.save()
        self.tweet_2 = Tweet(claim_id=self.claim_2.id,
                             user_id=self.user.id,
                             author=self.author_2,
                             tweet_link='tweet_link2',
                             )

        self.author_3 = Author(author_name='author3',
                               author_rank=60)
        self.author_3.save()
        self.tweet_3 = Tweet(claim_id=self.claim_2.id,
                             user_id=self.user.id,
                             author=self.author_3,
                             tweet_link='tweet_link3',
                             )

        self.tweet_1.save()
        self.tweet_2.save()
        self.num_of_saved_tweets = 2
        self.num_of_saved_authors = 3
        self.tweet_link = 'https://twitter.com/Israel/status/1112580470003458054'
        self.author_name = 'Israel'
        self.new_tweet_details = {'user_id': self.user.id,
                                  'is_superuser': False,
                                  'claim_id': self.claim_1.id,
                                  'tweet_link': self.tweet_link,
                                  'author_rank': '50'}

        self.update_tweet_details = {'tweet_id': self.tweet_2.id,
                                     'user_id': self.tweet_2.user_id,
                                     'is_superuser': False,
                                     'tweet_link': self.tweet_link,
                                     'author_rank': '40'}

        self.tweet_label = {'user_id': self.claim_2.user_id,
                            'is_superuser': False,
                            'tweet_id': self.tweet_2.id,
                            'label': 'True'}

        self.post_request = HttpRequest()
        self.post_request.method = 'POST'
        self.get_request = HttpRequest()
        self.get_request.method = 'GET'

        self.csv_fields = MultiValueDict({
            'fields_to_export[]': ["Claim", "Tweet Link", "Author", "Author Rank", "Label"],
            'date_start': [str(datetime.date.today() - datetime.timedelta(days=20))],
            'date_end': [str(datetime.date.today())]})

        self.test_file_data = {'claim_id': self.claim_1.id,
                               'user_id': self.admin.id,
                               'tweet_link': 'tweet_link',
                               'author': 'author1',
                               'author_rank': 0.5}
        self.test_file = SimpleUploadedFile("tests.csv", open(
            'tweets/tests.csv', 'r', encoding='utf-8-sig').read().encode())
        self.test_file_invalid_header = SimpleUploadedFile("tests_invalid.csv", open(
            'tweets/tests_invalid.csv', 'r', encoding='utf-8-sig').read().encode())

    def test_add_tweet(self):
        len_tweets = len(Tweet.objects.filter(claim_id=self.claim_1.id))
        self.post_request.POST = self.new_tweet_details
        self.post_request.user = self.user
        self.assertTrue(add_tweet(self.post_request).status_code == 200)
        self.assertTrue(len(Tweet.objects.filter(claim_id=self.claim_1.id)) == len_tweets + 1)
        new_tweet = Tweet.objects.all().order_by('-id').first()
        self.assertTrue(new_tweet.id == self.num_of_saved_tweets + 1)
        self.assertTrue(new_tweet.claim_id == self.new_tweet_details['claim_id'])
        self.assertTrue(new_tweet.user_id == self.new_tweet_details['user_id'])
        self.assertTrue(new_tweet.tweet_link == self.new_tweet_details['tweet_link'])
        self.assertTrue(new_tweet.author.author_name == self.author_name)
        self.assertTrue(new_tweet.author.author_rank == int(self.new_tweet_details['author_rank']))

    def test_add_tweet_by_user_not_authenticated(self):
        from django.contrib.auth.models import AnonymousUser
        self.post_request.POST = self.new_tweet_details
        self.post_request.user = AnonymousUser()
        self.assertRaises(Http404, add_tweet, self.post_request)

    def test_add_tweet_by_invalid_user(self):
        guest = User(id=self.num_of_saved_users + random.randint(1, 10), username='guest')
        self.new_tweet_details['user_id'] = guest.id
        self.post_request.POST = self.new_tweet_details
        self.post_request.user = guest
        self.assertRaises(Exception, add_tweet, self.post_request)

    def test_add_tweet_invalid_request(self):
        self.get_request.POST = self.new_tweet_details
        self.get_request.user = self.user
        self.assertRaises(Http404, add_tweet, self.get_request)

    def test_add_tweet_missing_claim_id(self):
        del self.new_tweet_details['claim_id']
        self.post_request.POST = self.new_tweet_details
        self.post_request.user = self.user
        self.assertRaises(Exception, add_tweet, self.post_request)

    def test_add_comment_missing_tweet_link(self):
        del self.new_tweet_details['tweet_link']
        self.post_request.POST = self.new_tweet_details
        self.post_request.user = self.user
        self.assertRaises(Exception, add_tweet, self.post_request)

    def test_add_comment_missing_author_rank(self):
        del self.new_tweet_details['author_rank']
        self.post_request.POST = self.new_tweet_details
        self.post_request.user = self.user
        self.assertRaises(Exception, add_tweet, self.post_request)

    def test_add_tweet_missing_args(self):
        del self.new_tweet_details['user_id']
        del self.new_tweet_details['is_superuser']
        for i in range(10):
            dict_copy = self.new_tweet_details.copy()
            args_to_remove = []
            for j in range(0, (random.randint(1, len(self.new_tweet_details.keys()) - 1))):
                args_to_remove.append(list(self.new_tweet_details.keys())[j])
            for j in range(len(args_to_remove)):
                del self.new_tweet_details[args_to_remove[j]]
            len_tweets = len(Tweet.objects.filter(claim_id=self.claim_1.id))
            self.post_request.POST = self.new_tweet_details
            self.post_request.user = self.user
            self.assertRaises(Exception, add_tweet, self.post_request)
            self.assertTrue(len(Tweet.objects.filter(claim_id=self.claim_1.id)) == len_tweets)
            self.new_tweet_details = dict_copy.copy()

    def test_build_tweet_by_user(self):
        len_tweets = len(Tweet.objects.all())
        build_tweet(self.tweet_3.claim_id,
                    self.tweet_3.user_id,
                    self.tweet_3.tweet_link,
                    self.tweet_3.author.author_name,
                    self.tweet_3.author.author_rank)
        self.assertTrue(len(Tweet.objects.all()) == len_tweets + 1)
        new_tweet = Tweet.objects.all().order_by('-id').first()
        self.assertTrue(new_tweet.id == self.num_of_saved_tweets + 1)
        self.assertTrue(new_tweet.claim_id == self.tweet_3.claim_id)
        self.assertTrue(new_tweet.user_id == self.tweet_3.user_id)
        self.assertTrue(new_tweet.tweet_link == self.tweet_3.tweet_link)
        self.assertTrue(new_tweet.author.author_name == self.tweet_3.author.author_name)
        self.assertTrue(new_tweet.author.author_rank == self.tweet_3.author.author_rank)

    def test_build_tweet_by_added_user(self):
        len_tweets = len(Tweet.objects.all())
        user_2 = User(username="User2", email='user2@gmail.com')
        user_2.save()
        self.tweet_3.user_id = user_2.id
        build_tweet(self.tweet_3.claim_id,
                    self.tweet_3.user_id,
                    self.tweet_3.tweet_link,
                    self.tweet_3.author.author_name,
                    self.tweet_3.author.author_rank)
        self.assertTrue(len(Tweet.objects.all()) == len_tweets + 1)
        new_tweet = Tweet.objects.all().order_by('-id').first()
        self.assertTrue(new_tweet.id == self.num_of_saved_tweets + 1)
        self.assertTrue(new_tweet.claim_id == self.tweet_3.claim_id)
        self.assertTrue(new_tweet.user_id == self.tweet_3.user_id)
        self.assertTrue(new_tweet.tweet_link == self.tweet_3.tweet_link)
        self.assertTrue(new_tweet.author.author_name == self.tweet_3.author.author_name)
        self.assertTrue(new_tweet.author.author_rank == self.tweet_3.author.author_rank)

    def test_build_existing_author(self):
        self.assertTrue(build_author(self.author_1.author_name, self.author_1.author_rank) == self.author_1)

    def test_build_existing_author_new_rank(self):
        new_author_rank = random.randint(1, 100)
        self.assertTrue(build_author(self.author_1.author_name, new_author_rank) == self.author_1)
        self.assertTrue(Author.objects.filter(author_name=self.author_1.author_name).first().author_rank ==
                        new_author_rank)

    def test_build_new_author(self):
        new_author_rank = random.randint(1, 100)
        new_author = build_author('author' + str(self.num_of_saved_authors), new_author_rank)
        self.assertTrue(new_author.author_name == 'author' + str(self.num_of_saved_authors))
        self.assertTrue(new_author.author_rank == new_author_rank)

    def test_check_if_tweet_is_valid(self):
        self.assertTrue(check_if_tweet_is_valid(self.new_tweet_details))

    def test_check_if_tweet_is_valid_missing_user_id(self):
        del self.new_tweet_details['user_id']
        self.assertFalse(check_if_tweet_is_valid(self.new_tweet_details)[0])

    def test_check_if_tweet_is_valid_missing_claim_id(self):
        del self.new_tweet_details['claim_id']
        self.assertFalse(check_if_tweet_is_valid(self.new_tweet_details)[0])

    def test_check_if_tweet_is_valid_missing_is_superuser(self):
        del self.new_tweet_details['is_superuser']
        self.assertFalse(check_if_tweet_is_valid(self.new_tweet_details)[0])

    def test_check_if_tweet_is_valid_missing_tweet_link(self):
        del self.new_tweet_details['tweet_link']
        self.assertFalse(check_if_tweet_is_valid(self.new_tweet_details)[0])

    def test_check_if_tweet_is_valid_invalid_tweet_link(self):
        letters = string.ascii_lowercase
        self.new_tweet_details['tweet_link'] = ''.join(random.choice(letters) for i in range(random.randint(1, 10)))
        self.assertFalse(check_if_tweet_is_valid(self.new_tweet_details)[0])

    def test_check_if_tweet_is_valid_invalid_tweet_author(self):
        self.new_tweet_details['tweet_link'] = 'https://twitter.com/'
        self.assertFalse(check_if_tweet_is_valid(self.new_tweet_details)[0])

    def test_check_if_tweet_is_valid_missing_author_rank(self):
        del self.new_tweet_details['author_rank']
        self.assertFalse(check_if_tweet_is_valid(self.new_tweet_details)[0])

    def test_check_if_tweet_is_valid_invalid_format_author_rank(self):
        self.new_tweet_details['author_rank'] = str(random.randint(1, 100)) + '.' + str(random.randint(1, 50))
        self.assertFalse(check_if_tweet_is_valid(self.new_tweet_details)[0])

    def test_check_if_tweet_is_valid_invalid_value_author_rank(self):
        self.new_tweet_details['author_rank'] = str(random.randint(1, 100) * -1)
        self.assertFalse(check_if_tweet_is_valid(self.new_tweet_details)[0])
        self.new_tweet_details['author_rank'] = str(random.randint(101, 300))
        self.assertFalse(check_if_tweet_is_valid(self.new_tweet_details)[0])

    def test_check_if_tweet_is_valid_invalid_claim_id(self):
        self.new_tweet_details['claim_id'] = str(self.num_of_saved_claims + random.randint(1, 10))
        self.assertFalse(check_if_tweet_is_valid(self.new_tweet_details)[0])

    def test_check_if_tweet_is_valid_invalid_user_id(self):
        self.new_tweet_details['user_id'] = str(self.num_of_saved_users + random.randint(1, 10))
        self.assertFalse(check_if_tweet_is_valid(self.new_tweet_details)[0])

    def test_check_if_tweet_is_valid_tweet_twice(self):
        self.new_tweet_details['claim_id'] = str(self.claim_2.id)
        self.assertFalse(check_if_tweet_is_valid(self.new_tweet_details)[0])

    def test_is_valid_author(self):
        self.assertTrue(is_valid_author(self.new_tweet_details))
        self.assertTrue(self.new_tweet_details['author_name'] == self.author_name)

    def test_is_valid_author_invalid(self):
        letters = string.ascii_lowercase
        self.new_tweet_details['tweet_link'] = ''.join(random.choice(letters) for i in range(random.randint(1, 10)))
        self.assertFalse(is_valid_author(self.new_tweet_details))

    def test_edit_tweet(self):
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.update_tweet_details)
        self.post_request.POST = query_dict
        self.post_request.user = self.user
        self.assertTrue(edit_tweet(self.post_request).status_code == 200)
        tweet = Tweet.objects.filter(id=self.tweet_2.id).first()
        self.assertTrue(tweet.tweet_link == self.update_tweet_details['tweet_link'])
        self.assertTrue(tweet.author.author_name == self.author_name)
        self.assertTrue(tweet.author.author_rank == int(self.update_tweet_details['author_rank']))

    def test_edit_tweet_by_user_not_his_tweet(self):
        new_user = User(username='newUser', email='newUser@gmail.com')
        new_user.save()
        self.update_tweet_details['user_id'] = str(self.num_of_saved_users + random.randint(1, 10))
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.update_tweet_details)
        self.post_request.POST = query_dict
        self.post_request.user = new_user
        self.assertRaises(Exception, edit_tweet, self.post_request)
        tweet = Tweet.objects.filter(id=self.tweet_2.id).first()
        self.assertTrue(tweet.tweet_link == self.tweet_2.tweet_link)
        self.assertTrue(tweet.author.author_name == self.tweet_2.author.author_name)
        self.assertTrue(tweet.author.author_rank == self.tweet_2.author.author_rank)

    def test_edit_tweet_by_invalid_user_id(self):
        user = User(id=self.num_of_saved_users + random.randint(1, 10), email='user@gmail.com')
        self.update_tweet_details['user_id'] = user.id
        self.update_tweet_details['tweet_id'] = str(self.tweet_2.id)
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.update_tweet_details)
        self.post_request.POST = query_dict
        self.post_request.user = user
        self.assertRaises(Exception, edit_tweet, self.post_request)
        tweet = Tweet.objects.filter(id=self.tweet_2.id).first()
        self.assertTrue(tweet.tweet_link == self.tweet_2.tweet_link)
        self.assertTrue(tweet.author.author_name == self.tweet_2.author.author_name)
        self.assertTrue(tweet.author.author_rank == self.tweet_2.author.author_rank)

    def test_edit_tweet_by_invalid_tweet_id(self):
        self.update_tweet_details['tweet_id'] = self.num_of_saved_tweets + random.randint(1, 10)
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.update_tweet_details)
        self.post_request.POST = query_dict
        self.post_request.user = self.user
        self.assertRaises(Exception, edit_tweet, self.post_request)
        tweet = Tweet.objects.filter(id=self.tweet_2.id).first()
        self.assertTrue(tweet.tweet_link == self.tweet_2.tweet_link)
        self.assertTrue(tweet.author.author_name == self.tweet_2.author.author_name)
        self.assertTrue(tweet.author.author_rank == self.tweet_2.author.author_rank)

    def test_edit_tweet_missing_args(self):
        for i in range(10):
            dict_copy = self.update_tweet_details.copy()
            args_to_remove = []
            for j in range(0, (random.randint(1, len(self.update_tweet_details.keys()) - 1))):
                args_to_remove.append(list(self.update_tweet_details.keys())[j])
            for j in range(len(args_to_remove)):
                del self.update_tweet_details[args_to_remove[j]]
            query_dict = QueryDict('', mutable=True)
            query_dict.update(self.update_tweet_details)
            self.post_request.POST = query_dict
            self.post_request.user = self.user
            self.assertRaises(Exception, edit_tweet, self.post_request)
            self.update_tweet_details = dict_copy.copy()

    def test_edit_tweet_by_invalid_request(self):
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.update_tweet_details)
        self.get_request.POST = query_dict
        self.get_request.user = self.user
        self.assertRaises(Http404, edit_tweet, self.get_request)
        tweet = Tweet.objects.filter(id=self.tweet_2.id).first()
        self.assertTrue(tweet.tweet_link == self.tweet_2.tweet_link)
        self.assertTrue(tweet.author.author_name == self.tweet_2.author.author_name)
        self.assertTrue(tweet.author.author_rank == self.tweet_2.author.author_rank)

    def test_check_tweet_new_fields(self):
        self.assertTrue(check_tweet_new_fields(self.update_tweet_details)[0])
        self.update_tweet_details['is_superuser'] = True
        self.assertTrue(check_tweet_new_fields(self.update_tweet_details)[0])

    def test_check_tweet_new_fields_missing_user_id(self):
        del self.update_tweet_details['user_id']
        self.assertFalse(check_tweet_new_fields(self.update_tweet_details)[0])

    def test_check_tweet_new_fields_invalid_user_id(self):
        self.update_tweet_details['user_id'] = str(self.num_of_saved_users + random.randint(1, 10))
        self.assertFalse(check_tweet_new_fields(self.update_tweet_details)[0])
        self.update_tweet_details['is_superuser'] = True
        self.assertFalse(check_tweet_new_fields(self.update_tweet_details)[0])

    def test_check_tweet_new_fields_missing_user_type(self):
        del self.update_tweet_details['is_superuser']
        self.assertFalse(check_tweet_new_fields(self.update_tweet_details)[0])

    def test_check_tweet_new_fields_missing_tweet_id(self):
        del self.update_tweet_details['tweet_id']
        self.assertFalse(check_tweet_new_fields(self.update_tweet_details)[0])
        self.update_tweet_details['is_superuser'] = True
        self.assertFalse(check_tweet_new_fields(self.update_tweet_details)[0])

    def test_check_tweet_new_fields_invalid_tweet_id(self):
        self.update_tweet_details['tweet_id'] = str(self.num_of_saved_tweets + random.randint(1, 10))
        self.assertFalse(check_tweet_new_fields(self.update_tweet_details)[0])
        self.update_tweet_details['is_superuser'] = True
        self.assertFalse(check_tweet_new_fields(self.update_tweet_details)[0])

    def test_check_tweet_new_fields_missing_tweet_link(self):
        del self.update_tweet_details['tweet_link']
        self.assertFalse(check_tweet_new_fields(self.update_tweet_details)[0])
        self.update_tweet_details['is_superuser'] = True
        self.assertFalse(check_tweet_new_fields(self.update_tweet_details)[0])

    def test_check_tweet_new_fields_missing_author_rank(self):
        del self.update_tweet_details['author_rank']
        self.assertFalse(check_tweet_new_fields(self.update_tweet_details)[0])
        self.update_tweet_details['is_superuser'] = True
        self.assertFalse(check_tweet_new_fields(self.update_tweet_details)[0])

    def test_check_tweet_new_fields_invalid_format_author_rank(self):
        self.update_tweet_details['author_rank'] = str(random.randint(1, 100)) + '.' + str(random.randint(1, 50))
        self.assertFalse(check_tweet_new_fields(self.update_tweet_details)[0])

    def test_check_tweet_new_fields_invalid_value_author_rank(self):
        self.update_tweet_details['author_rank'] = str(random.randint(1, 100) * -1)
        self.assertFalse(check_tweet_new_fields(self.update_tweet_details)[0])
        self.update_tweet_details['author_rank'] = str(random.randint(101, 300))
        self.assertFalse(check_tweet_new_fields(self.update_tweet_details)[0])

    def test_check_tweet_new_fields_tweet_not_belong_to_user(self):
        self.update_tweet_details['tweet_id'] = str(self.tweet_1.id)
        self.assertFalse(check_tweet_new_fields(self.update_tweet_details)[0])
        self.update_tweet_details['is_superuser'] = True
        self.assertTrue(check_tweet_new_fields(self.update_tweet_details)[0])

    def test_check_tweet_new_fields_edit_after_five_minutes(self):
        Tweet.objects.filter(id=self.tweet_2.id).update(timestamp=datetime.datetime.now() -
                                                        datetime.timedelta(minutes=6))
        self.assertFalse(check_tweet_new_fields(self.update_tweet_details)[0])
        self.update_tweet_details['is_superuser'] = True
        self.assertTrue(check_tweet_new_fields(self.update_tweet_details)[0])

    def test_delete_tweet_by_user(self):
        tweet_to_delete = {'tweet_id': self.tweet_2.id}
        self.post_request.POST = tweet_to_delete
        self.post_request.user = self.user
        len_tweets = len(Tweet.objects.all())
        response = delete_tweet(self.post_request)
        self.assertTrue(len(Tweet.objects.all()) == len_tweets - 1)
        self.assertTrue(response.status_code == 200)

    def test_delete_tweet_by_user_not_his_tweet(self):
        tweet_to_delete = {'tweet_id': self.tweet_1.id}
        self.post_request.POST = tweet_to_delete
        self.post_request.user = self.user
        len_tweets = len(Tweet.objects.all())
        self.assertRaises(Exception, delete_tweet, self.post_request)
        self.assertTrue(len(Tweet.objects.all()) == len_tweets)

    def test_delete_tweet_by_invalid_user(self):
        user = User(id=self.num_of_saved_users + random.randint(1, 10), email='user@gmail.com')
        tweet_to_delete = {'tweet_id': self.tweet_1.id}
        self.post_request.POST = tweet_to_delete
        self.post_request.user = user
        len_tweets = len(Tweet.objects.all())
        self.assertRaises(Exception, delete_tweet, self.post_request)
        self.assertTrue(len(Tweet.objects.all()) == len_tweets)

    def test_delete_tweet_by_not_authenticated_user(self):
        from django.contrib.auth.models import AnonymousUser
        tweet_to_delete = {'tweet_id': self.tweet_1.id}
        self.post_request.POST = tweet_to_delete
        self.post_request.user = AnonymousUser()
        len_tweets = len(Tweet.objects.all())
        self.assertRaises(Http404, delete_tweet, self.post_request)
        self.assertTrue(len(Tweet.objects.all()) == len_tweets)

    def test_delete_tweet_by_invalid_tweet_id(self):
        tweet_to_delete = {'tweet_id': self.num_of_saved_tweets + random.randint(1, 10)}
        self.post_request.POST = tweet_to_delete
        self.post_request.user = self.user
        len_tweets = len(Tweet.objects.all())
        self.assertRaises(Exception, delete_tweet, self.post_request)
        self.assertTrue(len(Tweet.objects.all()) == len_tweets)

    def test_delete_tweet_invalid_request(self):
        tweet_to_delete = {'tweet_id': self.tweet_1.id}
        self.get_request.POST = tweet_to_delete
        self.get_request.user = self.user
        len_tweets = len(Tweet.objects.all())
        self.assertRaises(Http404, delete_tweet, self.get_request)
        self.assertTrue(len(Tweet.objects.all()) == len_tweets)

    def test_check_if_delete_tweet_is_valid(self):
        tweet_to_delete = {'tweet_id': self.tweet_2.id}
        self.post_request.POST = tweet_to_delete
        self.post_request.user = self.user
        self.assertTrue(check_if_delete_tweet_is_valid(self.post_request)[0])

    def test_check_if_delete_tweet_is_valid_missing_tweet_id(self):
        self.post_request.user = self.user
        self.assertFalse(check_if_delete_tweet_is_valid(self.post_request)[0])

    def test_check_if_delete_tweet_is_valid_invalid_tweet_id(self):
        tweet_to_delete = {'tweet_id': self.num_of_saved_tweets + random.randint(1, 10)}
        self.post_request.POST = tweet_to_delete
        self.post_request.user = self.user
        self.assertFalse(check_if_delete_tweet_is_valid(self.post_request)[0])

    def test_check_if_delete_tweet_is_valid_invalid_user_id(self):
        user = User(id=self.num_of_saved_users + random.randint(1, 10), email='user@gmail.com')
        tweet_to_delete = {'tweet_id': self.tweet_2.id}
        self.post_request.POST = tweet_to_delete
        self.post_request.user = user
        self.assertFalse(check_if_delete_tweet_is_valid(self.post_request)[0])

    def test_check_if_delete_tweet_is_valid_another_user_tweet(self):
        tweet_to_delete = {'tweet_id': self.tweet_1.id}
        self.post_request.POST = tweet_to_delete
        self.post_request.user = self.user
        self.assertFalse(check_if_delete_tweet_is_valid(self.post_request)[0])
        self.post_request.user = self.admin
        self.assertTrue(check_if_delete_tweet_is_valid(self.post_request)[0])

    def test_up_vote(self):
        tweet_to_vote = {'tweet_id': self.tweet_1.id}
        query_dict = QueryDict('', mutable=True)
        query_dict.update(tweet_to_vote)
        self.post_request.POST = query_dict
        self.post_request.user = self.user
        self.assertRaises(Exception, up_vote, self.post_request)
        Tweet.objects.filter(id=self.tweet_1.id).update(timestamp=datetime.datetime.now() -
                                                        datetime.timedelta(minutes=6))
        self.assertTrue(up_vote(self.post_request).status_code == 200)
        self.assertTrue(self.tweet_1.up_votes.count() == 1)
        self.assertTrue(self.tweet_1.down_votes.count() == 0)

    def test_up_vote_twice(self):
        tweet_to_vote = {'tweet_id': self.tweet_1.id}
        query_dict = QueryDict('', mutable=True)
        query_dict.update(tweet_to_vote)
        self.post_request.POST = query_dict
        self.post_request.user = self.user
        self.assertRaises(Exception, up_vote, self.post_request)
        Tweet.objects.filter(id=self.tweet_1.id).update(timestamp=datetime.datetime.now() -
                                                        datetime.timedelta(minutes=6))
        self.assertTrue(up_vote(self.post_request).status_code == 200)
        self.assertTrue(up_vote(self.post_request).status_code == 200)
        self.assertTrue(self.tweet_1.up_votes.count() == 0)
        self.assertTrue(self.tweet_1.down_votes.count() == 0)

    def test_up_vote_after_down_vote(self):
        tweet_to_vote = {'tweet_id': self.tweet_1.id}
        query_dict = QueryDict('', mutable=True)
        query_dict.update(tweet_to_vote)
        self.post_request.POST = query_dict
        self.post_request.user = self.user
        self.assertRaises(Exception, down_vote, self.post_request)
        self.assertRaises(Exception, up_vote, self.post_request)
        Tweet.objects.filter(id=self.tweet_1.id).update(timestamp=datetime.datetime.now() -
                                                        datetime.timedelta(minutes=6))
        self.assertTrue(down_vote(self.post_request).status_code == 200)
        self.assertTrue(up_vote(self.post_request).status_code == 200)
        self.assertTrue(self.tweet_1.up_votes.count() == 1)
        self.assertTrue(self.tweet_1.down_votes.count() == 0)

    def test_up_vote_user_not_authenticated(self):
        from django.contrib.auth.models import AnonymousUser
        tweet_to_vote = {'tweet_id': self.tweet_1.id}
        query_dict = QueryDict('', mutable=True)
        query_dict.update(tweet_to_vote)
        self.post_request.POST = query_dict
        self.post_request.user = AnonymousUser()
        self.assertRaises(Http404, up_vote, self.post_request)

    def test_up_vote_invalid_request(self):
        user = User(id=self.num_of_saved_users + random.randint(1, 10), email="user@gmail.com")
        tweet_to_vote = {'tweet_id': self.tweet_1.id}
        query_dict = QueryDict('', mutable=True)
        query_dict.update(tweet_to_vote)
        self.get_request.POST = query_dict
        self.get_request.user = user
        self.assertRaises(Exception, up_vote, self.get_request)

    def test_up_vote_invalid_user(self):
        user = User(id=self.num_of_saved_users + random.randint(1, 10), email="user@gmail.com")
        tweet_to_vote = {'tweet_id': self.tweet_1.id}
        query_dict = QueryDict('', mutable=True)
        query_dict.update(tweet_to_vote)
        self.post_request.POST = query_dict
        self.post_request.user = user
        self.assertRaises(Exception, up_vote, self.post_request)

    def test_down_vote(self):
        tweet_to_vote = {'tweet_id': self.tweet_2.id}
        query_dict = QueryDict('', mutable=True)
        query_dict.update(tweet_to_vote)
        self.post_request.POST = query_dict
        self.post_request.user = self.user
        self.assertRaises(Exception, down_vote, self.post_request)
        Tweet.objects.filter(id=self.tweet_2.id).update(timestamp=datetime.datetime.now() -
                                                        datetime.timedelta(minutes=6))
        self.assertTrue(down_vote(self.post_request).status_code == 200)
        self.assertTrue(self.tweet_2.down_votes.count() == 1)
        self.assertTrue(self.tweet_2.up_votes.count() == 0)

    def test_down_vote_twice(self):
        tweet_to_vote = {'tweet_id': self.tweet_2.id}
        query_dict = QueryDict('', mutable=True)
        query_dict.update(tweet_to_vote)
        self.post_request.POST = query_dict
        self.post_request.user = self.user
        self.assertRaises(Exception, down_vote, self.post_request)
        Tweet.objects.filter(id=self.tweet_2.id).update(timestamp=datetime.datetime.now() -
                                                        datetime.timedelta(minutes=6))

        self.assertTrue(down_vote(self.post_request).status_code == 200)
        self.assertTrue(down_vote(self.post_request).status_code == 200)
        self.assertTrue(self.tweet_2.down_votes.count() == 0)
        self.assertTrue(self.tweet_2.down_votes.count() == 0)

    def test_down_vote_after_up_vote(self):
        tweet_to_vote = {'tweet_id': self.tweet_2.id}
        query_dict = QueryDict('', mutable=True)
        query_dict.update(tweet_to_vote)
        self.post_request.POST = query_dict
        self.post_request.user = self.user
        self.assertRaises(Exception, up_vote, self.post_request)
        self.assertRaises(Exception, down_vote, self.post_request)
        Tweet.objects.filter(id=self.tweet_2.id).update(timestamp=datetime.datetime.now() -
                                                        datetime.timedelta(minutes=6))

        self.assertTrue(up_vote(self.post_request).status_code == 200)
        self.assertTrue(down_vote(self.post_request).status_code == 200)
        self.assertTrue(self.tweet_2.up_votes.count() == 0)
        self.assertTrue(self.tweet_2.down_votes.count() == 1)

    def test_down_vote_user_not_authenticated(self):
        from django.contrib.auth.models import AnonymousUser
        tweet_to_vote = {'tweet_id': self.tweet_2.id}
        query_dict = QueryDict('', mutable=True)
        query_dict.update(tweet_to_vote)
        self.post_request.POST = query_dict
        self.post_request.user = AnonymousUser()
        self.assertRaises(Http404, down_vote, self.post_request)

    def test_down_vote_invalid_user(self):
        user = User(id=self.num_of_saved_users + random.randint(1, 10), email="user@gmail.com")
        tweet_to_vote = {'tweet_id': self.tweet_2.id}
        query_dict = QueryDict('', mutable=True)
        query_dict.update(tweet_to_vote)
        self.post_request.POST = query_dict
        self.post_request.user = user
        self.assertRaises(Exception, down_vote, self.post_request)

    def test_down_vote_invalid_request(self):
        tweet_to_vote = {'tweet_id': self.tweet_2.id}
        query_dict = QueryDict('', mutable=True)
        query_dict.update(tweet_to_vote)
        self.get_request.POST = query_dict
        self.get_request.user = self.user
        self.assertRaises(Exception, down_vote, self.get_request)

    def test_check_if_vote_is_valid(self):
        tweet_to_vote = {'tweet_id': self.tweet_1.id,
                         'user_id': self.user.id}
        self.assertFalse(check_if_vote_is_valid(tweet_to_vote)[0])
        Tweet.objects.filter(id=self.tweet_1.id).update(timestamp=datetime.datetime.now() -
                                                        datetime.timedelta(minutes=6))
        self.assertTrue(check_if_vote_is_valid(tweet_to_vote)[0])

    def test_check_if_vote_is_valid_missing_user_id(self):
        tweet_to_vote = {'tweet_id': self.tweet_1.id}
        self.assertFalse(check_if_vote_is_valid(tweet_to_vote)[0])

    def test_check_if_vote_is_valid_invalid_user_id(self):
        tweet_to_vote = {'tweet_to_vote': self.tweet_1.id,
                         'user_id': self.num_of_saved_users + random.randint(1, 10)}
        self.assertFalse(check_if_vote_is_valid(tweet_to_vote)[0])

    def test_check_if_vote_is_valid_missing_tweet_id(self):
        tweet_to_vote = {'user_id': self.user.id}
        self.assertFalse(check_if_vote_is_valid(tweet_to_vote)[0])

    def test_check_if_vote_is_valid_invalid_comment_id(self):
        tweet_to_vote = {'tweet_id': self.num_of_saved_tweets + random.randint(1, 10),
                         'user_id': self.user.id}
        self.assertFalse(check_if_vote_is_valid(tweet_to_vote)[0])

    def test_set_user_label_to_tweet(self):
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.tweet_label)
        self.post_request.POST = query_dict
        self.post_request.user = self.user
        self.assertTrue(set_user_label_to_tweet(self.post_request).status_code == 200)
        self.assertTrue(Tweet.objects.filter(id=self.tweet_2.id).first().label == 'True')

    def test_set_user_label_to_tweet_user_not_authenticated(self):
        from django.contrib.auth.models import AnonymousUser
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.tweet_label)
        self.post_request.POST = query_dict
        self.post_request.POST = query_dict
        self.post_request.user = AnonymousUser()
        self.assertRaises(Http404, set_user_label_to_tweet, self.post_request)

    def test_set_user_label_to_tweet_by_invalid_user(self):
        guest = User(id=self.num_of_saved_users + random.randint(1, 10), username='guest')
        self.new_tweet_details['user_id'] = guest.id
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.tweet_label)
        self.post_request.POST = query_dict
        self.post_request.user = guest
        self.assertRaises(Exception, set_user_label_to_tweet, self.post_request)

    def test_set_user_label_to_tweet_invalid_request(self):
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.tweet_label)
        self.get_request.POST = query_dict
        self.get_request.user = self.user
        self.assertRaises(Http404, set_user_label_to_tweet, self.get_request)

    def test_set_user_label_to_tweet_missing_tweet_id(self):
        del self.tweet_label['tweet_id']
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.tweet_label)
        self.get_request.POST = query_dict
        self.post_request.user = self.user
        self.assertRaises(Exception, set_user_label_to_tweet, self.post_request)

    def test_set_user_label_to_tweet_missing_label(self):
        del self.tweet_label['label']
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.tweet_label)
        self.get_request.POST = query_dict
        self.post_request.user = self.user
        self.assertRaises(Exception, set_user_label_to_tweet, self.post_request)

    def test_check_if_tweet_label_is_valid(self):
        self.assertTrue(check_if_tweet_label_is_valid(self.tweet_label)[0])
        self.tweet_label['is_superuser'] = True
        self.assertTrue(check_if_tweet_label_is_valid(self.tweet_label)[0])

    def test_check_if_tweet_label_is_valid_missing_user_id(self):
        del self.tweet_label['user_id']
        self.assertFalse(check_if_tweet_label_is_valid(self.tweet_label)[0])
        self.tweet_label['is_superuser'] = True
        self.assertFalse(check_if_tweet_label_is_valid(self.tweet_label)[0])

    def test_check_if_tweet_label_is_valid_invalid_user_id(self):
        self.tweet_label['user_id'] = self.num_of_saved_users + random.randint(1, 10)
        self.assertFalse(check_if_tweet_label_is_valid(self.tweet_label)[0])
        self.tweet_label['is_superuser'] = True
        self.assertFalse(check_if_tweet_label_is_valid(self.tweet_label)[0])

    def test_check_if_tweet_label_is_valid_missing_user_type(self):
        del self.tweet_label['is_superuser']
        self.assertFalse(check_if_tweet_label_is_valid(self.tweet_label)[0])

    def test_check_if_tweet_label_is_valid_missing_tweet_id(self):
        del self.tweet_label['tweet_id']
        self.assertFalse(check_if_tweet_label_is_valid(self.tweet_label)[0])
        self.tweet_label['is_superuser'] = True
        self.assertFalse(check_if_tweet_label_is_valid(self.tweet_label)[0])

    def test_check_if_tweet_label_is_valid_invalid_tweet_id(self):
        self.tweet_label['tweet_id'] = self.num_of_saved_tweets + random.randint(1, 10)
        self.assertFalse(check_if_tweet_label_is_valid(self.tweet_label)[0])
        self.tweet_label['is_superuser'] = True
        self.assertFalse(check_if_tweet_label_is_valid(self.tweet_label)[0])

    def test_check_if_tweet_label_is_valid_missing_label(self):
        del self.tweet_label['label']
        self.assertFalse(check_if_tweet_label_is_valid(self.tweet_label)[0])
        self.tweet_label['is_superuser'] = True
        self.assertFalse(check_if_tweet_label_is_valid(self.tweet_label)[0])

    def test_check_if_tweet_label_is_valid_invalid_claim_id(self):
        self.tweet_2.claim_id = self.num_of_saved_claims + random.randint(1, 10)
        self.tweet_2.save()
        self.assertFalse(check_if_tweet_label_is_valid(self.tweet_label)[0])
        self.tweet_label['is_superuser'] = True
        self.assertFalse(check_if_tweet_label_is_valid(self.tweet_label)[0])

    def test_check_if_tweet_label_is_valid_of_another_user(self):
        user_2 = User(username='user2', email='user2@gmail.com')
        user_2.save()
        self.tweet_label['user_id'] = user_2.id
        self.assertFalse(check_if_tweet_label_is_valid(self.tweet_label)[0])
        self.tweet_label['is_superuser'] = True
        self.assertTrue(check_if_tweet_label_is_valid(self.tweet_label)[0])

    def test_export_to_csv(self):
        Tweet.objects.filter(id=self.tweet_2.id).update(label='True')
        Tweet.objects.filter(id=self.tweet_1.id).update(label='False')
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.csv_fields)
        self.post_request.POST = query_dict
        self.post_request.user = self.admin
        res = export_to_csv(self.post_request)
        self.assertTrue(res.status_code == 200)
        expected_info = 'Claim Id,Claim,Tweet Link,Author,Author Rank,Label\r\n'\
                        '' + str(self.tweet_1.claim_id) + ',' + self.tweet_1.claim.claim + ',' + \
                        '' + self.tweet_1.tweet_link + ',' + self.tweet_1.author.author_name + ',' + \
                        '' + str(self.tweet_1.author.author_rank) + ',False\r\n' + \
                        '' + str(self.tweet_2.claim_id) + ',' + self.tweet_2.claim.claim + ',' + \
                        '' + self.tweet_2.tweet_link + ',' + self.tweet_2.author.author_name + ',' + \
                        '' + str(self.tweet_2.author.author_rank) + ',True\r\n'
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
        self.assertRaises(Exception, export_to_csv, self.post_request)

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
            self.assertRaises(Exception, export_to_csv, self.post_request)
            self.csv_fields = dict_copy.copy()

    def test_export_to_csv_empty(self):
        self.post_request.user = self.admin
        Tweet.objects.all().delete()
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.csv_fields)
        self.post_request.POST = query_dict
        res = export_to_csv(self.post_request)
        self.assertTrue(res.status_code == 200)
        self.assertTrue(res.content.decode('utf-8') == 'Claim Id,Claim,Tweet Link,Author,Author Rank,Label\r\n')

    def test_export_to_csv_user_not_authenticated(self):
        from django.contrib.auth.models import AnonymousUser
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.csv_fields)
        self.post_request.POST = query_dict
        self.post_request.user = AnonymousUser()
        self.assertRaises(Http404, export_to_csv, self.post_request)

    def test_export_to_csv_not_admin_user(self):
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.csv_fields)
        self.post_request.POST = query_dict
        self.post_request.user = self.user
        self.assertRaises(Http404, export_to_csv, self.post_request)

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
                self.assertTrue(row['Author'] == self.tweet_1.author.author_name)
                self.assertTrue(row['Author Rank'] == self.tweet_1.author.author_rank)
                self.assertTrue(row['Label'] == '')
            elif index == 1:
                self.assertTrue(row['Claim Id'] == self.tweet_2.claim.id)
                self.assertTrue(row['Claim'] == self.tweet_2.claim.claim)
                self.assertTrue(row['Tweet Link'] == self.tweet_2.tweet_link)
                self.assertTrue(row['Author'] == self.tweet_2.author.author_name)
                self.assertTrue(row['Author Rank'] == self.tweet_2.author.author_rank)
                self.assertTrue(row['Label'] == '')

    def test_export_claims_page(self):
        self.get_request.user = self.user
        response = export_tweets_page(self.get_request)
        self.assertTrue(response.status_code == 200)

    def test_export_claims_page_user_not_authenticated(self):
        from django.contrib.auth.models import AnonymousUser
        self.get_request.user = AnonymousUser()
        self.assertRaises(Http404, export_tweets_page, self.get_request)

    def test_export_claims_page_invalid_request(self):
        self.post_request.user = self.user
        self.assertRaises(Http404, export_tweets_page, self.post_request)

    def test_download_tweets_for_claims(self):
        self.post_request.FILES['csv_file'] = self.test_file
        self.post_request.user = self.admin
        len_tweets = len(Tweet.objects.filter(claim_id=self.claim_1.id))
        self.assertTrue(download_tweets_for_claims(self.post_request).status_code == 200)
        self.assertTrue(len(Tweet.objects.filter(claim_id=self.claim_1.id)) == len_tweets + 1)
        new_tweet = Tweet.objects.all().order_by('-id').first()
        self.assertTrue(new_tweet.id == self.num_of_saved_tweets + 1)
        self.assertTrue(new_tweet.claim_id == self.test_file_data['claim_id'])
        self.assertTrue(new_tweet.user_id == self.test_file_data['user_id'])
        self.assertTrue(new_tweet.tweet_link == self.test_file_data['tweet_link'])
        self.assertTrue(new_tweet.author.author_name == self.test_file_data['author'])
        self.assertTrue(new_tweet.author.author_rank == int(float(self.test_file_data['author_rank'] * 100)))

    def test_download_tweets_for_claims_not_admin_user(self):
        self.post_request.FILES['csv_file'] = self.test_file
        self.post_request.user = self.user
        len_tweets = len(Tweet.objects.all())
        self.assertRaises(Http404, download_tweets_for_claims, self.post_request)
        self.assertTrue(len(Tweet.objects.all()) == len_tweets)

    def test_download_tweets_for_claims_user_not_authenticated(self):
        from django.contrib.auth.models import AnonymousUser
        self.post_request.FILES['csv_file'] = self.test_file
        self.post_request.user = AnonymousUser()
        len_tweets = len(Tweet.objects.all())
        self.assertRaises(Http404, download_tweets_for_claims, self.post_request)
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
        self.assertTrue(new_tweet.user_id == self.test_file_data['user_id'])
        self.assertTrue(new_tweet.tweet_link == self.test_file_data['tweet_link'])
        self.assertTrue(new_tweet.author.author_name == self.test_file_data['author'])
        self.assertTrue(new_tweet.author.author_rank == int(float(self.test_file_data['author_rank'] * 100)))

    def test_download_tweets_for_claims_invalid_request(self):
        self.get_request.FILES['csv_file'] = self.test_file
        self.get_request.user = self.admin
        len_tweets = len(Tweet.objects.all())
        self.assertRaises(Http404, download_tweets_for_claims, self.get_request)
        self.assertTrue(len(Tweet.objects.all()) == len_tweets)

    def test_download_tweets_for_claims_invalid_file(self):
        self.post_request.user = self.admin
        len_tweets = len(Tweet.objects.all())
        self.assertRaises(Http404, download_tweets_for_claims, self.post_request)
        self.assertTrue(len(Tweet.objects.all()) == len_tweets)

    def test_download_tweets_for_claims_invalid_headers_in_file(self):
        self.post_request.FILES['csv_file'] = self.test_file_invalid_header
        self.post_request.user = self.admin
        len_tweets = len(Tweet.objects.all())
        self.assertRaises(Http404, download_tweets_for_claims, self.post_request)
        self.assertTrue(len(Tweet.objects.all()) == len_tweets)
