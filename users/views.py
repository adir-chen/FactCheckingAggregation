from django.contrib.auth.models import User
from users.models import Users_Images, Scrapers
from users.models import Users_Reputations


# This function returns true in case the user exists, otherwise false
def check_if_user_exists_by_user_id(user_id):
    result = User.objects.filter(id=user_id)
    if len(result) > 0:
        return True
    return False


# This function returns the username id for a given user's id
def get_username_by_user_id(user_id):
    result = User.objects.filter(id=user_id)
    if len(result) > 0:
        return result[0].username
    return None


# This function adds all the scrapers as users to the website
def add_all_scrapers():
    scraper_1 = User(username='Snopes')
    scraper_1.save()
    scraper_1_img = Users_Images(user_id=scraper_1, user_img='https://www.snopes.com/content/themes/snopes/dist/images/logo-s-crop-on.svg')
    scraper_1_img.save()
    scraper_1_rep = Users_Reputations(user_id=scraper_1, user_rep=0)
    scraper_1_rep.save()
    scraper_1_details = Scrapers(scraper_name=scraper_1.username, scraper_id=scraper_1)
    scraper_1_details.save()

    scraper_2 = User(username='Polygraph')
    scraper_2.save()
    scraper_2_img = Users_Images(user_id=scraper_2, user_img='https://www.polygraph.info/Content/responsive/RFE/en-Poly/img/logo.png')
    scraper_2_img.save()
    scraper_2_rep = Users_Reputations(user_id=scraper_2, user_rep=0)
    scraper_2_rep.save()
    scraper_2_details = Scrapers(scraper_name=scraper_2.username, scraper_id=scraper_2)
    scraper_2_details.save()

    scraper_3 = User(username='TruthOrFiction')
    scraper_3.save()
    scraper_3_img = Users_Images(user_id=scraper_3, user_img='https://dn.truthorfiction.com/wp-content/uploads/2018/10/25032229/truth-or-fiction-logo-tagline.png')
    scraper_3_img.save()
    scraper_3_rep = Users_Reputations(user_id=scraper_3, user_rep=0)
    scraper_3_rep.save()
    scraper_3_details = Scrapers(scraper_name=scraper_3.username, scraper_id=scraper_3)
    scraper_3_details.save()

    scraper_4 = User(username='Politifact')
    scraper_4.save()
    scraper_4_img = Users_Images(user_id=scraper_4, user_img='https://static.politifact.com/images/POLITIFACT_logo_rgb141x25.png')
    scraper_4_img.save()
    scraper_4_rep = Users_Reputations(user_id=scraper_4, user_rep=0)
    scraper_4_rep.save()
    scraper_4_details = Scrapers(scraper_name=scraper_4.username, scraper_id=scraper_4)
    scraper_4_details.save()

    scraper_5 = User(username='GossipCop')
    scraper_5.save()
    scraper_5_img = Users_Images(user_id=scraper_5, user_img='https://s3.gossipcop.com/thm/gossipcop/images/horizontal-logo.png')
    scraper_5_img.save()
    scraper_5_rep = Users_Reputations(user_id=scraper_5, user_rep=0)
    scraper_5_rep.save()
    scraper_5_details = Scrapers(scraper_name=scraper_5.username, scraper_id=scraper_5)
    scraper_5_details.save()

    scraper_6 = User(username='ClimateFeedback')
    scraper_6.save()
    scraper_6_img = Users_Images(user_id=scraper_6, user_img='https://climatefeedback.org/wp-content/themes/wordpress-theme/dist/images/Climate_Feedback_logo_s.png')
    scraper_6_img.save()
    scraper_6_rep = Users_Reputations(user_id=scraper_6, user_rep=0)
    scraper_6_rep.save()
    scraper_6_details = Scrapers(scraper_name=scraper_6.username, scraper_id=scraper_6)
    scraper_6_details.save()

    scraper_7 = User(username='FactScan')
    scraper_7.save()
    scraper_7_img = Users_Images(user_id=scraper_7, user_img='http://factscan.ca/test/wp-content/uploads/2015/02/web-logo.png')
    scraper_7_img.save()
    scraper_7_rep = Users_Reputations(user_id=scraper_7, user_rep=0)
    scraper_7_rep.save()
    scraper_7_details = Scrapers(scraper_name=scraper_7.username, scraper_id=scraper_7)
    scraper_7_details.save()

    scraper_8 = User(username='AfricaCheck')
    scraper_8.save()
    scraper_8_img = Users_Images(user_id=scraper_8, user_img='https://upload.wikimedia.org/wikipedia/en/2/2f/Africa_Check_Website_logo.png')
    scraper_8_img.save()
    scraper_8_rep = Users_Reputations(user_id=scraper_8, user_rep=0)
    scraper_8_rep.save()
    scraper_8_details = Scrapers(scraper_name=scraper_8.username, scraper_id=scraper_8)
    scraper_8_details.save()


# This function returns all the scrapers ids'
def get_all_scrapers_ids(request):
    from django.http import JsonResponse
    scrapers = {}
    result = Scrapers.objects.all()
    for scraper in result:
        scrapers[scraper.scraper_name] = scraper.scraper_id.id
    return JsonResponse(scrapers)
