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
    scraper_1 = User(username='Snopes', email='', state='', reputation=-1,
                     user_img='https://www.snopes.com/content/themes/snopes/dist/images/logo-s-crop-on.svg')
    scraper_2 = User(username='Polygraph', email='', state='', reputation=-1,
                     user_img='https://www.polygraph.info/Content/responsive/RFE/en-Poly/img/logo.png')
    scraper_3 = User(username='TruthOrFiction', email='', state='', reputation=-1,
                     user_img='https://dn.truthorfiction.com/wp-content/uploads/2018/10/25032229/truth-or-fiction-logo-tagline.png')
    scraper_4 = User(username='Politifact', email='', state='', reputation=-1,
                     user_img='https://static.politifact.com/images/POLITIFACT_logo_rgb141x25.png')
    scraper_5 = User(username='GossipCop', email='', state='', reputation=-1,
                     user_img='https://s3.gossipcop.com/thm/gossipcop/images/horizontal-logo.png')
    scraper_6 = User(username='ClimateFeedback', email='', state='', reputation=-1,
                     user_img='https://climatefeedback.org/wp-content/themes/wordpress-theme/dist/images/Climate_Feedback_logo_s.png')
    scraper_7 = User(username='FactScan', email='', state='', reputation=-1,
                     user_img='http://factscan.ca/test/wp-content/uploads/2015/02/web-logo.png')
    scraper_8 = User(username='AfricaCheck', email='', state='', reputation=-1,
                     user_img='https://upload.wikimedia.org/wikipedia/en/2/2f/Africa_Check_Website_logo.png')
    scraper_1.save()
    scraper_2.save()
    scraper_3.save()
    scraper_4.save()
    scraper_5.save()
    scraper_6.save()
    scraper_7.save()
    scraper_8.save()


# This function deletes all the website users
def reset_users():
    User.objects.all().delete()

