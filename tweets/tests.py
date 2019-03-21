from django.http import HttpRequest, Http404, QueryDict
from django.test import TestCase
from claims.models import Claim
from tweets.views import build_tweet, up_vote, down_vote, check_if_vote_is_valid, edit_tweet, \
    check_tweet_new_fields
from tweets.models import Tweet
from users.models import User
import datetime
import random


class CommentTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(username="admin", password='admin', email='admin@gmail.com')
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

        self.update_tweet_details = {'tweet_id': self.tweet_2.id,
                                     'user_id': self.tweet_2.user_id,
                                     'claim_id': self.tweet_2.claim_id,
                                     'tweet_link': 'new_tweet_link1',
                                     'author': 'new_author1',
                                     'author_rank': 40}

        self.post_request = HttpRequest()
        self.post_request.method = 'POST'
        self.get_request = HttpRequest()
        self.get_request.method = 'GET'

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
        self.assertTrue(tweet.author_rank == self.update_tweet_details['author_rank'])

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