from django.http import HttpRequest, Http404, QueryDict
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from claims.models import Claim
from tweets.views import add_tweet, build_tweet, check_if_tweet_is_valid, up_vote, down_vote, \
    check_if_vote_is_valid, edit_tweet, check_tweet_new_fields, delete_tweet, check_if_delete_tweet_is_valid, \
    post_tweets_page, download_tweets_for_claims
from tweets.models import Tweet
from users.models import User
import datetime
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
                             user_id=self.admin.id,
                             tweet_link='tweet_link1',
                             author='author1',
                             author_rank=20,
                             )

        self.tweet_2 = Tweet(claim_id=self.claim_2.id,
                             user_id=self.user.id,
                             tweet_link='tweet_link2',
                             author='author2',
                             author_rank=80,
                             )

        self.tweet_3 = Tweet(claim_id=self.claim_2.id,
                             user_id=self.user.id,
                             tweet_link='tweet_link3',
                             author='author3',
                             author_rank=60,
                             )

        self.tweet_1.save()
        self.tweet_2.save()
        self.num_of_saved_tweets = 2

        self.new_tweet_details = {'user_id': self.user.id,
                                  'is_superuser': False,
                                  'claim_id': self.claim_1.id,
                                  'tweet_link': 'tweet_link1',
                                  'author': 'author1',
                                  'author_rank': '50'}

        self.update_tweet_details = {'tweet_id': self.tweet_2.id,
                                     'user_id': self.tweet_2.user_id,
                                     'is_superuser': False,
                                     'tweet_link': 'new_tweet_link1',
                                     'author': 'new_author1',
                                     'author_rank': '40'}

        self.post_request = HttpRequest()
        self.post_request.method = 'POST'
        self.get_request = HttpRequest()
        self.get_request.method = 'GET'

        self.test_file_data = {'claim_id': self.claim_1.id,
                          'user_id': self.admin.id,
                          'tweet_link': 'tweet_link',
                          'author': 'author1',
                          'author_rank': 0.5}
        self.test_file = SimpleUploadedFile("tests.csv", open(
            'tweets/tests.csv', 'rb').read())

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
        self.assertTrue(new_tweet.author == self.new_tweet_details['author'])
        self.assertTrue(new_tweet.author_rank == int(self.new_tweet_details['author_rank']))

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

    def test_add_comment_missing_author(self):
        del self.new_tweet_details['author']
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
                    self.tweet_3.author,
                    self.tweet_3.author_rank)
        self.assertTrue(len(Tweet.objects.all()) == len_tweets + 1)
        new_tweet = Tweet.objects.all().order_by('-id').first()
        self.assertTrue(new_tweet.id == self.num_of_saved_tweets + 1)
        self.assertTrue(new_tweet.claim_id == self.tweet_3.claim_id)
        self.assertTrue(new_tweet.user_id == self.tweet_3.user_id)
        self.assertTrue(new_tweet.tweet_link == self.tweet_3.tweet_link)
        self.assertTrue(new_tweet.author == self.tweet_3.author)
        self.assertTrue(new_tweet.author_rank == self.tweet_3.author_rank)

    def test_build_tweet_by_added_user(self):
        len_tweets = len(Tweet.objects.all())
        user_2 = User(username="User2", email='user2@gmail.com')
        user_2.save()
        self.tweet_3.user_id = user_2.id
        build_tweet(self.tweet_3.claim_id,
                    self.tweet_3.user_id,
                    self.tweet_3.tweet_link,
                    self.tweet_3.author,
                    self.tweet_3.author_rank)
        self.assertTrue(len(Tweet.objects.all()) == len_tweets + 1)
        new_tweet = Tweet.objects.all().order_by('-id').first()
        self.assertTrue(new_tweet.id == self.num_of_saved_tweets + 1)
        self.assertTrue(new_tweet.claim_id == self.tweet_3.claim_id)
        self.assertTrue(new_tweet.user_id == self.tweet_3.user_id)
        self.assertTrue(new_tweet.tweet_link == self.tweet_3.tweet_link)
        self.assertTrue(new_tweet.author == self.tweet_3.author)
        self.assertTrue(new_tweet.author_rank == self.tweet_3.author_rank)

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

    def test_check_if_tweet_is_valid_missing_author(self):
        del self.new_tweet_details['author']
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

    def test_check_if_tweet_is_valid_invalid_input_for_author(self):
        self.new_tweet_details['author'] = 'קלט בשפה שאינה אנגלית'
        self.assertFalse(check_if_tweet_is_valid(self.new_tweet_details)[0])

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

    def test_edit_tweet(self):
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.update_tweet_details)
        self.post_request.POST = query_dict
        self.post_request.user = self.user
        self.assertTrue(edit_tweet(self.post_request).status_code == 200)
        tweet = Tweet.objects.filter(id=self.tweet_2.id).first()
        self.assertTrue(tweet.tweet_link == self.update_tweet_details['tweet_link'])
        self.assertTrue(tweet.author == self.update_tweet_details['author'])
        self.assertTrue(tweet.author_rank == int(self.update_tweet_details['author_rank']))

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
        self.assertTrue(tweet.author == self.tweet_2.author)
        self.assertTrue(tweet.author_rank == self.tweet_2.author_rank)

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
        self.assertTrue(tweet.author == self.tweet_2.author)
        self.assertTrue(tweet.author_rank == self.tweet_2.author_rank)

    def test_edit_tweet_by_invalid_tweet_id(self):
        self.update_tweet_details['tweet_id'] = self.num_of_saved_tweets + random.randint(1, 10)
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.update_tweet_details)
        self.post_request.POST = query_dict
        self.post_request.user = self.user
        self.assertRaises(Exception, edit_tweet, self.post_request)
        tweet = Tweet.objects.filter(id=self.tweet_2.id).first()
        self.assertTrue(tweet.tweet_link == self.tweet_2.tweet_link)
        self.assertTrue(tweet.author == self.tweet_2.author)
        self.assertTrue(tweet.author_rank == self.tweet_2.author_rank)

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
        self.assertTrue(tweet.author == self.tweet_2.author)
        self.assertTrue(tweet.author_rank == self.tweet_2.author_rank)

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

    def test_check_tweet_new_fields_missing_author(self):
        del self.update_tweet_details['author']
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

    def test_check_tweet_new_fields_invalid_input_for_author(self):
        self.update_tweet_details['author'] = 'Խոսք'
        self.assertFalse(check_tweet_new_fields(self.update_tweet_details)[0])
        self.update_tweet_details['is_superuser'] = True
        self.assertFalse(check_tweet_new_fields(self.update_tweet_details)[0])

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

    def test_download_tweets_page(self):
        self.get_request.user = self.admin
        self.assertTrue(post_tweets_page(self.get_request).status_code == 200)

    def test_download_tweets_page_not_admin_user(self):
        self.get_request.user = self.user
        self.assertRaises(Http404, post_tweets_page, self.get_request)

    def test_download_tweets_page_invalid_request(self):
        self.post_request.user = self.admin
        self.assertRaises(Http404, post_tweets_page, self.post_request)

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
        self.assertTrue(new_tweet.author == self.test_file_data['author'])
        self.assertTrue(new_tweet.author_rank == int(float(self.test_file_data['author_rank'] * 100)))

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
        details = {'username':self.admin.username, 'password': self.password}
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
        self.assertTrue(new_tweet.author == self.test_file_data['author'])
        self.assertTrue(new_tweet.author_rank == int(float(self.test_file_data['author_rank'] * 100)))

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