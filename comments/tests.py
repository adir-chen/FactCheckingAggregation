from django.test import TestCase
from claims.models import Claim
from comments.models import Comment
from comments.views import add_comment, build_comment, check_if_comment_is_valid, \
    get_all_comments_for_user_id, get_all_comments_for_claim_id, export_to_csv
from users.models import User
import datetime


class CommentTests(TestCase):
    def setUp(self):
        self.user_1 = User(username="User1", email='user1@gmail.com')
        self.user_2 = User(username="User2", email='user2@gmail.com')
        self.user_1.save()
        self.user_2.save()

        self.claim_1 = Claim(claim='Sniffing rosemary increases human memory by up to 75 percent',
                             category='Science',
                             tags="sniffing human memory",
                             authenticity_grade=0)
        self.claim_2 = Claim(claim='A photograph shows the largest U.S. flag ever made, displayed in front of Hoover Dam',
                             category='Fauxtography',
                             tags="photograph U.S. flag",
                             authenticity_grade=0)
        self.claim_1.save()
        self.claim_2.save()

        self.comment_1 = Comment(claim_id=self.claim_1.id,
                                 user_id=self.user_1.id,
                                 title=self.claim_1.claim,
                                 description='description1',
                                 url='url1',
                                 verdict_date='11/2/2019',
                                 label='label1',
                                 pos_votes=0,
                                 neg_votes=0)
        self.comment_2 = Comment(claim_id=self.claim_2.id,
                                 user_id=self.user_1.id,
                                 title=self.claim_2.claim,
                                 description='description2',
                                 url='url2',
                                 verdict_date='11/1/2018',
                                 label='label2',
                                 pos_votes=0,
                                 neg_votes=0)
        self.comment_3 = Comment(claim_id=self.claim_1.id,
                                 user_id=self.user_2.id,
                                 title=self.claim_1.claim,
                                 description='description3',
                                 url='url3',
                                 verdict_date='11/1/2019',
                                 label='label3',
                                 pos_votes=0,
                                 neg_votes=0)
        self.comment_4 = Comment(claim_id=self.claim_1.id,
                                 user_id=self.user_2.id,
                                 title=self.claim_1.claim,
                                 description='description3',
                                 url='url3',
                                 verdict_date='10/2/2019',
                                 label='label3',
                                 pos_votes=0,
                                 neg_votes=0)
        self.comment_1.save()
        self.comment_2.save()
        self.comment_3.save()

        self.dict = {'user_id': self.user_1.id,
                     'claim_id': self.claim_1.id,
                     'title': 'Did Kurt Russell Say Democrats Should Be Declared ‘Enemies of the State’?',
                     'description': 'A notorious producer of junk news recycled an old quotation attributed to the veteran Hollywood actor.',
                     'url': "https://www.snopes.com/fact-check/kurt-russell-democrats/",
                     'verdict_date': '11/02/2019',
                     'label': 'False'}

    def tearDown(self):
        pass

    def test_build_comment_by_existing_user(self):
        len_comments = len(Comment.objects.all())
        build_comment(self.comment_4.claim_id,
                      self.comment_4.user_id,
                      self.comment_4.title,
                      self.comment_4.description,
                      self.comment_4.url,
                      self.comment_4.verdict_date,
                      self.comment_4.label)
        self.assertTrue(len(Comment.objects.all()) == len_comments + 1)
        new_comment = Comment.objects.all().order_by('-id')[0]
        self.assertTrue(new_comment.id == 4)
        self.assertTrue(new_comment.claim_id == self.comment_4.claim_id)
        self.assertTrue(new_comment.user_id == self.comment_4.user_id)
        self.assertTrue(new_comment.title == self.comment_4.title)

    def test_build_comment_by_added_user(self):
        len_comments = len(Comment.objects.all())
        user_3 = User(username="User3", email='user3@gmail.com')
        user_3.save()
        self.comment_4.user_id = user_3.id
        build_comment(self.comment_4.claim_id,
                      self.comment_4.user_id,
                      self.comment_4.title,
                      self.comment_4.description,
                      self.comment_4.url,
                      self.comment_4.verdict_date,
                      self.comment_4.label)
        self.assertTrue(len(Comment.objects.all()) == len_comments + 1)
        new_comment = Comment.objects.all().order_by('-id')[0]
        self.assertTrue(new_comment.id == 4)
        self.assertTrue(new_comment.claim_id == self.comment_4.claim_id)
        self.assertTrue(new_comment.user_id == self.comment_4.user_id)
        self.assertTrue(new_comment.title == self.comment_4.title)

    def test_check_if_comment_is_valid(self):
        self.assertTrue(check_if_comment_is_valid(self.dict))

    def test_check_if_comment_is_valid_missing_user_id(self):
        del self.dict['user_id']
        self.assertFalse(check_if_comment_is_valid(self.dict)[0])

    def test_check_if_comment_is_valid_missing_claim_id(self):
        del self.dict['claim_id']
        self.assertFalse(check_if_comment_is_valid(self.dict)[0])

    def test_check_if_comment_is_valid_missing_title(self):
        del self.dict['title']
        self.assertFalse(check_if_comment_is_valid(self.dict)[0])

    def test_check_if_comment_is_valid_missing_description(self):
        del self.dict['description']
        self.assertFalse(check_if_comment_is_valid(self.dict)[0])

    def test_check_if_comment_is_valid_missing_url(self):
        del self.dict['url']
        self.assertFalse(check_if_comment_is_valid(self.dict)[0])

    def test_check_if_comment_is_valid_missing_verdict_date(self):
        del self.dict['verdict_date']
        self.assertFalse(check_if_comment_is_valid(self.dict)[0])

    def test_check_if_comment_is_valid_missing_label(self):
        del self.dict['label']
        self.assertFalse(check_if_comment_is_valid(self.dict)[0])

    def test_check_if_comment_is_valid_invalid_claim_id(self):
        self.dict['claim_id'] = 4
        self.assertFalse(check_if_comment_is_valid(self.dict)[0])

    def test_check_if_comment_is_valid_invalid_user_id(self):
        self.dict['user_id'] = 3
        self.assertFalse(check_if_comment_is_valid(self.dict)[0])

    def test_check_if_comment_is_valid_invalid_verdict_date(self):
        self.dict['verdict_date'] = datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=7),'%d/%m/%Y')
        self.assertFalse(check_if_comment_is_valid(self.dict)[0])

    def test_get_all_comments_for_user_id(self):
        result = get_all_comments_for_user_id(self.user_1.id)
        self.assertTrue(len(result) == 2)
        self.assertTrue(result[0].claim_id == self.comment_1.claim_id)
        self.assertTrue(result[0].user_id == self.comment_1.user_id)
        self.assertTrue(result[0].title == self.comment_1.title)
        self.assertTrue(result[1].claim_id == self.comment_2.id)
        self.assertTrue(result[1].user_id == self.comment_2.user_id)
        self.assertTrue(result[1].title == self.comment_2.title)

        result = get_all_comments_for_user_id(self.user_2.id)
        self.assertTrue(len(result) == 1)
        self.assertTrue(result[0].claim_id == self.comment_3.claim_id)
        self.assertTrue(result[0].user_id == self.comment_3.user_id)
        self.assertTrue(result[0].title == self.comment_3.title)

    def test_get_all_comments_for_added_user(self):
        user_3 = User(username="User3", email='user3@gmail.com')
        user_3.save()
        comment_4 = Comment(claim_id=self.claim_1.id,
                            user_id=user_3.id,
                            title=self.claim_1.claim,
                            description='description4',
                            url='url1',
                            verdict_date='verdict_date1',
                            label='label1',
                            pos_votes=0,
                            neg_votes=0)
        comment_4.save()
        result = get_all_comments_for_user_id(user_3.id)
        self.assertTrue(len(result) == 1)
        self.assertTrue(result[0].claim_id == comment_4.claim_id)
        self.assertTrue(result[0].user_id == comment_4.user_id)
        self.assertTrue(result[0].title == comment_4.title)

    def test_get_all_comments_for_invalid_user_id(self):
        result = get_all_comments_for_user_id(3)
        self.assertTrue(result is None)

    def test_get_all_comments_for_claim_id(self):
        result_comment_1 = get_all_comments_for_claim_id(self.claim_1.id)
        self.assertTrue(len(result_comment_1) == 2)
        self.assertTrue(result_comment_1[0].claim_id == self.claim_1.id)
        self.assertTrue(result_comment_1[0].user_id == self.comment_1.user_id)
        self.assertTrue(result_comment_1[0].title == self.comment_1.title)
        self.assertTrue(result_comment_1[1].claim_id == self.claim_1.id)
        self.assertTrue(result_comment_1[1].user_id == self.comment_3.user_id)
        self.assertTrue(result_comment_1[1].title == self.comment_3.title)

        result_comment_2 = get_all_comments_for_claim_id(self.claim_2.id)
        self.assertTrue(len(result_comment_2) == 1)
        self.assertTrue(result_comment_2[0].claim_id == self.claim_2.id)
        self.assertTrue(result_comment_2[0].user_id == self.comment_2.user_id)
        self.assertTrue(result_comment_2[0].title == self.comment_2.title)

    def test_get_all_comments_for_claim_id_added_user(self):
        user_3 = User(username="User3", email='user3@gmail.com')
        user_3.save()
        comment_4 = Comment(claim_id=self.claim_1.id,
                            user_id=user_3.id,
                            title=self.claim_1.claim,
                            description='description4',
                            url='url1',
                            verdict_date='verdict_date1',
                            label='label1',
                            pos_votes=0,
                            neg_votes=0)
        comment_4.save()
        result_comment_1 = get_all_comments_for_claim_id(self.claim_1.id)
        self.assertTrue(len(result_comment_1) == 3)
        self.assertTrue(result_comment_1[0].claim_id == self.claim_1.id)
        self.assertTrue(result_comment_1[0].user_id == self.comment_1.user_id)
        self.assertTrue(result_comment_1[0].title == self.comment_1.title)
        self.assertTrue(result_comment_1[1].claim_id == self.claim_1.id)
        self.assertTrue(result_comment_1[1].user_id == self.comment_3.user_id)
        self.assertTrue(result_comment_1[1].title == self.comment_3.title)
        self.assertTrue(result_comment_1[2].claim_id == self.claim_1.id)
        self.assertTrue(result_comment_1[2].user_id == comment_4.user_id)
        self.assertTrue(result_comment_1[2].title == comment_4.title)

    def test_get_all_comments_for_invalid_claim_id(self):
        result = get_all_comments_for_claim_id(3) # no claim with the given id
        self.assertTrue(result is None)

    def test_export_to_csv(self):
        res = export_to_csv()
        self.assertTrue(res.status_code == 200)
        self.assertTrue(res.content == b'Title,Description,Url,Category,Verdict_Date,Tags,Label\r\nSniffing rosemary increases human memory by up to 75 percent,description1,url1,Science,11/2/2019,sniffing human memory,label1\r\n"A photograph shows the largest U.S. flag ever made, displayed in front of Hoover Dam",description2,url2,Fauxtography,11/1/2018,photograph U.S. flag,label2\r\nSniffing rosemary increases human memory by up to 75 percent,description3,url3,Science,11/1/2019,sniffing human memory,label3\r\n')

    def test_export_to_csv_empty(self):
        Comment.objects.all().delete()
        res = export_to_csv()
        self.assertTrue(res.status_code == 200)
        print(res.content == b'')
