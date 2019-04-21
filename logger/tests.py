from django.contrib.auth.models import User
from django.utils import timezone
from django.http import HttpRequest, QueryDict
from django.core.exceptions import PermissionDenied
from django.test import TestCase
from django.utils.datastructures import MultiValueDict
from logger.models import Logger
from logger.views import view_log, save_log_message, check_duplicate_log_for_user, export_to_csv, \
     check_if_csv_fields_are_valid, check_if_actions_list_valid, create_df_for_logger
import random
import datetime


class LoggerTest(TestCase):
    def setUp(self):
        self.user_1 = User(username="User1", email='user1@gmail.com')
        self.user_1.save()
        random_days = random.randint(1, 10)
        self.log_1 = Logger(date=timezone.now() - timezone.timedelta(days=random_days),
                            user_id=self.user_1.id,
                            username=self.user_1.username,
                            action='Adding a new claim',
                            result=True)
        self.log_1.save()
        self.log_2 = Logger(date=timezone.now() - timezone.timedelta(days=random_days),
                            user_id=self.user_1.id,
                            username=self.user_1.username,
                            action='Adding a new comment on claim with id 1',
                            result=True)
        self.log_2.save()
        random_days = random.randint(1, 10)
        self.log_3 = Logger(date=timezone.now() - timezone.timedelta(days=random_days),
                            user_id=self.user_1.id,
                            username=self.user_1.username,
                            action='Adding a new claim. Error: Missing value for category',
                            result=False)
        self.log_3.save()
        self.log_4 = Logger(date=timezone.now() - timezone.timedelta(days=random_days),
                            user_id=self.user_1.id,
                            username=self.user_1.username,
                            action='Adding a new comment on claim with id 1. '
                                   'Error: You can only comment once on a claim',
                            result=False)
        self.log_4.save()
        self.num_of_saved_logs = 4
        self.post_request = HttpRequest()
        self.post_request.method = 'POST'
        self.get_request = HttpRequest()
        self.get_request.method = 'GET'
        self.csv_fields = MultiValueDict({
            'actions_to_export[]': ["Adding a new claim", "Adding a new comment", "Editing a claim", "Editing a comment",
                                    "Deleting a claim", "Deleting a comment", "Reporting a claim as spam",
                                    "Up voting a comment", "Sending an email", "Down voting a comment"],
            'errors': 'with_errors',
            'date_start': [str(datetime.date.today() - datetime.timedelta(days=20))],
            'date_end': [str(datetime.date.today())]})

        self.error_code = 404

    def tearDown(self):
        pass

    def test_view_log_valid_user(self):
        admin = User.objects.create_superuser('admin', 'admin@gmail.com', 'admin')
        self.get_request.user = admin
        self.assertTrue(view_log(self.get_request).status_code == 200)

    def test_view_log_invalid_user(self):
        self.post_request.user = self.user_1
        self.assertRaises(PermissionDenied, view_log, self.post_request)

    def test_save_log_message_success_action(self):
        user_id = random.randint(1, 10)
        save_log_message(user_id, 'user_1', 'Adding new claim', True)
        log = Logger.objects.all().order_by('-id').first()
        self.assertTrue(log.username == 'user_1')
        self.assertTrue(log.user_id == user_id)
        self.assertTrue(log.action == 'Adding new claim')
        self.assertTrue(log.result)

    def test_save_log_message_failure_action(self):
        user_id = random.randint(1, 10)
        save_log_message(user_id, 'user_1', 'Adding new claim')
        log = Logger.objects.all().order_by('-id').first()
        self.assertTrue(log.username == 'user_1')
        self.assertTrue(log.user_id == user_id)
        self.assertTrue(log.action == 'Adding new claim')
        self.assertFalse(log.result)

    def test_save_log_message_failure_action_invalid_user(self):
        save_log_message(None, '', 'Adding new claim')
        log = Logger.objects.all().order_by('-id').first()
        self.assertTrue(log.username == 'Unknown')
        self.assertTrue(log.user_id == -1)
        self.assertTrue(log.action == 'Adding new claim')
        self.assertFalse(log.result)

    def test_check_duplicate_log_for_user_true(self):
        user_id = random.randint(1, 10)
        self.assertFalse(check_duplicate_log_for_user(user_id, 'Adding new claim'))

    def test_check_duplicate_log_for_user_false(self):
        user_id = random.randint(1, 10)
        save_log_message(user_id, 'user_1', 'Adding new claim')
        self.assertTrue(check_duplicate_log_for_user(user_id, 'Adding new claim'))

    def test_export_to_csv(self):
        admin = User.objects.create_superuser('admin', 'admin@gmail.com', 'admin')
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.csv_fields)
        self.post_request.POST = query_dict
        self.post_request.user = admin
        res = export_to_csv(self.post_request)
        self.assertTrue(res.status_code == 200)
        expected_info = 'Date,User Id,Username,Action,Result\r\n'\
                        '' + str(self.log_4.date.date()) + ',' + str(self.user_1.id) + \
                        ',User1,Adding a new comment on claim with id 1. ' \
                        'Error: You can only comment once on a claim,Failure\r\n' \
                        '' + str(self.log_3.date.date()) + ',' + str(self.user_1.id) + \
                        ',User1,Adding a new claim. ' \
                        'Error: Missing value for category,Failure\r\n'\
                        '' + str(self.log_2.date.date()) + ',' + str(self.user_1.id) + \
                        ',User1,Adding a new comment on claim with id 1,Success\r\n' \
                        '' + str(self.log_1.date.date()) + ',' + str(self.user_1.id) + \
                        ',User1,Adding a new claim,Success\r\n'
        self.assertEqual(res.content.decode('utf-8'), expected_info)

    def test_export_to_csv_invalid_arg_for_actions(self):
        import string
        actions_to_export = self.csv_fields.getlist('actions_to_export[]')
        actions_to_export.append(''.join(random.choices(string.ascii_uppercase + string.digits, k=random.randint(1, 20))))
        self.csv_fields.setlist('actions_to_export[]', actions_to_export)
        admin = User.objects.create_superuser('admin', 'admin@gmail.com', 'admin')
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.csv_fields)
        self.post_request.POST = query_dict
        self.post_request.user = admin
        response = export_to_csv(self.post_request)
        self.assertTrue(response.status_code == self.error_code)

    def test_export_to_csv_missing_args(self):
        admin = User.objects.create_superuser('admin', 'admin@gmail.com', 'admin')
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
            self.post_request.user = admin
            response = export_to_csv(self.post_request)
            self.assertTrue(response.status_code == self.error_code)
            self.csv_fields = dict_copy.copy()

    def test_export_to_csv_empty(self):
        admin = User.objects.create_superuser('admin', 'admin@gmail.com', 'admin')
        self.post_request.user = admin
        Logger.objects.all().delete()
        query_dict = QueryDict('', mutable=True)
        query_dict.update(self.csv_fields)
        self.post_request.POST = query_dict
        res = export_to_csv(self.post_request)
        self.assertTrue(res.status_code == 200)
        self.assertTrue(res.content.decode('utf-8') == 'Date,User Id,Username,Action,Result\r\n')

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
        self.post_request.user = self.user_1
        self.assertRaises(PermissionDenied, export_to_csv, self.post_request)

    def test_check_if_csv_fields_are_valid(self):
        self.assertTrue(check_if_csv_fields_are_valid(self.csv_fields)[0])

    def test_check_if_csv_fields_are_valid_missing_actions_to_export(self):
        del self.csv_fields['actions_to_export[]']
        self.assertFalse(check_if_csv_fields_are_valid(self.csv_fields)[0])

    def test_check_if_csv_fields_are_valid_missing_actions_to_errors(self):
        del self.csv_fields['errors']
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

    def test_check_if_actions_list_valid(self):
        self.assertTrue(check_if_actions_list_valid(self.csv_fields.getlist('actions_to_export[]'))[0])

    def test_check_if_actions_list_valid_invalid_action(self):
        import string
        new_actions = self.csv_fields.getlist('actions_to_export[]')
        new_actions.append(''.join(random.choices(string.ascii_uppercase + string.digits, k=random.randint(1, 20))))
        self.csv_fields.setlist('actions_to_export[]', new_actions)
        self.assertFalse(check_if_actions_list_valid(self.csv_fields.getlist('actions_to_export[]'))[0])

    def test_check_if_actions_list_valid_invalid_actions(self):
        import string
        new_actions = self.csv_fields.getlist('actions_to_export[]')
        for i in range(random.randint(1, 10)):
            new_actions.append(''.join(random.choices(string.ascii_uppercase + string.digits, k=random.randint(1, 20))))
        self.csv_fields.setlist('actions_to_export[]', new_actions)
        self.assertFalse(check_if_actions_list_valid(self.csv_fields.getlist('actions_to_export[]'))[0])

    def test_create_df_for_claims_with_errors(self):
        df_logger = create_df_for_logger(self.csv_fields.getlist('actions_to_export[]'),
                                         'with_errors',
                                         datetime.datetime.strptime(datetime.datetime.strptime(self.csv_fields.get('date_start'),
                                                                    '%Y-%m-%d').strftime('%d/%m/%Y'), '%d/%m/%Y').date(),
                                         datetime.datetime.strptime(datetime.datetime.strptime(self.csv_fields.get('date_end'),
                                                                    '%Y-%m-%d').strftime('%d/%m/%Y'), '%d/%m/%Y').date())
        self.assertTrue(len(df_logger) == self.num_of_saved_logs)
        for index, row in df_logger.iterrows():
            if index == 0:
                self.assertTrue(row['Date'] == self.log_4.date.date())
                self.assertTrue(row['User Id'] == self.log_4.user_id)
                self.assertTrue(row['Username'] == self.log_4.username)
                self.assertTrue(row['Action'] == self.log_4.action)
                self.assertTrue(row['Result'] == 'Failure')
            elif index == 1:
                self.assertTrue(row['Date'] == self.log_3.date.date())
                self.assertTrue(row['User Id'] == self.log_3.user_id)
                self.assertTrue(row['Username'] == self.log_3.username)
                self.assertTrue(row['Action'] == self.log_3.action)
                self.assertTrue(row['Result'] == 'Failure')
            elif index == 2:
                self.assertTrue(row['Date'] == self.log_2.date.date())
                self.assertTrue(row['User Id'] == self.log_2.user_id)
                self.assertTrue(row['Username'] == self.log_2.username)
                self.assertTrue(row['Action'] == self.log_2.action)
                self.assertTrue(row['Result'] == 'Success')
            elif index == 3:
                self.assertTrue(row['Date'] == self.log_1.date.date())
                self.assertTrue(row['User Id'] == self.log_1.user_id)
                self.assertTrue(row['Username'] == self.log_1.username)
                self.assertTrue(row['Action'] == self.log_1.action)
                self.assertTrue(row['Result'] == 'Success')

    def test_create_df_for_logger_without_errors(self):
        df_logger = create_df_for_logger(self.csv_fields.getlist('actions_to_export[]'),
                                         'without_errors',
                                         datetime.datetime.strptime(datetime.datetime.strptime(self.csv_fields.get('date_start'),
                                                                    '%Y-%m-%d').strftime('%d/%m/%Y'), '%d/%m/%Y').date(),
                                         datetime.datetime.strptime(datetime.datetime.strptime(self.csv_fields.get('date_end'),
                                                                    '%Y-%m-%d').strftime('%d/%m/%Y'), '%d/%m/%Y').date())
        self.assertTrue(len(df_logger) == self.num_of_saved_logs - 2)  # 2 for logs with error
        for index, row in df_logger.iterrows():
            if index == 0:
                self.assertTrue(row['Date'] == self.log_2.date.date())
                self.assertTrue(row['User Id'] == self.log_2.user_id)
                self.assertTrue(row['Username'] == self.log_2.username)
                self.assertTrue(row['Action'] == self.log_2.action)
                self.assertTrue(row['Result'] == 'Success')
            elif index == 1:
                self.assertTrue(row['Date'] == self.log_1.date.date())
                self.assertTrue(row['User Id'] == self.log_1.user_id)
                self.assertTrue(row['Username'] == self.log_1.username)
                self.assertTrue(row['Action'] == self.log_1.action)
                self.assertTrue(row['Result'] == 'Success')

    def test_create_df_for_logger_just_errors(self):
        df_logger = create_df_for_logger(self.csv_fields.getlist('actions_to_export[]'),
                                         'just_errors',
                                         datetime.datetime.strptime(datetime.datetime.strptime(self.csv_fields.get('date_start'),
                                                                    '%Y-%m-%d').strftime('%d/%m/%Y'), '%d/%m/%Y').date(),
                                         datetime.datetime.strptime(datetime.datetime.strptime(self.csv_fields.get('date_end'),
                                                                    '%Y-%m-%d').strftime('%d/%m/%Y'), '%d/%m/%Y').date())
        self.assertTrue(len(df_logger) == self.num_of_saved_logs - 2)  # 2 for logs without error
        for index, row in df_logger.iterrows():
            if index == 0:
                self.assertTrue(row['Date'] == self.log_4.date.date())
                self.assertTrue(row['User Id'] == self.log_4.user_id)
                self.assertTrue(row['Username'] == self.log_4.username)
                self.assertTrue(row['Action'] == self.log_4.action)
                self.assertTrue(row['Result'] == 'Failure')
            elif index == 1:
                self.assertTrue(row['Date'] == self.log_3.date.date())
                self.assertTrue(row['User Id'] == self.log_3.user_id)
                self.assertTrue(row['Username'] == self.log_3.username)
                self.assertTrue(row['Action'] == self.log_3.action)
                self.assertTrue(row['Result'] == 'Failure')

    def test_create_df_for_logger_empty(self):
        self.csv_fields['date_start'] = str(datetime.datetime.now().date())
        df_logger = create_df_for_logger(self.csv_fields.getlist('actions_to_export[]'),
                                         'with_errors',
                                         datetime.datetime.strptime(datetime.datetime.strptime(self.csv_fields.get('date_start'),
                                                                    '%Y-%m-%d').strftime('%d/%m/%Y'), '%d/%m/%Y').date(),
                                         datetime.datetime.strptime(datetime.datetime.strptime(self.csv_fields.get('date_end'),
                                                                    '%Y-%m-%d').strftime('%d/%m/%Y'), '%d/%m/%Y').date())
        self.assertTrue(len(df_logger) == 0)
