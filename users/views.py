from users.models import User


def get_user_id_by_username(username):
    result = User.objects.filter(username = username)
    if len(result) > 0:
        return result[0].id
    return None


def add_all_scrapers():
    scraper_1 = User(username='Snopes', email='', state='', reputation=-1)
    scraper_2 = User(username='Polygraph', email='', state='', reputation=-1)
    scraper_3 = User(username='TruthOrFiction', email='', state='', reputation=-1)
    scraper_1.save()
    scraper_2.save()
    scraper_3.save()


def reset_users():
    User.objects.all().delete()

