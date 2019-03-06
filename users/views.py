from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import render
from claims.models import Claim
from comments.models import Comment
from logger.views import save_log_message
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
        return result.first().username
    return None


# This function adds all the scrapers as users to the website
def add_all_scrapers(request):
    from claims.views import view_home
    if not request.user.is_superuser:
        raise Http404("Permission denied")
    try:
        password = User.objects.make_random_password()
        # print(password)
        scraper_1 = User.objects.create_user(username='Snopes', password=password)
        scraper_1.save()
        scraper_1_img = Users_Images(user_id=scraper_1, user_img='https://www.snopes.com/content/themes/snopes/dist/images/logo-s-crop-on.svg')
        scraper_1_img.save()
        scraper_1_rep = Users_Reputations(user_id=scraper_1, user_rep=0)
        scraper_1_rep.save()
        true_labels = ['true', 'probably true', 'partly true', 'correct attribution', 'mostly true']
        false_labels = ['false', 'not true', 'mostly false', 'fiction', 'legend', 'scam', 'miscaptioned']
        scraper_1_details = Scrapers(scraper_name=scraper_1.username,
                                     scraper_id=scraper_1,
                                     true_labels=','.join(true_labels),
                                     false_labels=','.join(false_labels))
        scraper_1_details.save()

        scraper_2 = User.objects.create_user(username='Polygraph', password=password)
        scraper_2.save()
        scraper_2_img = Users_Images(user_id=scraper_2, user_img='https://www.polygraph.info/Content/responsive/RFE/en-Poly/img/logo.png')
        scraper_2_img.save()
        scraper_2_rep = Users_Reputations(user_id=scraper_2, user_rep=0)
        scraper_2_rep.save()
        true_labels = ['true', 'partially true', 'likely true']
        false_labels = ['false', 'mostly false', 'highly misleading', 'misleading', 'likely false', 'partially false']
        scraper_2_details = Scrapers(scraper_name=scraper_2.username,
                                     scraper_id=scraper_2,
                                     true_labels=','.join(true_labels),
                                     false_labels=','.join(false_labels))
        scraper_2_details.save()

        scraper_3 = User.objects.create_user(username='TruthOrFiction', password=password)
        scraper_3.save()
        scraper_3_img = Users_Images(user_id=scraper_3, user_img='https://dn.truthorfiction.com/wp-content/uploads/2018/10/25032229/truth-or-fiction-logo-tagline.png')
        scraper_3_img.save()
        scraper_3_rep = Users_Reputations(user_id=scraper_3, user_rep=0)
        scraper_3_rep.save()
        true_labels = ['true', 'truth']
        false_labels = ['false', 'not true', 'decontextualized', 'fiction']
        scraper_3_details = Scrapers(scraper_name=scraper_3.username,
                                     scraper_id=scraper_3,
                                     true_labels=','.join(true_labels),
                                     false_labels=','.join(false_labels))
        scraper_3_details.save()

        scraper_4 = User.objects.create_user(username='Politifact', password=password)
        scraper_4.save()
        scraper_4_img = Users_Images(user_id=scraper_4, user_img='https://static.politifact.com/images/POLITIFACT_logo_rgb141x25.png')
        scraper_4_img.save()
        scraper_4_rep = Users_Reputations(user_id=scraper_4, user_rep=0)
        scraper_4_rep.save()
        true_labels = ['true', 'mostly true', 'no flip']
        false_labels = ['false', 'mostly false', 'full flop', 'pants on fire!']
        scraper_4_details = Scrapers(scraper_name=scraper_4.username,
                                     scraper_id=scraper_4,
                                     true_labels=','.join(true_labels),
                                     false_labels=','.join(false_labels))
        scraper_4_details.save()

        scraper_5 = User.objects.create_user(username='GossipCop', password=password)
        scraper_5.save()
        scraper_5_img = Users_Images(user_id=scraper_5, user_img='https://s3.gossipcop.com/thm/gossipcop/images/horizontal-logo.png')
        scraper_5_img.save()
        scraper_5_rep = Users_Reputations(user_id=scraper_5, user_rep=0)
        scraper_5_rep.save()
        true_labels = [str(i + 6) for i in range(5)]
        false_labels = [str(i) for i in range(5)]
        scraper_5_details = Scrapers(scraper_name=scraper_5.username,
                                     scraper_id=scraper_5,
                                     true_labels=','.join(true_labels),
                                     false_labels=','.join(false_labels))
        scraper_5_details.save()

        scraper_6 = User.objects.create_user(username='ClimateFeedback', password=password)
        scraper_6.save()
        scraper_6_img = Users_Images(user_id=scraper_6, user_img='https://climatefeedback.org/wp-content/themes/wordpress-theme/dist/images/Climate_Feedback_logo_s.png')
        scraper_6_img.save()
        scraper_6_rep = Users_Reputations(user_id=scraper_6, user_rep=0)
        scraper_6_rep.save()
        true_labels = ['true', 'accurate', 'mostly_correct', 'correct']
        false_labels = ['false', 'unsupported', 'incorrect', 'inaccurate', 'misleading', 'flawed_reasoning']
        scraper_6_details = Scrapers(scraper_name=scraper_6.username,
                                     scraper_id=scraper_6,
                                     true_labels=','.join(true_labels),
                                     false_labels=','.join(false_labels))
        scraper_6_details.save()

        scraper_7 = User.objects.create_user(username='FactScan', password=password)
        scraper_7.save()
        scraper_7_img = Users_Images(user_id=scraper_7, user_img='http://factscan.ca/test/wp-content/uploads/2015/02/web-logo.png')
        scraper_7_img.save()
        scraper_7_rep = Users_Reputations(user_id=scraper_7, user_rep=0)
        scraper_7_rep.save()
        true_labels = ['true']
        false_labels = ['false', 'misleading', 'farcical']
        scraper_7_details = Scrapers(scraper_name=scraper_7.username,
                                     scraper_id=scraper_7,
                                     true_labels=','.join(true_labels),
                                     false_labels=','.join(false_labels))
        scraper_7_details.save()

        scraper_8 = User.objects.create_user(username='AfricaCheck', password=password)
        scraper_8.save()
        scraper_8_img = Users_Images(user_id=scraper_8, user_img='https://upload.wikimedia.org/wikipedia/en/2/2f/Africa_Check_Website_logo.png')
        scraper_8_img.save()
        scraper_8_rep = Users_Reputations(user_id=scraper_8, user_rep=0)
        scraper_8_rep.save()
        scraper_8_details = Scrapers(scraper_name=scraper_8.username, scraper_id=scraper_8)
        scraper_8_details.save()
    except Exception:
        raise Http404("Permission denied - Scrapers already exist")
    return view_home(request)


# def update_scrapers_info(request):
#     from comments.models import Comment
#     if not check_if_user_exists_by_user_id(scraper_id):
#         raise Exception('Scraper with id ' + str(scraper_id) + ' does not exists')
#     scraper = User.objects.filter(id=scraper_id).first()
#     Scrapers.objects.filter(scraper_id=scraper).update()
#     for comment in Comment.objects.filter(user_id=scraper):
#             label = comment.label.lower().strip()
#             scraper = Scrapers.objects.filter(scraper_id=).first()
#             if label in scraper.true_labels:
#                 Comment.objects.filter(id=comment.id).update(system_label='True')
#             elif label in scraper.false_labels:
#                 Comment.objects.filter(id=comment.id).update(system_label='False')
#             else:
#                 Comment.objects.filter(id=comment.id).update(system_label='Unknown')


# This function returns all the scrapers' ids
def get_all_scrapers_ids(request):
    from django.http import JsonResponse
    scrapers = {}
    result = Scrapers.objects.all()
    for scraper in result:
        scrapers[scraper.scraper_name] = scraper.scraper_id.id
    return JsonResponse(scrapers)


# This function returns all the scrapers' ids in an array
def get_all_scrapers_ids_arr():
    all_scrapers_ids = []
    result = Scrapers.objects.all()
    for scraper in result:
        all_scrapers_ids.append(scraper.scraper_id.id)
    return all_scrapers_ids


# This function returns a random claim for each scraper in the system for testing (the scrapers)
def get_random_claims_from_scrapers(request):
    from django.http import JsonResponse
    claims = {}
    result = Scrapers.objects.all()
    from claims.models import Claim
    from comments.models import Comment
    for scraper in result:
        claim_comment = Comment.objects.all().filter(user_id=scraper.scraper_id.id).order_by('-id')
        if len(claim_comment):
            claim_comment = claim_comment.first()
            claim_details = Claim.objects.filter(id=claim_comment.claim_id).first()
            claims[scraper.scraper_name] = {'title': claim_comment.title,
                                            'claim': claim_details.claim,
                                            'description': claim_comment.description,
                                            'url': claim_comment.url,
                                            'verdict_date': claim_comment.verdict_date,
                                            'category': claim_details.category,
                                            'label': claim_comment.label}
    return JsonResponse(claims)


# This function return an HTML page for adding a new scraper
def add_scraper_guide(request):
    return render(request, 'users/add_scraper_guide.html')


# This function add new scraper to the website
def add_new_scraper(request):
    if request.user.is_superuser:
        scraper_info = request.POST.dict()
        valid_scraper, err_msg = check_if_scraper_info_is_valid(scraper_info)
        if not valid_scraper:
            save_log_message(request.user.id, request.user.username,
                             'Adding a new scraper. Error: ' + err_msg)
            raise Exception(err_msg)
        true_labels = scraper_info['scraper_true_labels'].lower().split()
        if 'true' not in true_labels:
            true_labels.append('true')
        false_labels = scraper_info['scraper_false_labels'].lower().split()
        if 'false' not in false_labels:
            false_labels.append('false')
        new_scraper = User.objects.create_user(username=scraper_info['scraper_name'],
                                               password=scraper_info['scraper_password'])
        new_scraper.save()
        new_scraper_img = Users_Images(user_id=new_scraper,
                                       user_img=scraper_info['scraper_icon'])
        new_scraper_img.save()

        new_scraper_rep = Users_Reputations(user_id=new_scraper, user_rep=0)
        new_scraper_rep.save()

        new_scraper_img_details = Scrapers(scraper_name=new_scraper.username,
                                           scraper_id=new_scraper,
                                           true_labels=','.join(true_labels),
                                           false_labels=','.join(false_labels))
        new_scraper_img_details.save()
        save_log_message(request.user.id, request.user.username, 'Adding a new scraper', True)
        return add_scraper_guide(request)
    raise Http404("Permission denied")


# This function checks if a given scraper's info is valid, i.e. the info has all the fields with the correct format.
# The function returns true in case the info is valid, otherwise false and an error
def check_if_scraper_info_is_valid(scraper_info):
    err = ''
    if 'scraper_name' not in scraper_info or not scraper_info['scraper_name']:
        err += 'Missing value for scraper\'s name'
    elif 'scraper_password' not in scraper_info or not scraper_info['scraper_password']:
        err += 'Missing value for scraper\'s password'
    elif 'scraper_password_2' not in scraper_info or not scraper_info['scraper_password_2'] \
            or not scraper_info['scraper_password'] == scraper_info['scraper_password_2']:
        err += 'Passwords do not match'
    elif 'scraper_icon' not in scraper_info or not scraper_info['scraper_icon']:
        err += 'Missing value for scraper\'s icon'
    elif len(User.objects.filter(username=scraper_info['scraper_name'])) != 0:
        err += 'Scraper ' + scraper_info['scraper_name'] + ' already exists'
    if len(err) > 0:
        return False, err
    return True, err


# This function updates a user's reputation
def update_reputation_for_user(user_id, earn_points, num_of_points):
    if not check_if_user_exists_by_user_id(user_id):
        raise Exception('User with id ' + str(user_id) + ' does not exist')
    user = User.objects.filter(id=user_id).first()
    user_rep = Users_Reputations.objects.filter(user_id=user)
    if len(user_rep) == 0:  # user has no reputation
        new_user_rep = Users_Reputations(user_id=user)
        new_user_rep.save()
        reputation = 1
    else:
        reputation = user_rep.first().user_rep
    if earn_points:
        reputation = min(100, reputation + num_of_points)
    else:
        reputation = max(1, reputation - num_of_points)
    Users_Reputations.objects.filter(user_id=user).update(user_rep=reputation)


# This function returns a HTML for user's profile
def user_page(request, username):
    user = get_user_by_username(username)
    if user is None:
        raise Http404('User with username ' + username + ' does not exist')
    user_rep = Users_Reputations.objects.filter(user_id=user.id)
    claims = Claim.objects.filter(user=user.id)
    comments = Comment.objects.filter(user=user.id)
    user_claims = list(get_users_images_for_claims(claims).items())
    page = request.GET.get('page1')
    paginator = Paginator(user_claims, 3)
    headlines = {}
    for comment in comments:
        headlines[comment] = User.objects.filter(id=comment.user_id).first()
    user_comments = list(headlines.items())
    page2 = request.GET.get('page2')
    paginator2 = Paginator(user_comments, 3)
    return render(request, 'users/user_page.html', {
        'reputation': user_rep,
        'user_claims': paginator.get_page(page),
        'user_comments': paginator2.get_page(page2),
    })


# This function returns a user by the specified username
def get_user_by_username(username):
    result = User.objects.filter(username=username)
    if len(result) > 0:
        return result[0]
    return None


# This function return a HTML page for my own profile
def my_profile_page(request):
    user_rep = Users_Reputations.objects.filter(user_id=request.user.id)
    claims = Claim.objects.filter(user=request.user.id)
    comments = Comment.objects.filter(user=request.user.id)
    user_claims = list(get_users_images_for_claims(claims).items())
    page = request.GET.get('page1')
    paginator = Paginator(user_claims, 3)
    headlines = {}
    '''for claim in claims:
        user_img = Users_Images.objects.filter(user_id=User.objects.filter(id=claim.user_id).first())
        if len(user_img) == 0:
            new_user_img = Users_Images.objects.create(user_id=User.objects.filter(id=claim.user_id).first())
            new_user_img.save()
            user_img = new_user_img
        else:
            user_img = user_img.first()
        user_claims[claim] = user_img.user_img'''
    for comment in comments:
        headlines[comment] = User.objects.filter(id=comment.user_id).first()
    user_comments = list(headlines.items())
    page2 = request.GET.get('page2')
    paginator2 = Paginator(user_comments, 3)
    return render(request, 'users/my_profile.html', {
        'reputation': user_rep,
        'user_claims': paginator.get_page(page),
        'user_comments': paginator2.get_page(page2),
    })


def get_users_images_for_claims(claims):
    headlines = {}
    for claim in claims:
        user_img = Users_Images.objects.filter(user_id=User.objects.filter(id=claim.user_id).first())
        if len(user_img) == 0:
            new_user_img = Users_Images.objects.create(user_id=User.objects.filter(id=claim.user_id).first())
            new_user_img.save()
            user_img = new_user_img
        else:
            user_img = user_img.first()
        headlines[claim] = user_img.user_img
    return headlines
