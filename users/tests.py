from django.test import TestCase
from users.models import User
from users.views import reset_users, get_user_id_by_username, add_all_scrapers

class UsersTest(TestCase):

    def setUp(self):
        self.user_1 = User(username="User1", email='user1@gmail.com', state='Regular', reputation=-1)
        self.user_2= User(username="User2", email='user2@gmail.com', state='Regular', reputation=-1)
        self.user_3= User(username="User3", email='user3@gmail.com', state='Admin', reputation=10)
        self.user_1.save()
        self.user_2.save()
        self.user_3.save()

    def tearDown(self):
        pass

    def test_reset_users(self):
        reset_users()
        self.assertTrue(len(User.objects.all()) == 0)

    def test_get_user_id_by_username(self):
        self.assertTrue(get_user_id_by_username('User1') == self.user_1.id)
        self.assertTrue(get_user_id_by_username('User2') == self.user_2.id)
        self.assertTrue(get_user_id_by_username('User3') == self.user_3.id)
        self.assertTrue(get_user_id_by_username('User4') is None)

    def test_add_all_scrapers(self):
        reset_users()
        add_all_scrapers()
        self.assertTrue(get_user_id_by_username('Snopes') == 4)
        self.assertTrue(get_user_id_by_username('Polygraph') == 5)
        self.assertTrue(get_user_id_by_username('TruthOrFiction') == 6)
