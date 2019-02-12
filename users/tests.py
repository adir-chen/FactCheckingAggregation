from django.http import HttpRequest
from django.test import TestCase
from users.models import User
from users.views import check_if_user_exists_by_user_id, get_username_by_user_id, add_all_scrapers, get_all_scrapers_ids


class UsersTest(TestCase):
    def setUp(self):
        self.user_1 = User(username="User1", email='user1@gmail.com')
        self.user_2 = User(username="User2", email='user2@gmail.com')
        self.user_3 = User(username="User3", email='user3@gmail.com')
        self.user_1.save()
        self.user_2.save()
        self.user_3.save()

    def tearDown(self):
        pass

    def test_check_if_user_exists_by_user_id(self):
        self.assertTrue(check_if_user_exists_by_user_id(1))
        self.assertTrue(check_if_user_exists_by_user_id(2))
        self.assertTrue(check_if_user_exists_by_user_id(3))

    def test_check_if_user_exists_by_invalid_user_id(self):
        self.assertFalse(check_if_user_exists_by_user_id(4))

    def test_get_username_by_user_id(self):
        self.assertTrue(get_username_by_user_id(1) == self.user_1.username)
        self.assertTrue(get_username_by_user_id(2) == self.user_2.username)
        self.assertTrue(get_username_by_user_id(3) == self.user_3.username)

    def test_get_username_by_user_id_invalid_user(self):
        self.assertTrue(get_username_by_user_id(4) is None)

    def test_add_all_scrapers(self):
        add_all_scrapers()
        self.assertTrue(check_if_user_exists_by_user_id(4))
        self.assertTrue(check_if_user_exists_by_user_id(5))
        self.assertTrue(check_if_user_exists_by_user_id(6))
        self.assertTrue(check_if_user_exists_by_user_id(7))
        self.assertTrue(check_if_user_exists_by_user_id(8))
        self.assertTrue(check_if_user_exists_by_user_id(9))
        self.assertTrue(check_if_user_exists_by_user_id(10))
        self.assertTrue(check_if_user_exists_by_user_id(11))
        self.assertTrue(get_username_by_user_id(4) == 'Snopes')
        self.assertTrue(get_username_by_user_id(5) == 'Polygraph')
        self.assertTrue(get_username_by_user_id(6) == 'TruthOrFiction')
        self.assertTrue(get_username_by_user_id(7) == 'Politifact')
        self.assertTrue(get_username_by_user_id(8) == 'GossipCop')
        self.assertTrue(get_username_by_user_id(9) == 'ClimateFeedback')
        self.assertTrue(get_username_by_user_id(10) == 'FactScan')
        self.assertTrue(get_username_by_user_id(11) == 'AfricaCheck')

    def test_get_all_scrapers_ids(self):
        import json
        add_all_scrapers()
        scrapers_ids = json.loads(get_all_scrapers_ids(HttpRequest()).content.decode('utf-8'))
        self.assertTrue(scrapers_ids == {'Snopes': 4,
                                         'Polygraph': 5,
                                         'TruthOrFiction': 6,
                                         'Politifact': 7,
                                         'GossipCop': 8,
                                         'ClimateFeedback': 9,
                                         'FactScan': 10,
                                         'AfricaCheck': 11,
                                         })