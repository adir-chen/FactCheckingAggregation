from users.models import User


# This function returns the user's id of a given username
def get_user_id_by_username(username):
    result = User.objects.filter(username=username)
    if len(result) > 0:
        return result[0].id
    return None


# This function returns the username id of a given user's id
def get_username_by_user_id(id):
    result = User.objects.filter(id=id)
    if len(result) > 0:
        return result[0].username
    return None


# This function adds all the scrapers as users to the website
def add_all_scrapers():
    scraper_1 = User(username='Snopes', email='', state='', reputation=-1)
    scraper_2 = User(username='Polygraph', email='', state='', reputation=-1)
    scraper_3 = User(username='TruthOrFiction', email='', state='', reputation=-1)
    scraper_1.save()
    scraper_2.save()
    scraper_3.save()


# This function deletes all the website users
def reset_users():
    User.objects.all().delete()

