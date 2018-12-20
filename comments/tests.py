from django.test import TestCase
from claims.models import Claim
from comments.models import Comment
from comments.views import get_all_comments_for_user_id, get_all_comments_for_claim_id, reset_comments, \
    get_category_for_claim, add_comment, export_to_csv
from users.models import User


class CommentTests(TestCase):
    def setUp(self):
        self.user_1 = User(username="User1", email='user1@gmail.com', state='Regular', reputation=-1)
        self.user_2 = User(username="User2", email='user2@gmail.com', state='Regular', reputation=-1)
        self.user_1.save()
        self.user_2.save()

        self.claim_1 = Claim.objects.create(title='claim1', category='category1', authentic_grade=-1)
        self.claim_1.save()
        self.claim_2 = Claim.objects.create(title='claim2', category='category2', authentic_grade=-1)
        self.claim_2.save()

        self.comment_1 = Comment(claim_id=self.claim_1.id, user_id=self.user_1.id, title=self.claim_1.title,
                            description='description1', url='url1', verdict_date='verdict_date1',
                            tags='tags1', label='label1', pos_votes=0, neg_votes=0)
        self.comment_2 = Comment(claim_id=self.claim_2.id, user_id=self.user_1.id, title=self.claim_2.title,
                            description='description2', url='url2', verdict_date='verdict_date2',
                            tags='tags2', label='label2', pos_votes=0, neg_votes=0)

        self.comment_3 = Comment(claim_id=self.claim_1.id, user_id=self.user_2.id, title=self.claim_1.title,
                            description='description1', url='url1', verdict_date='verdict_date1',
                            tags='tags1', label='label1', pos_votes=0, neg_votes=0)
        self.comment_1.save()
        self.comment_2.save()
        self.comment_3.save()

    def tearDown(self):
        pass

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

    def test_reset_comments(self):
        reset_comments()
        self.assertTrue(len(Comment.objects.all()) == 0)

    def test_get_category_for_claim(self):
        self.assertTrue(get_category_for_claim(self.claim_1.id) == self.claim_1.category)
        self.assertTrue(get_category_for_claim(self.claim_2.id) == self.claim_2.category)

    def test_add_comment(self):
        len_comments = len(Comment.objects.all())
        add_comment(self.claim_1.id, self.user_2.id, self.claim_2.title,
                    'description3', 'url3', 'verdict_date3', 'tags3', 'label3')
        self.assertTrue(len(Comment.objects.all()) == len_comments + 1)
        new_comment = Comment.objects.all().order_by('-id')[0]
        self.assertTrue(new_comment.id == 4)
        self.assertTrue(new_comment.title == self.claim_2.title)
        self.assertTrue(new_comment.user_id == self.user_2.id)

    def test_export_to_csv(self):
        res = export_to_csv()
        self.assertTrue(res.status_code == 200)
        print(res.content)
        self.assertTrue(res.content == b'Title,Description,Url,Category,Verdict_Date,Tags,Label\r\nclaim1,description1,url1,category1,verdict_date1,tags1,label1\r\nclaim2,description2,url2,category2,verdict_date2,tags2,label2\r\nclaim1,description1,url1,category1,verdict_date1,tags1,label1\r\n')