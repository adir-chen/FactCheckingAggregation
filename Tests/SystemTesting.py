import datetime
from django.contrib.auth.models import User
from django.http import HttpRequest, QueryDict
from django.test import TestCase
from claims.models import Claim
from comments.models import Comment
import random
from claims.views import add_claim, edit_claim, delete_claim
from comments.views import export_to_csv, up_vote, down_vote, add_comment, edit_comment, delete_comment
from contact_us.views import send_email
from users.views import add_new_scraper


class SystemTesting(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="User", email='user1@gmail.com')
        self.password = User.objects.make_random_password()
        self.scraper = User.objects.create_user(username="Scraper", password=self.password)
        self.num_of_saved_users = 2
        self.claim_1 = Claim(user_id=self.user.id,
                             claim='claim1',
                             category='category1',
                             tags="tag1, tag2",
                             authenticity_grade=0,
                             image_src='image1')
        self.claim_2 = Claim(user_id=self.scraper.id,
                             claim='claim2',
                             category='category2',
                             tags="tag3, tag4",
                             authenticity_grade=0,
                             image_src='image2')
        self.claim_1.save()
        self.claim_2.save()
        self.num_of_saved_claims = 2
        self.comment_1 = Comment(claim_id=self.claim_1.id,
                                 user_id=self.claim_1.user_id,
                                 title='title1',
                                 description='description1',
                                 url='url1',
                                 verdict_date=datetime.date.today() - datetime.timedelta(days=random.randint(0, 10)),
                                 label='True')
        self.comment_1.save()
        self.num_of_saved_comments = 1

        self.new_claim_with_comment_details = {'claim': 'claim3',
                                               'title': 'title3',
                                               'description': 'description3',
                                               'url': 'url3',
                                               'add_comment': 'true',
                                               'verdict_date': datetime.datetime.strptime(str(datetime.date.today() - datetime.timedelta(days=random.randint(0, 10))), '%Y-%m-%d').strftime('%d/%m/%Y'),
                                               'tags': 'tag4 tag5',
                                               'category': 'category3',
                                               'label': 'False',
                                               'image_src': 'image3'}

        self.new_claim_details = {'claim': 'claim4',
                                  'add_comment': 'false',
                                  'category': 'category4',
                                  'image_src': 'image4'}

        self.new_comment_details = {'title': 'commentTitle',
                                    'description': 'commentDescription',
                                    'url': 'commentUrl',
                                    'verdict_date': datetime.datetime.strptime(str(datetime.date.today() - datetime.timedelta(days=random.randint(0, 10))), '%Y-%m-%d').strftime('%d/%m/%Y'),
                                    'label': 'True'}

        self.update_claim_details = {'claim': 'claim3',
                                     'category': 'newCategory3',
                                     'tags': 'newTag4 newTag5',
                                     'image_src': 'image_src'}

        self.update_comment_details = {'comment_title': 'newCommentTitle',
                                       'comment_description': 'commentDescription',
                                       'comment_reference': 'newCommentUrl',
                                       'comment_tags': 'newCommentTag1 newCommentTag2',
                                       'comment_verdict_date': self.new_comment_details['verdict_date'],
                                       'comment_label': 'False'}

        self.post_request = HttpRequest()
        self.post_request.method = 'POST'

    def tearDown(self):
        pass

    def test_flow(self):
        len_claims = len(Claim.objects.all())
        len_comments = len(Comment.objects.all())
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.new_claim_with_comment_details)
        self.post_request.POST = query_dict
        self.post_request.user = self.user
        self.assertTrue(add_claim(self.post_request).status_code == 200)
        self.assertTrue(len(Claim.objects.all()) == len_claims + 1)
        self.assertTrue(len(Comment.objects.all()) == len_comments + 1)
        new_claim = Claim.objects.filter(id=self.num_of_saved_claims + 1).first()
        new_comment = Comment.objects.filter(id=self.num_of_saved_comments + 1).first()
        self.assertTrue(new_claim.claim == self.new_claim_with_comment_details['claim'])
        self.assertTrue(new_claim.category == self.new_claim_with_comment_details['category'])
        self.assertTrue(new_claim.tags == ', '.join(self.new_claim_with_comment_details['tags'].split()))
        self.assertTrue(new_claim.image_src == self.new_claim_with_comment_details['image_src'])
        self.assertTrue(new_claim.authenticity_grade == 0)
        self.num_of_saved_claims += 1

        self.assertTrue(new_comment.claim == new_claim)
        self.assertTrue(new_comment.title == self.new_claim_with_comment_details['title'])
        self.assertTrue(new_comment.description == self.new_claim_with_comment_details['description'])
        self.assertTrue(new_comment.url == self.new_claim_with_comment_details['url'])
        self.assertTrue(new_comment.tags == ', '.join(self.new_claim_with_comment_details['tags'].split()))
        self.assertTrue(new_comment.verdict_date == datetime.datetime.strptime(self.new_claim_with_comment_details['verdict_date'], '%d/%m/%Y').date())
        self.assertTrue(new_comment.label == self.new_claim_with_comment_details['label'])
        self.assertTrue(new_comment.system_label == 'False')
        self.assertTrue(new_comment.up_votes.count() == 0)
        self.assertTrue(new_comment.down_votes.count() == 0)
        self.num_of_saved_comments += 1

        self.update_claim_details['claim_id'] = str(self.num_of_saved_claims)
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.update_claim_details)
        self.post_request.POST = query_dict
        self.assertTrue(edit_claim(self.post_request).status_code == 200)
        new_claim_after_edit = Claim.objects.filter(id=self.num_of_saved_claims).first()
        self.assertTrue(new_claim_after_edit.claim == self.update_claim_details['claim'])
        self.assertTrue(new_claim_after_edit.category == self.update_claim_details['category'])
        self.assertTrue(new_claim_after_edit.tags == ', '.join(self.update_claim_details['tags'].split()))
        self.assertTrue(new_claim_after_edit.image_src == self.update_claim_details['image_src'])
        self.assertTrue(new_claim_after_edit.authenticity_grade == 0)

        self.update_claim_details_copy = self.update_claim_details.copy()
        del self.update_claim_details['claim_id']
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.update_claim_details)
        self.post_request.POST = query_dict
        self.assertRaises(Exception, edit_claim, self.post_request)

        self.update_claim_details = self.update_claim_details_copy.copy()
        del self.update_claim_details['claim']
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.update_claim_details)
        self.post_request.POST = query_dict
        self.assertRaises(Exception, edit_claim, self.post_request)

        self.update_claim_details = self.update_claim_details_copy.copy()
        del self.update_claim_details['category']
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.update_claim_details)
        self.post_request.POST = query_dict
        self.assertRaises(Exception, edit_claim, self.post_request)

        self.update_claim_details = self.update_claim_details_copy.copy()
        del self.update_claim_details['image_src']
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.update_claim_details)
        self.post_request.POST = query_dict
        self.assertRaises(Exception, edit_claim, self.post_request)

        self.update_claim_details = self.update_claim_details_copy.copy()
        del self.update_claim_details['tags']
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.update_claim_details)
        self.post_request.POST = query_dict
        self.assertTrue(edit_claim(self.post_request).status_code == 200)

        import time
        time.sleep(60 * 5)  # sleep for 5 minutes
        self.update_claim_details = self.update_claim_details_copy.copy()
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.update_claim_details)
        self.post_request.POST = query_dict
        self.assertRaises(Exception, edit_claim, self.post_request)

        len_claims = len(Claim.objects.all())
        len_comments = len(Comment.objects.all())
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.new_claim_details)
        self.post_request.POST = query_dict
        self.assertTrue(add_claim(self.post_request).status_code == 200)
        self.assertTrue(len(Claim.objects.all()) == len_claims + 1)
        self.assertTrue(len(Comment.objects.all()) == len_comments)
        new_claim = Claim.objects.filter(id=self.num_of_saved_claims + 1).first()
        self.assertTrue(len(Comment.objects.filter(id=self.num_of_saved_comments + 1)) == 0)
        self.assertTrue(new_claim.claim == self.new_claim_details['claim'])
        self.assertTrue(new_claim.category == self.new_claim_details['category'])
        self.assertTrue(new_claim.tags == ', '.join(''.split()))
        self.assertTrue(new_claim.image_src == self.new_claim_details['image_src'])
        self.assertTrue(new_claim.authenticity_grade == 0)
        self.num_of_saved_claims += 1

        self.new_comment_details['claim_id'] = str(self.num_of_saved_claims)
        len_comments = len(Comment.objects.all())
        self.post_request.POST = self.new_comment_details
        self.assertTrue(add_comment(self.post_request).status_code == 200)
        self.assertTrue(len(Comment.objects.all()) == len_comments + 1)
        new_comment = Comment.objects.filter(id=self.num_of_saved_comments + 1).first()
        self.assertTrue(new_comment.title == self.new_comment_details['title'])
        self.assertTrue(new_comment.description == self.new_comment_details['description'])
        self.assertTrue(new_comment.url == self.new_comment_details['url'])
        self.assertTrue(new_comment.verdict_date == datetime.datetime.strptime(self.new_comment_details['verdict_date'], '%d/%m/%Y').date())
        self.assertTrue(new_comment.tags == ', '.join(''.split()))
        self.assertTrue(new_comment.label == self.new_comment_details['label'])
        self.assertTrue(new_comment.system_label == self.new_comment_details['label'])
        self.assertTrue(new_comment.up_votes.count() == 0)
        self.assertTrue(new_comment.down_votes.count() == 0)
        self.num_of_saved_comments += 1

        self.update_comment_details['comment_id'] = str(self.num_of_saved_comments)
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.update_comment_details)
        self.post_request.POST = query_dict
        self.assertTrue(edit_comment(self.post_request).status_code == 200)
        new_comment_after_edit = Comment.objects.filter(id=self.num_of_saved_comments).first()
        self.assertTrue(new_comment_after_edit.title == self.update_comment_details['comment_title'])
        self.assertTrue(new_comment_after_edit.description == self.update_comment_details['comment_description'])
        self.assertTrue(new_comment_after_edit.url == self.update_comment_details['comment_reference'])
        self.assertTrue(new_comment_after_edit.verdict_date == datetime.datetime.strptime(self.update_comment_details['comment_verdict_date'], '%d/%m/%Y').date())
        self.assertTrue(new_comment_after_edit.tags == ', '.join(self.update_comment_details['comment_tags'].split()))
        self.assertTrue(new_comment_after_edit.system_label == self.update_comment_details['comment_label'])
        self.assertTrue(new_comment_after_edit.up_votes.count() == 0)
        self.assertTrue(new_comment_after_edit.down_votes.count() == 0)

        self.update_comment_details_copy = self.update_comment_details.copy()
        del self.update_comment_details['comment_id']
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.update_comment_details)
        self.post_request.POST = query_dict
        self.assertRaises(Exception, edit_comment, self.post_request)

        self.update_comment_details = self.update_comment_details_copy.copy()
        del self.update_comment_details['comment_title']
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.update_comment_details)
        self.post_request.POST = query_dict
        self.assertRaises(Exception, edit_comment, self.post_request)

        self.update_comment_details = self.update_comment_details_copy.copy()
        del self.update_comment_details['comment_description']
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.update_comment_details)
        self.post_request.POST = query_dict
        self.assertRaises(Exception, edit_comment, self.post_request)

        self.update_comment_details = self.update_comment_details_copy.copy()
        del self.update_comment_details['comment_reference']
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.update_comment_details)
        self.post_request.POST = query_dict
        self.assertRaises(Exception, edit_comment, self.post_request)

        self.update_comment_details = self.update_comment_details_copy.copy()
        del self.update_comment_details['comment_tags']
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.update_comment_details)
        self.post_request.POST = query_dict
        self.assertTrue(edit_comment(self.post_request).status_code == 200)

        self.update_comment_details = self.update_comment_details_copy.copy()
        del self.update_comment_details['comment_verdict_date']
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.update_comment_details)
        self.post_request.POST = query_dict
        self.assertRaises(Exception, edit_comment, self.post_request)

        self.update_comment_details = self.update_comment_details_copy.copy()
        del self.update_comment_details['comment_label']
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.update_comment_details)
        self.post_request.POST = query_dict
        self.assertRaises(Exception, edit_comment, self.post_request)

        time.sleep(60 * 5)  # sleep for 5 minutes
        self.update_comment_details = self.update_comment_details_copy.copy()
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.update_comment_details)
        self.post_request.POST = query_dict
        self.assertRaises(Exception, edit_comment, self.post_request)

        len_comments = len(Comment.objects.all())
        self.post_request.POST = {'comment_id': self.num_of_saved_comments}
        self.assertTrue(delete_comment(self.post_request).status_code == 200)
        self.assertTrue(len(Comment.objects.all()) == len_comments - 1)
        self.num_of_saved_comments -= 1

        len_claims = len(Claim.objects.all())
        self.post_request.POST = {'claim_id': self.num_of_saved_claims}
        self.assertTrue(delete_claim(self.post_request).status_code == 200)
        self.assertTrue(len(Claim.objects.all()) == len_claims - 1)
        self.num_of_saved_claims -= 1

        query_dict = QueryDict('', mutable=True)
        query_dict.update({'comment_id': self.num_of_saved_comments})
        self.post_request.POST = query_dict
        self.assertTrue(up_vote(self.post_request).status_code == 200)
        self.assertTrue(Comment.objects.filter(id=self.num_of_saved_comments).first().up_votes.count() == 1)

        self.post_request.user = self.scraper
        self.assertTrue(down_vote(self.post_request).status_code == 200)
        self.assertTrue(Comment.objects.filter(id=self.num_of_saved_comments).first().down_votes.count() == 1)

        query_dict = QueryDict('', mutable=True)
        query_dict.update({'comment_id': self.comment_1.id})
        self.post_request.POST = query_dict
        self.assertTrue(up_vote(self.post_request).status_code == 200)

        self.post_request.user = self.user
        self.assertTrue(up_vote(self.post_request).status_code == 200)

        self.assertTrue(Comment.objects.filter(id=self.comment_1.id).first().up_votes.count() == 2)
        self.assertTrue(Comment.objects.filter(id=self.comment_1.id).first().down_votes.count() == 0)