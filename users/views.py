from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import render
from claims.models import Claim
from comments.models import Comment
from logger.views import save_log_message
from tweets.models import Tweet
from users.models import Users_Images, Scrapers
from users.models import Users_Reputations


# This function returns true in case the user exists, otherwise false
def check_if_user_exists_by_user_id(user_id):
    result = User.objects.filter(id=user_id)
    if len(result) > 0:
        return True
    return False


# This function returns the username for a given user's id (in case the user exists), otherwise none
def get_username_by_user_id(user_id):
    result = User.objects.filter(id=user_id)
    if len(result) > 0:
        return result.first().username
    return None


# This function returns the user object for a given username (in case the username exists), otherwise none
def get_user_by_username(username):
    result = User.objects.filter(username=username)
    if len(result) > 0:
        return result.first()
    return None


# This function adds all the scrapers as users to the website
def add_all_scrapers(request):
    from claims.views import view_home, return_get_request_to_user
    if not request.user.is_superuser or request.method != 'GET':
        raise Http404("Permission denied")
    try:
        password = User.objects.make_random_password()
        # print(password)
        scraper_1 = User.objects.create_user(username='Snopes', password=password)
        scraper_1.save()
        scraper_1_img = Users_Images(user_id=scraper_1, user_img='https://www.snopes.com/content/themes/snopes/dist/images/logo-s-crop-on.svg')
        scraper_1_img.save()
        scraper_1_rep = Users_Reputations(user_id=scraper_1)
        scraper_1_rep.save()
        true_labels = ['true', 'probably true', 'partly true', 'correct attribution', 'mostly true']
        false_labels = ['false', 'not true', 'mostly false', 'fiction', 'legend', 'scam', 'miscaptioned']
        scraper_1_details = Scrapers(scraper_name=scraper_1.username,
                                     scraper_id=scraper_1,
                                     true_labels=','.join(true_labels),
                                     false_labels=','.join(false_labels))
        scraper_1_details.save()

        password = User.objects.make_random_password()
        scraper_2 = User.objects.create_user(username='Polygraph', password=password)
        scraper_2.save()
        scraper_2_img = Users_Images(user_id=scraper_2, user_img='https://www.polygraph.info/Content/responsive/RFE/en-Poly/img/logo.png')
        scraper_2_img.save()
        scraper_2_rep = Users_Reputations(user_id=scraper_2)
        scraper_2_rep.save()
        true_labels = ['true', 'partially true', 'likely true']
        false_labels = ['false', 'mostly false', 'highly misleading', 'misleading', 'likely false', 'partially false']
        scraper_2_details = Scrapers(scraper_name=scraper_2.username,
                                     scraper_id=scraper_2,
                                     true_labels=','.join(true_labels),
                                     false_labels=','.join(false_labels))
        scraper_2_details.save()

        password = User.objects.make_random_password()
        scraper_3 = User.objects.create_user(username='TruthOrFiction', password=password)
        scraper_3.save()
        scraper_3_img = Users_Images(user_id=scraper_3, user_img='https://dn.truthorfiction.com/wp-content/uploads/2018/10/25032229/truth-or-fiction-logo-tagline.png')
        scraper_3_img.save()
        scraper_3_rep = Users_Reputations(user_id=scraper_3)
        scraper_3_rep.save()
        true_labels = ['true', 'truth', 'truth!', 'mostly truth!', 'authorship confirmed!', 'correct attribution!', 'correctly attributed!']
        false_labels = ['false', 'not true', 'fiction', 'fiction!', 'mostly fiction!', 'reported fiction!',
                        'incorrect attribution!', 'misleading!', 'misattributed', 'decontextualized']
        scraper_3_details = Scrapers(scraper_name=scraper_3.username,
                                     scraper_id=scraper_3,
                                     true_labels=','.join(true_labels),
                                     false_labels=','.join(false_labels))
        scraper_3_details.save()

        password = User.objects.make_random_password()
        scraper_4 = User.objects.create_user(username='Politifact', password=password)
        scraper_4.save()
        scraper_4_img = Users_Images(user_id=scraper_4, user_img='https://static.politifact.com/images/POLITIFACT_logo_rgb141x25.png')
        scraper_4_img.save()
        scraper_4_rep = Users_Reputations(user_id=scraper_4)
        scraper_4_rep.save()
        true_labels = ['true', 'mostly true', 'no flip']
        false_labels = ['false', 'mostly false', 'full flop', 'pants on fire!']
        scraper_4_details = Scrapers(scraper_name=scraper_4.username,
                                     scraper_id=scraper_4,
                                     true_labels=','.join(true_labels),
                                     false_labels=','.join(false_labels))
        scraper_4_details.save()

        password = User.objects.make_random_password()
        scraper_5 = User.objects.create_user(username='GossipCop', password=password)
        scraper_5.save()
        scraper_5_img = Users_Images(user_id=scraper_5, user_img='https://s3.gossipcop.com/thm/gossipcop/images/horizontal-logo.png')
        scraper_5_img.save()
        scraper_5_rep = Users_Reputations(user_id=scraper_5)
        scraper_5_rep.save()
        true_labels = [str(i + 6) for i in range(5)]
        false_labels = [str(i) for i in range(5)]
        scraper_5_details = Scrapers(scraper_name=scraper_5.username,
                                     scraper_id=scraper_5,
                                     true_labels=','.join(true_labels),
                                     false_labels=','.join(false_labels))
        scraper_5_details.save()

        password = User.objects.make_random_password()
        scraper_6 = User.objects.create_user(username='ClimateFeedback', password=password)
        scraper_6.save()
        scraper_6_img = Users_Images(user_id=scraper_6, user_img='https://climatefeedback.org/wp-content/themes/wordpress-theme/dist/images/Climate_Feedback_logo_s.png')
        scraper_6_img.save()
        scraper_6_rep = Users_Reputations(user_id=scraper_6)
        scraper_6_rep.save()
        true_labels = ['true', 'accurate', 'mostly_correct', 'correct']
        false_labels = ['false', 'unsupported', 'incorrect', 'inaccurate', 'misleading', 'flawed_reasoning']
        scraper_6_details = Scrapers(scraper_name=scraper_6.username,
                                     scraper_id=scraper_6,
                                     true_labels=','.join(true_labels),
                                     false_labels=','.join(false_labels))
        scraper_6_details.save()

        password = User.objects.make_random_password()
        scraper_7 = User.objects.create_user(username='FactScan', password=password)
        scraper_7.save()
        scraper_7_img = Users_Images(user_id=scraper_7, user_img='http://factscan.ca/test/wp-content/uploads/2015/02/web-logo.png')
        scraper_7_img.save()
        scraper_7_rep = Users_Reputations(user_id=scraper_7)
        scraper_7_rep.save()
        true_labels = ['true']
        false_labels = ['false', 'misleading', 'farcical']
        scraper_7_details = Scrapers(scraper_name=scraper_7.username,
                                     scraper_id=scraper_7,
                                     true_labels=','.join(true_labels),
                                     false_labels=','.join(false_labels))
        scraper_7_details.save()

        password = User.objects.make_random_password()
        scraper_8 = User.objects.create_user(username='AfricaCheck', password=password)
        scraper_8.save()
        scraper_8_img = Users_Images(user_id=scraper_8, user_img='https://upload.wikimedia.org/wikipedia/en/2/2f/Africa_Check_Website_logo.png')
        scraper_8_img.save()
        scraper_8_rep = Users_Reputations(user_id=scraper_8)
        scraper_8_rep.save()
        scraper_8_details = Scrapers(scraper_name=scraper_8.username, scraper_id=scraper_8)
        scraper_8_details.save()

        password = User.objects.make_random_password()
        scraper_9 = User.objects.create_user(username='CNN', password=password)
        scraper_9.save()
        scraper_9_img = Users_Images(user_id=scraper_9, user_img='https://cdn.cnn.com/cnn/.e1mo/img/4.0/logos/CNN_logo_400x400.png')
        scraper_9_img.save()
        scraper_9_rep = Users_Reputations(user_id=scraper_9)
        scraper_9_rep.save()
        scraper_9_details = Scrapers(scraper_name=scraper_9.username,
                                     scraper_id=scraper_9)
        scraper_9_details.save()
    except Exception:
        raise Http404("Permission denied - Scrapers already exist")
    return view_home(return_get_request_to_user(request.user))


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
    if request.method != 'GET':
        raise Http404("Permission denied")
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
    if not request.user.is_superuser or request.method != 'GET':
        raise Http404("Permission denied")
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
    from claims.views import return_get_request_to_user
    if not request.user.is_superuser or request.method != 'POST':
        raise Http404("Permission denied")
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

    new_scraper_rep = Users_Reputations(user_id=new_scraper)
    new_scraper_rep.save()

    new_scraper_img_details = Scrapers(scraper_name=new_scraper.username,
                                       scraper_id=new_scraper,
                                       true_labels=','.join(true_labels),
                                       false_labels=','.join(false_labels))
    new_scraper_img_details.save()
    save_log_message(request.user.id, request.user.username, 'Adding a new scraper', True)
    return add_scraper_guide(return_get_request_to_user(request.user))


# This function checks if a given scraper's info is valid (for adding a new scraper),
# i.e. the info has all the fields with the correct format.
# The function returns true in case the info is valid, otherwise false and an error
def check_if_scraper_info_is_valid(scraper_info):
    from claims.views import check_if_input_format_is_valid, is_english_input
    err = ''
    if 'scraper_name' not in scraper_info or not scraper_info['scraper_name']:
        err += 'Missing value for scraper\'s name'
    elif not check_if_input_format_is_valid(scraper_info['scraper_true_labels']):
        err += 'Incorrect format for scraper\'s true labels'
    elif not check_if_input_format_is_valid(scraper_info['scraper_false_labels']):
        err += 'Incorrect format for scraper\'s false labels'
    elif 'scraper_password' not in scraper_info or not scraper_info['scraper_password']:
        err += 'Missing value for scraper\'s password'
    elif 'scraper_password_2' not in scraper_info or not scraper_info['scraper_password_2'] \
            or not scraper_info['scraper_password'] == scraper_info['scraper_password_2']:
        err += 'Passwords do not match'
    elif 'scraper_icon' not in scraper_info or not scraper_info['scraper_icon']:
        err += 'Missing value for scraper\'s icon'
    elif not is_english_input(scraper_info['scraper_name']) \
            or not is_english_input(scraper_info['scraper_true_labels']) \
            or not is_english_input(scraper_info['scraper_false_labels']):
        err += 'Input should be in the English language'
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


# This function returns a HTML for a user's profile
def user_page(request, username):
    from django.contrib.sessions.models import Session
    if request.method != 'GET':
        raise Http404("Permission denied")
    user = get_user_by_username(username)
    if user is None:
        raise Http404('User ' + username + ' does not exist')
    decoded_sessions = [s.get_decoded() for s in Session.objects.all()]
    logged_in_users = [int(s.get('_auth_user_id')) for s in decoded_sessions]
    logged_in = user.id in logged_in_users
    from claims.views import get_users_images_for_claims, get_users_details_for_comments, \
        get_user_img_and_rep
    user_claims, user_comments, user_tweets = list(), list(), list()
    claims = Claim.objects.filter(user=user.id)
    if len(claims) > 0:
        user_claims = list(get_users_images_for_claims(claims).items())
    comments = Comment.objects.filter(user=user.id)
    if len(comments) > 0:
        user_comments = list(get_users_details_for_comments(comments).items())
    tweets = Tweet.objects.filter(user=user.id)
    if len(tweets) > 0:
        user_tweets = list(get_users_details_for_comments(tweets).items())
    user_img, user_rep = get_user_img_and_rep(user.id)
    page = request.GET.get('page1')
    paginator = Paginator(user_claims, 4)
    page2 = request.GET.get('page2')
    paginator2 = Paginator(user_comments, 4)
    page3 = request.GET.get('page3')
    paginator3 = Paginator(user_tweets, 4)
    return render(request, 'users/user_page.html', {
        'user': user,
        'logged_in': logged_in,
        'user_claims': paginator.get_page(page),
        'user_comments': paginator2.get_page(page2),
        'user_tweets': paginator3.get_page(page3),
        'user_img': user_img,
        'user_rep': user_rep,
        'scrapers_ids': get_all_scrapers_ids_arr(),
        'true_labels': get_true_labels(username),
        'false_labels': get_false_labels(username),
        'scraper_url': get_scraper_url(username)
    })


# This function returns all true labels of the given scraper
def get_scraper_url(scraper_name):
    scraper = Scrapers.objects.filter(scraper_name=scraper_name)
    url = ''
    if len(scraper) > 0:
        url = scraper.first().scraper_url
    return url


# This function returns all true labels of the given scraper
def get_true_labels(scraper_name):
    scraper = Scrapers.objects.filter(scraper_name=scraper_name)
    true_labels = []
    if len(scraper) > 0:
        true_labels = scraper.first().true_labels.split(',')
    return true_labels


# This function returns all false labels of the given scraper
def get_false_labels(scraper_name):
    scraper = Scrapers.objects.filter(scraper_name=scraper_name)
    false_labels = []
    if len(scraper) > 0:
        false_labels = scraper.first().false_labels.split(',')
    return false_labels


# This function adds a true label to the scraper
def add_true_label_to_scraper(request):
    from claims.views import return_get_request_to_user
    if not request.user.is_superuser or request.method != 'POST':
        raise Http404("Permission denied")
    scraper_info = request.POST.dict()
    valid_scraper_label, err_msg = check_if_scraper_new_label_is_valid(scraper_info, True)
    if not valid_scraper_label:
        save_log_message(request.user.id, request.user.username,
                         'Adding a new label (T) for scraper. Error: ' + err_msg)
        raise Exception(err_msg)
    scraper = Scrapers.objects.filter(scraper_id=User.objects.filter(id=scraper_info['scraper_id']).first()).first()
    Scrapers.objects.filter(id=scraper.id).update(true_labels=scraper.true_labels +
                                                  ',' + scraper_info['scraper_label'])
    return user_page(return_get_request_to_user(request.user), scraper.scraper_name)


# This function deletes the specified true label from the scraper
def delete_true_label_from_scraper(request):
    from claims.views import return_get_request_to_user
    if not request.user.is_superuser or request.method != 'POST':
        raise Http404("Permission denied")
    scraper_info = request.POST.dict()
    valid_scraper_label, err_msg = check_if_scraper_label_delete_is_valid(scraper_info)
    if not valid_scraper_label:
        save_log_message(request.user.id, request.user.username,
                         'Deleting a label (T) from scraper. Error: ' + err_msg)
        raise Exception(err_msg)
    true_labels = request.POST.getlist('scraper_label[]')
    valid_true_labels, err_msg = check_if_scraper_labels_already_exist(scraper_info['scraper_id'], true_labels, True)
    if not valid_true_labels:
        save_log_message(request.user.id, request.user.username,
                         'Deleting a label (T) from scraper. Error: ' + err_msg)
        raise Exception(err_msg)
    scraper = Scrapers.objects.filter(scraper_id=User.objects.filter(id=scraper_info['scraper_id']).first()).first()
    new_scraper_true_labels = []
    for true_label in scraper.true_labels.split(','):
        if true_label not in true_labels:
            new_scraper_true_labels.append(true_label)
    Scrapers.objects.filter(id=scraper.id).update(true_labels=','.join(new_scraper_true_labels))
    return user_page(return_get_request_to_user(request.user), scraper.scraper_name)


# This function adds a false label to the scraper
def add_false_label_to_scraper(request):
    from claims.views import return_get_request_to_user
    if not request.user.is_superuser or request.method != 'POST':
        raise Http404("Permission denied")
    scraper_info = request.POST.dict()
    valid_scraper_label, err_msg = check_if_scraper_new_label_is_valid(scraper_info, False)
    if not valid_scraper_label:
        save_log_message(request.user.id, request.user.username,
                         'Adding a new label (F) for scraper. Error: ' + err_msg)
        raise Exception(err_msg)
    scraper = Scrapers.objects.filter(scraper_id=User.objects.filter(id=scraper_info['scraper_id']).first()).first()
    Scrapers.objects.filter(id=scraper.id).update(false_labels=scraper.false_labels +
                                                               ',' + scraper_info['scraper_label'])
    return user_page(return_get_request_to_user(request.user), scraper.scraper_name)


# This function deletes the specified false label from the scraper
def delete_false_label_from_scraper(request):
    from claims.views import return_get_request_to_user
    if not request.user.is_superuser or request.method != 'POST':
        raise Http404("Permission denied")
    scraper_info = request.POST.dict()
    valid_scraper_label, err_msg = check_if_scraper_label_delete_is_valid(scraper_info)
    if not valid_scraper_label:
        save_log_message(request.user.id, request.user.username,
                         'Deleting a label (F) from scraper. Error: ' + err_msg)
        raise Exception(err_msg)
    false_labels = request.POST.getlist('scraper_label[]')
    valid_false_labels, err_msg = check_if_scraper_labels_already_exist(scraper_info['scraper_id'], false_labels, False)
    if not valid_false_labels:
        save_log_message(request.user.id, request.user.username,
                         'Deleting a label (F) from scraper. Error: ' + err_msg)
        raise Exception(err_msg)
    scraper = Scrapers.objects.filter(scraper_id=User.objects.filter(id=scraper_info['scraper_id']).first()).first()
    new_scraper_false_labels = []
    for false_label in scraper.false_labels.split(','):
        if false_label not in false_labels:
            new_scraper_false_labels.append(false_label)
    Scrapers.objects.filter(id=scraper.id).update(false_labels=','.join(new_scraper_false_labels))
    return user_page(return_get_request_to_user(request.user), scraper.scraper_name)


# This function checks if a given scraper's info (for adding a new label) is valid,
# i.e. the info has all the fields with the correct format.
# The function returns true in case the info is valid, otherwise false and an error
def check_if_scraper_new_label_is_valid(scraper_info, add_label):
    from claims.views import is_english_input
    err = ''
    if 'scraper_id' not in scraper_info or not scraper_info['scraper_id']:
        err += 'Missing value for scraper id'
    elif 'scraper_label' not in scraper_info or not scraper_info['scraper_label']:
        err += 'Missing value for scraper label(s)'
    elif not is_english_input(scraper_info['scraper_label']):
        err += 'Input should be in the English language'
    elif len(User.objects.filter(id=scraper_info['scraper_id'])) == 0:
        err += 'Scraper with id ' + str(scraper_info['scraper_id']) + ' does not exist'
    elif add_label and any(scraper_info['scraper_label'].lower() == label
                           for label in Scrapers.objects.filter(scraper_id=User.objects.filter(id=scraper_info['scraper_id']).first()).first().true_labels.split(',')):
        err += 'Label ' + scraper_info['scraper_label'] + ' already belongs to scraper\'s true labels'
    elif not add_label and any(scraper_info['scraper_label'].lower() == label
                               for label in Scrapers.objects.filter(scraper_id=User.objects.filter(id=scraper_info['scraper_id']).first()).first().false_labels.split(',')):
        err += 'Label ' + scraper_info['scraper_label'] + ' already belongs to scraper\'s false labels'
    if len(err) > 0:
        return False, err
    return True, err


# This function checks if a given scraper's info (for deleting an existing label) is valid,
# i.e. the info has all the fields with the correct format.
# The function returns true in case the info is valid, otherwise false and an error
def check_if_scraper_label_delete_is_valid(scraper_info):
    err = ''
    if 'scraper_id' not in scraper_info or not scraper_info['scraper_id']:
        err += 'Missing value for scraper\'s id'
    elif 'scraper_label[]' not in scraper_info or not scraper_info['scraper_label[]']:
        err += 'Missing value for scraper\'s label(s)'
    elif len(User.objects.filter(id=scraper_info['scraper_id'])) == 0:
        err += 'Scraper with id ' + str(scraper_info['scraper_id']) + ' does not exist'
    if len(err) > 0:
        return False, err
    return True, err


# The function checks if all labels in labels_list are in scraper's labels
# The function returns true in case all all labels in labels_list are in scraper's labels, otherwise false and an error
def check_if_scraper_labels_already_exist(scraper_id, labels_list, label):
    err = ''
    if label:  # true label case
        scraper_true_labels_list = Scrapers.objects.filter(
            scraper_id=User.objects.filter(id=scraper_id).first()).first().true_labels.split(',')
        if not all(true_label in scraper_true_labels_list for true_label in labels_list):
            err += 'Label(s) does not(do not) belong to scraper\'s true labels'
    else:  # false label case
        scraper_false_labels_list = Scrapers.objects.filter(
            scraper_id=User.objects.filter(id=scraper_id).first()).first().false_labels.split(',')
        if not all(false_label in scraper_false_labels_list for false_label in labels_list):
            err += 'Label(s) does not(do not) belong to scraper\'s false labels'
    if len(err) > 0:
        return False, err
    return True, err

