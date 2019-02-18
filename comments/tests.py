from django.http import HttpRequest, Http404
from django.test import TestCase
from claims.models import Claim
from comments.models import Comment
from comments.views import add_comment, build_comment, check_if_comment_is_valid, \
    get_system_label_to_comment, get_all_comments_for_user_id, get_all_comments_for_claim_id, \
    export_to_csv, up_vote, down_vote, edit_comment, check_comment_new_fields, delete_comment, \
    update_authenticity_grade
from users.models import User
import datetime
import random


class CommentTests(TestCase):
    def setUp(self):
        self.user_1 = User(username="User1", email='user1@gmail.com')
        self.user_2 = User(username="User2", email='user2@gmail.com')
        self.user_1.save()
        self.user_2.save()
        self.num_of_saved_users = 2
        self.claim_1 = Claim(user_id=self.user_1.id,
                             claim='Sniffing rosemary increases human memory by up to 75 percent',
                             category='Science',
                             tags="sniffing human memory",
                             authenticity_grade=0)
        self.claim_2 = Claim(user_id=self.user_2.id,
                             claim='A photograph shows the largest U.S. flag ever made, displayed in front of Hoover Dam',
                             category='Fauxtography',
                             tags="photograph U.S. flag",
                             authenticity_grade=0)
        self.claim_1.save()
        self.claim_2.save()
        self.num_of_saved_claims = 2
        self.comment_1 = Comment(claim_id=self.claim_1.id,
                                 user_id=self.user_1.id,
                                 title=self.claim_1.claim,
                                 description='description1',
                                 url='url1',
                                 verdict_date=datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=7), '%d/%m/%Y'),
                                 label='label1')
        self.comment_2 = Comment(claim_id=self.claim_2.id,
                                 user_id=self.user_1.id,
                                 title=self.claim_2.claim,
                                 description='description2',
                                 url='url2',
                                 verdict_date=datetime.datetime.strftime(datetime.datetime.now() - datetime.timedelta(days=7), '%d/%m/%Y'),
                                 label='label2')
        self.comment_3 = Comment(claim_id=self.claim_1.id,
                                 user_id=self.user_2.id,
                                 title=self.claim_1.claim,
                                 description='description3',
                                 url='url3',
                                 verdict_date=datetime.datetime.strftime(datetime.datetime.now() - datetime.timedelta(days=10), '%d/%m/%Y'),
                                 label='label3')
        self.comment_4 = Comment(claim_id=self.claim_1.id,
                                 user_id=self.user_2.id,
                                 title=self.claim_1.claim,
                                 description='description3',
                                 url='url3',
                                 verdict_date=datetime.datetime.strftime(datetime.datetime.now(), '%d/%m/%Y'),
                                 label='label3')
        self.comment_1.save()
        self.comment_2.save()
        self.comment_3.save()
        self.num_of_saved_comments = 3
        self.dict = {'user_id': self.user_1.id,
                     'claim_id': self.claim_1.id,
                     'title': 'Did Kurt Russell Say Democrats Should Be Declared ‘Enemies of the State’?',
                     'description': 'A notorious producer of junk news recycled an old quotation attributed to the veteran Hollywood actor.',
                     'url': "https://www.snopes.com/fact-check/kurt-russell-democrats/",
                     'verdict_date': '11/02/2019',
                     'label': 'False'}

        self.post_request = HttpRequest()
        self.post_request.method = 'POST'
        self.data = {'claim_id': self.comment_4.claim_id,
                     'user_id': self.comment_4.user_id,
                     'title': self.comment_4.title,
                     'description': self.comment_4.description,
                     'url': self.comment_4.url,
                     'label': self.comment_4.label}

        self.data_new_field = {'comment_title': self.comment_1.title,
                               'comment_description': self.comment_2.description,
                               'comment_reference': self.comment_2.url,
                               'comment_label': True}

    def tearDown(self):
        pass

    def test_add_comment(self):
        len_comments = len(Comment.objects.filter(claim_id=self.claim_1.id))
        self.post_request.POST = self.data
        self.assertTrue(add_comment(self.post_request).status_code == 200)
        self.assertTrue(len(Comment.objects.filter(claim_id=self.claim_1.id)) == len_comments + 1)
        new_comment = Comment.objects.all().order_by('-id')[0]
        self.assertTrue(new_comment.id == self.num_of_saved_comments + 1)
        self.assertTrue(new_comment.claim_id == self.comment_4.claim_id)
        self.assertTrue(new_comment.user_id == self.comment_4.user_id)
        self.assertTrue(new_comment.title == self.comment_4.title)
        self.assertTrue(new_comment.description == self.comment_4.description)
        self.assertTrue(new_comment.url == self.comment_4.url)
        self.assertTrue(new_comment.verdict_date == self.comment_4.verdict_date)
        self.assertTrue(new_comment.label == self.comment_4.label)

    def test_add_comment_missing_claim_id(self):
        del self.data['claim_id']
        self.post_request.POST = self.data
        self.assertRaises(Exception, add_comment, self.post_request)

    def test_add_comment_missing_user_id(self):
        del self.data['user_id']
        self.post_request.POST = self.data
        self.assertRaises(Exception, add_comment, self.post_request)

    def test_add_comment_missing_title(self):
        del self.data['title']
        self.post_request.POST = self.data
        self.assertRaises(Exception, add_comment, self.post_request)

    def test_add_comment_missing_description(self):
        del self.data['description']
        self.post_request.POST = self.data
        self.assertRaises(Exception, add_comment, self.post_request)

    def test_add_comment_missing_url(self):
        del self.data['url']
        self.post_request.POST = self.data
        self.assertRaises(Exception, add_comment, self.post_request)

    def test_add_comment_missing_label(self):
        del self.data['label']
        self.post_request.POST = self.data
        self.assertRaises(Exception, add_comment, self.post_request)

    def test_add_comment_missing_args(self):
        for i in range(10):
            dict_copy = self.data
            args_to_remove = []
            for j in range(random.randint(0, len(self.data.keys()) - 1)):
                args_to_remove.append(list(self.data.keys())[j])
            for j in range(len(args_to_remove)):
                del self.data[args_to_remove[j]]
            len_comments = len(Comment.objects.filter(claim_id=self.claim_1.id))
            self.post_request.POST = self.data
            self.assertTrue(len(Comment.objects.filter(claim_id=self.claim_1.id)) == len_comments)
            self.assertRaises(Exception, add_comment, self.post_request)
            self.dict = dict_copy

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
        self.assertTrue(new_comment.description == self.comment_4.description)
        self.assertTrue(new_comment.url == self.comment_4.url)
        self.assertTrue(new_comment.verdict_date == self.comment_4.verdict_date)
        self.assertTrue(new_comment.label == self.comment_4.label)

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

    def test_check_if_comment_is_valid_missing_label(self):
        del self.dict['label']
        self.assertFalse(check_if_comment_is_valid(self.dict)[0])

    def test_check_if_comment_is_valid_invalid_claim_id(self):
        self.dict['claim_id'] = str(self.num_of_saved_claims + 1)
        self.assertFalse(check_if_comment_is_valid(self.dict)[0])

    def test_check_if_comment_is_valid_invalid_user_id(self):
        self.dict['user_id'] = str(self.num_of_saved_users + 1)
        self.assertFalse(check_if_comment_is_valid(self.dict)[0])

    def test_get_system_label_to_comment(self):
        self.assertTrue(get_system_label_to_comment("Mostly True"))
        self.assertTrue(get_system_label_to_comment("True"))
        self.assertTrue(get_system_label_to_comment("TRUE"))
        self.assertTrue(get_system_label_to_comment("Accurate"))
        self.assertTrue(get_system_label_to_comment("ACCURATE"))

        self.assertFalse(get_system_label_to_comment("Mostly False"))
        self.assertFalse(get_system_label_to_comment("False"))
        self.assertFalse(get_system_label_to_comment("FALSE"))
        self.assertFalse(get_system_label_to_comment("Inaccurate"))
        self.assertFalse(get_system_label_to_comment("INACCURATE"))

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
                            label='label1')
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
                            label='label1')
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
        self.assertTrue(res.content == b'Title,Description,Url,Category,Verdict_Date,Tags,Label\r\nSniffing rosemary increases human memory by up to 75 percent,description1,url1,Science,25/02/2019,sniffing human memory,label1\r\n"A photograph shows the largest U.S. flag ever made, displayed in front of Hoover Dam",description2,url2,Fauxtography,11/02/2019,photograph U.S. flag,label2\r\nSniffing rosemary increases human memory by up to 75 percent,description3,url3,Science,08/02/2019,sniffing human memory,label3\r\n')

    def test_export_to_csv_empty(self):
        Comment.objects.all().delete()
        res = export_to_csv()
        self.assertTrue(res.status_code == 200)
        print(res.content == b'Title,Description,Url,Category,Verdict_Date,Tags,Label\r\n')

    def test_up_vote(self):
        data = {'user_id': self.comment_1.user_id, 'comment_id': self.comment_2.id}
        self.post_request.POST = data
        response = up_vote(self.post_request)
        self.assertTrue(self.comment_2.up_votes.count() == 1)
        self.assertTrue(self.comment_2.down_votes.count() == 0)
        self.assertTrue(response.status_code == 200)

    def test_up_vote_twice(self):
        data = {'user_id': self.comment_1.user_id, 'comment_id': self.comment_2.id}
        self.post_request.POST = data
        up_vote(self.post_request)
        response = up_vote(self.post_request)
        self.assertTrue(self.comment_2.up_votes.count() == 0)
        self.assertTrue(self.comment_2.down_votes.count() == 0)
        self.assertTrue(response.status_code == 200)

    def test_up_vote_after_down_vote(self):
        data = {'user_id': self.comment_1.user_id, 'comment_id': self.comment_2.id}
        self.post_request.POST = data
        down_vote(self.post_request)
        response = up_vote(self.post_request)
        self.assertTrue(self.comment_2.up_votes.count() == 1)
        self.assertTrue(self.comment_2.down_votes.count() == 0)
        self.assertTrue(response.status_code == 200)

    def test_down_vote(self):
        data = {'user_id': self.comment_1.user_id, 'comment_id': self.comment_2.id}
        self.post_request.POST = data
        response = down_vote(self.post_request)
        self.assertTrue(self.comment_2.down_votes.count() == 1)
        self.assertTrue(self.comment_2.up_votes.count() == 0)
        self.assertTrue(response.status_code == 200)

    def test_down_vote_twice(self):
        data = {'user_id': self.comment_1.user_id, 'comment_id': self.comment_2.id}
        self.post_request.POST = data
        down_vote(self.post_request)
        response = down_vote(self.post_request)
        self.assertTrue(self.comment_2.down_votes.count() == 0)
        self.assertTrue(self.comment_2.down_votes.count() == 0)
        self.assertTrue(response.status_code == 200)

    def test_down_vote_after_up_vote(self):
        data = {'user_id': self.comment_1.user_id, 'comment_id': self.comment_2.id}
        self.post_request.POST = data
        up_vote(self.post_request)
        response = down_vote(self.post_request)
        self.assertTrue(self.comment_2.up_votes.count() == 0)
        self.assertTrue(self.comment_2.down_votes.count() == 1)
        self.assertTrue(response.status_code == 200)

    def test_edit_comment(self):
        self.data_new_field['comment_id'] = str(self.comment_1.id)
        self.data_new_field['user_id'] = str(self.comment_1.user_id)
        self.post_request.POST = self.data_new_field
        self.assertTrue(self.comment_1.title == self.data_new_field['comment_title'])
        self.assertFalse(self.comment_1.description == self.data_new_field['comment_description'])
        self.assertFalse(self.comment_1.url == self.data_new_field['comment_reference'])
        self.assertFalse(self.comment_1.system_label == self.data_new_field['comment_label'])
        self.assertTrue(edit_comment(self.post_request).status_code == 200)
        new_comment = Comment.objects.filter(id=self.comment_1.id)[0]
        self.assertTrue(new_comment.title == self.data_new_field['comment_title'])
        self.assertTrue(new_comment.description == self.data_new_field['comment_description'])
        self.assertTrue(new_comment.url == self.data_new_field['comment_reference'])
        self.assertTrue(new_comment.system_label == self.data_new_field['comment_label'])

    def test_edit_comment_by_user_not_his_comment(self):
        self.data_new_field['user_id'] = str(self.comment_3.user_id)
        self.data_new_field['comment_id'] = str(self.comment_1.id)
        self.post_request.POST = self.data_new_field
        self.assertTrue(edit_comment(self.post_request).status_code == 200)
        comment = Comment.objects.filter(id=self.comment_1.id)[0]
        self.assertTrue(comment.title == self.comment_1.title)
        self.assertTrue(comment.description == self.comment_1.description)
        self.assertTrue(comment.url == self.comment_1.url)
        self.assertTrue(comment.label == self.comment_1.label)

    def test_edit_comment_by_invalid_user_id(self):
        self.data_new_field['user_id'] = self.num_of_saved_users + random.randint(1, 10)
        self.data_new_field['comment_id'] = str(self.comment_1.id)
        self.post_request.POST = self.data_new_field
        self.assertRaises(Exception, edit_comment, self.post_request)
        comment = Comment.objects.filter(id=self.comment_1.id)[0]
        self.assertTrue(comment.title == self.comment_1.title)
        self.assertTrue(comment.description == self.comment_1.description)
        self.assertTrue(comment.url == self.comment_1.url)
        self.assertTrue(comment.label == self.comment_1.label)

    def test_edit_comment_by_invalid_comment_id(self):
        self.data_new_field['user_id'] = str(self.comment_1.user_id)
        self.data_new_field['comment_id'] = self.num_of_saved_comments + random.randint(1, 10)
        self.post_request.POST = self.data_new_field
        self.assertRaises(Exception, edit_comment, self.post_request)
        comment = Comment.objects.filter(id=self.comment_1.id)[0]
        self.assertTrue(comment.title == self.comment_1.title)
        self.assertTrue(comment.description == self.comment_1.description)
        self.assertTrue(comment.url == self.comment_1.url)
        self.assertTrue(comment.label == self.comment_1.label)

    def test_check_comment_new_fields(self):
        self.post_request.POST = self.data_new_field
        self.assertTrue(check_comment_new_fields(self.post_request)[0])

    def test_check_comment_new_fields_missing_title(self):
        del self.data_new_field['comment_title']
        self.post_request.POST = self.data_new_field
        self.assertFalse(check_comment_new_fields(self.post_request)[0])

    def test_check_comment_new_fields_missing_description(self):
        del self.data_new_field['comment_description']
        self.post_request.POST = self.data_new_field
        self.assertFalse(check_comment_new_fields(self.post_request)[0])

    def test_check_comment_new_fields_missing_reference(self):
        del self.data_new_field['comment_reference']
        self.post_request.POST = self.data_new_field
        self.assertFalse(check_comment_new_fields(self.post_request)[0])

    def test_check_comment_new_fields_missing_label(self):
        del self.data_new_field['comment_label']
        self.post_request.POST = self.data_new_field
        self.assertFalse(check_comment_new_fields(self.post_request)[0])

    def test_delete_comment_by_user(self):
        data = {'user_id': self.comment_1.user_id, 'comment_id': self.comment_1.id}
        self.post_request.POST = data
        len_comments = len(Comment.objects.all())
        response = delete_comment(self.post_request)
        self.assertTrue(len(Comment.objects.all()) == len_comments - 1)
        self.assertTrue(response.status_code == 200)

    def test_delete_comment_by_user_not_his_comment(self):
        data = {'user_id': self.comment_1.user_id, 'comment_id': self.comment_3.id}
        self.post_request.POST = data
        len_comments = len(Comment.objects.all())
        response = delete_comment(self.post_request)
        self.assertTrue(len(Comment.objects.all()) == len_comments)
        self.assertTrue(response.status_code == 200)

    def test_delete_comment_by_invalid_user(self):
        data = {'user_id': self.num_of_saved_users + random.randint(1, 10), 'comment_id': self.comment_3.id}
        self.post_request.POST = data
        len_comments = len(Comment.objects.all())
        self.assertRaises(Exception, delete_comment, self.post_request)
        self.assertTrue(len(Comment.objects.all()) == len_comments)

    def test_delete_comment_by_invalid_comment(self):
        data = {'user_id': self.comment_1.user_id, 'comment_id': self.num_of_saved_comments + random.randint(0, 10)}
        self.post_request.POST = data
        len_comments = len(Comment.objects.all())
        self.assertRaises(Exception, delete_comment, self.post_request)
        self.assertTrue(len(Comment.objects.all()) == len_comments)

    def test_update_authenticity_grade_true(self):
        Comment.objects.filter(id=self.comment_1.id).update(system_label=True)
        Comment.objects.filter(id=self.comment_3.id).update(system_label=True)
        update_authenticity_grade(self.claim_1.id)
        self.assertTrue(Claim.objects.filter(id=self.claim_1.id)[0].authenticity_grade == 100)

    def test_update_authenticity_grade_true_and_false(self):
        Comment.objects.filter(id=self.comment_1.id).update(system_label=True)
        Comment.objects.filter(id=self.comment_3.id).update(system_label=False)
        update_authenticity_grade(self.claim_1.id)
        self.assertTrue(Claim.objects.filter(id=self.claim_1.id)[0].authenticity_grade == 50)

    def test_update_authenticity_grade_true_and_false_with_down_vote(self):
        Comment.objects.filter(id=self.comment_1.id).update(system_label=True)
        Comment.objects.filter(id=self.comment_3.id).update(system_label=False)
        data = {'user_id': self.comment_3.user_id, 'comment_id': self.comment_3.id}
        self.post_request.POST = data
        down_vote(self.post_request)
        update_authenticity_grade(self.claim_1.id)
        self.assertTrue(Claim.objects.filter(id=self.claim_1.id)[0].authenticity_grade == 100)

    def test_update_authenticity_grade_true_and_false_with_up_vote(self):
        Comment.objects.filter(id=self.comment_1.id).update(system_label=True)
        Comment.objects.filter(id=self.comment_3.id).update(system_label=False)
        data = {'user_id': self.comment_3.user_id, 'comment_id': self.comment_3.id}
        self.post_request.POST = data
        up_vote(self.post_request)
        update_authenticity_grade(self.claim_1.id)
        self.assertTrue(Claim.objects.filter(id=self.claim_1.id)[0].authenticity_grade == 50)

    def test_update_authenticity_grade_true_with_up_vote_and_false(self):
        Comment.objects.filter(id=self.comment_1.id).update(system_label=True)
        Comment.objects.filter(id=self.comment_3.id).update(system_label=False)
        data = {'user_id': self.comment_1.user_id, 'comment_id': self.comment_1.id}
        self.post_request.POST = data
        up_vote(self.post_request)
        update_authenticity_grade(self.claim_1.id)
        self.assertTrue(Claim.objects.filter(id=self.claim_1.id)[0].authenticity_grade == 50)

    def test_update_authenticity_grade_true_with_down_vote_and_false(self):
        Comment.objects.filter(id=self.comment_1.id).update(system_label=True)
        Comment.objects.filter(id=self.comment_3.id).update(system_label=False)
        data = {'user_id': self.comment_1.user_id, 'comment_id': self.comment_1.id}
        self.post_request.POST = data
        down_vote(self.post_request)
        update_authenticity_grade(self.claim_1.id)
        self.assertTrue(Claim.objects.filter(id=self.claim_1.id)[0].authenticity_grade == 0)

    def test_update_authenticity_grade_true_with_down_vote_and_false_with_down_vote(self):
        Comment.objects.filter(id=self.comment_1.id).update(system_label=True)
        Comment.objects.filter(id=self.comment_3.id).update(system_label=False)
        data = {'user_id': self.comment_1.user_id, 'comment_id': self.comment_1.id}
        self.post_request.POST = data
        down_vote(self.post_request)
        data['comment_id'] = self.comment_3.id
        self.post_request.POST = data
        down_vote(self.post_request)
        update_authenticity_grade(self.claim_1.id)
        self.assertTrue(Claim.objects.filter(id=self.claim_1.id)[0].authenticity_grade == 0)