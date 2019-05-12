from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.http import Http404, HttpResponse
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from notifications.models import Notification

from claims.models import Claim
from comments.models import Comment
from logger.views import save_log_message
from users.forms import ImageUploadForm
from users.models import Users_Images, Scrapers
from users.models import Users_Reputations
import json


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


def get_user_reputation(user_id):
    if not check_if_user_exists_by_user_id(user_id):
        err_msg = 'User with id ' + str(user_id) + ' does not exists'
        return HttpResponse(json.dumps(err_msg), content_type='application/json', status=404)
    user = User.objects.filter(id=user_id).first()
    user_rep = Users_Reputations.objects.filter(user=user)
    if len(user_rep) == 0:
        new_user_rep = Users_Reputations.objects.create(user=user)
        new_user_rep.save()
        user_rep = new_user_rep
    else:
        user_rep = user_rep.first()
    return user_rep.reputation


# This function adds all the scrapers as users to the website
def add_all_scrapers(request):
    from claims.views import view_home, return_get_request_to_user
    if not request.user.is_superuser or request.method != 'GET':
        raise PermissionDenied
    try:
        password = User.objects.make_random_password()
        # print(password)
        scraper_1 = User.objects.create_user(username='Snopes', password=password)
        scraper_1.save()
        scraper_1_img = Users_Images(user=scraper_1)
        scraper_1_img.save()
        scraper_1_rep = Users_Reputations(user=scraper_1)
        scraper_1_rep.save()
        true_labels = ['true', 'probably true', 'partly true', 'correct attribution', 'mostly true']
        false_labels = ['false', 'not true', 'mostly false', 'fiction', 'legend', 'scam', 'miscaptioned']
        scraper_1_details = Scrapers(scraper_name=scraper_1.username,
                                     scraper=scraper_1,
                                     true_labels=','.join(true_labels),
                                     false_labels=','.join(false_labels))
        scraper_1_details.save()

        password = User.objects.make_random_password()
        scraper_2 = User.objects.create_user(username='Polygraph', password=password)
        scraper_2.save()
        scraper_2_img = Users_Images(user=scraper_2)
        scraper_2_img.save()
        scraper_2_rep = Users_Reputations(user=scraper_2)
        scraper_2_rep.save()
        true_labels = ['true', 'partially true', 'likely true']
        false_labels = ['false', 'mostly false', 'highly misleading', 'misleading', 'likely false', 'partially false']
        scraper_2_details = Scrapers(scraper_name=scraper_2.username,
                                     scraper=scraper_2,
                                     true_labels=','.join(true_labels),
                                     false_labels=','.join(false_labels))
        scraper_2_details.save()

        password = User.objects.make_random_password()
        scraper_3 = User.objects.create_user(username='TruthOrFiction', password=password)
        scraper_3.save()
        scraper_3_img = Users_Images(user=scraper_3)
        scraper_3_img.save()
        scraper_3_rep = Users_Reputations(user=scraper_3)
        scraper_3_rep.save()
        true_labels = ['true', 'truth', 'truth!', 'mostly truth!', 'authorship confirmed!', 'correct attribution!', 'correctly attributed!']
        false_labels = ['false', 'not true', 'fiction', 'fiction!', 'mostly fiction!', 'reported fiction!',
                        'incorrect attribution!', 'misleading!', 'misattributed', 'decontextualized']
        scraper_3_details = Scrapers(scraper_name=scraper_3.username,
                                     scraper=scraper_3,
                                     true_labels=','.join(true_labels),
                                     false_labels=','.join(false_labels))
        scraper_3_details.save()

        password = User.objects.make_random_password()
        scraper_4 = User.objects.create_user(username='Politifact', password=password)
        scraper_4.save()
        scraper_4_img = Users_Images(user=scraper_4)
        scraper_4_img.save()
        scraper_4_rep = Users_Reputations(user=scraper_4)
        scraper_4_rep.save()
        true_labels = ['true', 'mostly true', 'no flip']
        false_labels = ['false', 'mostly false', 'full flop', 'pants on fire!']
        scraper_4_details = Scrapers(scraper_name=scraper_4.username,
                                     scraper=scraper_4,
                                     true_labels=','.join(true_labels),
                                     false_labels=','.join(false_labels))
        scraper_4_details.save()

        password = User.objects.make_random_password()
        scraper_5 = User.objects.create_user(username='GossipCop', password=password)
        scraper_5.save()
        scraper_5_img = Users_Images(user=scraper_5)
        scraper_5_img.save()
        scraper_5_rep = Users_Reputations(user=scraper_5)
        scraper_5_rep.save()
        true_labels = [str(i + 6) for i in range(5)]
        false_labels = [str(i) for i in range(5)]
        scraper_5_details = Scrapers(scraper_name=scraper_5.username,
                                     scraper=scraper_5,
                                     true_labels=','.join(true_labels),
                                     false_labels=','.join(false_labels))
        scraper_5_details.save()

        password = User.objects.make_random_password()
        scraper_6 = User.objects.create_user(username='ClimateFeedback', password=password)
        scraper_6.save()
        scraper_6_img = Users_Images(user=scraper_6)
        scraper_6_img.save()
        scraper_6_rep = Users_Reputations(user=scraper_6)
        scraper_6_rep.save()
        true_labels = ['true', 'accurate', 'mostly_correct', 'correct']
        false_labels = ['false', 'unsupported', 'incorrect', 'inaccurate', 'misleading', 'flawed_reasoning']
        scraper_6_details = Scrapers(scraper_name=scraper_6.username,
                                     scraper=scraper_6,
                                     true_labels=','.join(true_labels),
                                     false_labels=','.join(false_labels))
        scraper_6_details.save()

        password = User.objects.make_random_password()
        scraper_7 = User.objects.create_user(username='FactScan', password=password)
        scraper_7.save()
        scraper_7_img = Users_Images(user=scraper_7)
        scraper_7_img.save()
        scraper_7_rep = Users_Reputations(user=scraper_7)
        scraper_7_rep.save()
        true_labels = ['true']
        false_labels = ['false', 'misleading', 'farcical']
        scraper_7_details = Scrapers(scraper_name=scraper_7.username,
                                     scraper=scraper_7,
                                     true_labels=','.join(true_labels),
                                     false_labels=','.join(false_labels))
        scraper_7_details.save()

        password = User.objects.make_random_password()
        scraper_8 = User.objects.create_user(username='AfricaCheck', password=password)
        scraper_8.save()
        scraper_8_img = Users_Images(user=scraper_8)
        scraper_8_img.save()
        scraper_8_rep = Users_Reputations(user=scraper_8)
        scraper_8_rep.save()
        scraper_8_details = Scrapers(scraper_name=scraper_8.username, scraper=scraper_8)
        scraper_8_details.save()

        password = User.objects.make_random_password()
        scraper_9 = User.objects.create_user(username='CNN', password=password)
        scraper_9.save()
        scraper_9_img = Users_Images(user=scraper_9)
        scraper_9_img.save()
        scraper_9_rep = Users_Reputations(user=scraper_9)
        scraper_9_rep.save()
        scraper_9_details = Scrapers(scraper_name=scraper_9.username,
                                     scraper=scraper_9)
        scraper_9_details.save()
    except Exception:
        raise Http404("Error - scrapers already exist")
    return view_home(return_get_request_to_user(request.user))


# This function returns all the scrapers' ids
def get_all_scrapers_ids(request):
    if request.method != 'GET':
        raise PermissionDenied
    from django.http import JsonResponse
    scrapers = {}
    result = Scrapers.objects.all()
    for scraper in result:
        scrapers[scraper.scraper_name] = scraper.scraper.id
    return JsonResponse(scrapers)


# This function returns all the scrapers' ids in an array
def get_all_scrapers_ids_arr():
    all_scrapers_ids = []
    for scraper in Scrapers.objects.all():
        all_scrapers_ids.append(scraper.scraper.id)
    return all_scrapers_ids


# This function returns a random claim for each scraper in the system for testing (the scrapers)
def get_random_claims_from_scrapers(request):
    if not request.user.is_superuser or request.method != 'GET':
        raise PermissionDenied
    from django.http import JsonResponse
    claims = {}
    result = Scrapers.objects.all()
    from claims.models import Claim
    from comments.models import Comment
    for scraper in result:
        claim_comment = Comment.objects.all().filter(user=scraper.scraper.id).order_by('-id')
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
        raise PermissionDenied
    scraper_info = request.POST.dict()
    valid_scraper, err_msg = check_if_scraper_info_is_valid(scraper_info)
    if not valid_scraper:
        save_log_message(request.user.id, request.user.username,
                         'Adding a new scraper. Error: ' + err_msg)
        return HttpResponse(json.dumps(err_msg), content_type='application/json', status=404)
    true_labels = scraper_info['scraper_true_labels'].lower().split()
    if 'true' not in true_labels:
        true_labels.append('true')
    false_labels = scraper_info['scraper_false_labels'].lower().split()
    if 'false' not in false_labels:
        false_labels.append('false')
    new_scraper = User.objects.create_user(username=scraper_info['scraper_name'],
                                           password=scraper_info['scraper_password'])
    new_scraper.save()
    new_scraper_img = Users_Images(user=new_scraper)
    new_scraper_img.save()

    new_scraper_rep = Users_Reputations(user=new_scraper)
    new_scraper_rep.save()

    new_scraper_img_details = Scrapers(scraper_name=new_scraper.username,
                                       scraper=new_scraper,
                                       scraper_url=scraper_info['scraper_url'],
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
    from comments.views import is_valid_url
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
    elif 'scraper_url' not in scraper_info or not scraper_info['scraper_url'] \
            or not is_valid_url(scraper_info['scraper_url']):
        err += 'Invalid url'
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
        err_msg = 'User with id ' + str(user_id) + ' does not exist'
        return HttpResponse(json.dumps(err_msg), content_type='application/json', status=404)
    user = User.objects.filter(id=user_id).first()
    user_rep = Users_Reputations.objects.filter(user=user)
    if len(user_rep) == 0:  # user has no reputation
        new_user_rep = Users_Reputations(user=user)
        new_user_rep.save()
        reputation = 1
    else:
        reputation = user_rep.first().reputation
    if earn_points:
        reputation = min(100, reputation + num_of_points)
    else:
        reputation = max(1, reputation - num_of_points)
    Users_Reputations.objects.filter(user=user).update(reputation=reputation)


# This function returns a HTML for a user's profile
@ensure_csrf_cookie
def user_page(request, user_id):
    from django.contrib.sessions.models import Session
    if request.method != 'GET':
        raise PermissionDenied
    user = User.objects.filter(id=user_id)
    if len(user) == 0:
        raise Http404('Error - user with id ' + str(user_id) + ' does not exist')
    user = user.first()
    decoded_sessions = [s.get_decoded() for s in Session.objects.all()]
    logged_in_users = [s.get('_auth_user_id') for s in decoded_sessions]
    logged_in = str(user.id) in logged_in_users
    user_claims = Claim.objects.filter(user=user.id).order_by('-id')
    user_comments = Comment.objects.filter(user=user.id).order_by('-id')
    page = request.GET.get('page1')
    paginator = Paginator(user_claims, 4)
    page_2 = request.GET.get('page2')
    paginator_2 = Paginator(user_comments, 4)
    form = ImageUploadForm(initial={'user_id': user_id})
    return render(request, 'users/user_page.html', {
        'user': user,
        'logged_in': logged_in,
        'user_claims': paginator.get_page(page),
        'user_comments': paginator_2.get_page(page_2),
        'form': form
    })


# This function returns the url of the given scraper
def get_scraper_url(scraper_name):
    scraper = Scrapers.objects.filter(scraper_name=scraper_name)
    scraper_url = ''
    if len(scraper) > 0:
        scraper_url = scraper.first().scraper_url
    return scraper_url


# This function adds a true label to the scraper
def add_true_label_to_scraper(request):
    from claims.views import return_get_request_to_user
    if not request.user.is_superuser or request.method != 'POST':
        raise PermissionDenied
    scraper_info = request.POST.dict()
    valid_scraper_label, err_msg = check_if_scraper_new_label_is_valid(scraper_info, True)
    if not valid_scraper_label:
        save_log_message(request.user.id, request.user.username,
                         'Adding a new label (T) for scraper. Error: ' + err_msg)
        return HttpResponse(json.dumps(err_msg), content_type='application/json', status=404)
    scraper = Scrapers.objects.filter(scraper=User.objects.filter(id=scraper_info['scraper_id']).first()).first()
    true_labels = ''
    if scraper.true_labels:
        true_labels = scraper.true_labels + ','
    Scrapers.objects.filter(id=scraper.id).update(true_labels=true_labels +
                                                  scraper_info['scraper_label'])
    update_scrapers_comments_verdicts(scraper.scraper.id)
    save_log_message(request.user.id, request.user.username,
                     'Adding a new label (T) for scraper - ' + scraper.scraper_name)
    return user_page(return_get_request_to_user(request.user), scraper.scraper.id)


# This function deletes the specified true label from the scraper
def delete_true_label_from_scraper(request):
    from claims.views import return_get_request_to_user
    if not request.user.is_superuser or request.method != 'POST':
        raise PermissionDenied
    scraper_info = request.POST.dict()
    valid_scraper_label, err_msg = check_if_scraper_label_delete_is_valid(scraper_info)
    if not valid_scraper_label:
        save_log_message(request.user.id, request.user.username,
                         'Deleting a label (T) from scraper. Error: ' + err_msg)
        return HttpResponse(json.dumps(err_msg), content_type='application/json', status=404)
    true_labels = request.POST.getlist('scraper_label[]')
    valid_true_labels, err_msg = check_if_scraper_labels_already_exist(scraper_info['scraper_id'], true_labels, True)
    if not valid_true_labels:
        save_log_message(request.user.id, request.user.username,
                         'Deleting a label (T) from scraper. Error: ' + err_msg)
        return HttpResponse(json.dumps(err_msg), content_type='application/json', status=404)
    scraper = Scrapers.objects.filter(scraper=User.objects.filter(id=scraper_info['scraper_id']).first()).first()
    new_scraper_true_labels = []
    for true_label in scraper.true_labels.split(','):
        if true_label not in true_labels:
            new_scraper_true_labels.append(true_label)
    Scrapers.objects.filter(id=scraper.id).update(true_labels=','.join(new_scraper_true_labels))
    update_scrapers_comments_verdicts(scraper.scraper.id)
    save_log_message(request.user.id, request.user.username,
                     'Deleting a label (T) from scraper - ' + scraper.scraper_name)
    return user_page(return_get_request_to_user(request.user), scraper.scraper.id)


# This function adds a false label to the scraper
def add_false_label_to_scraper(request):
    from claims.views import return_get_request_to_user
    if not request.user.is_superuser or request.method != 'POST':
        raise PermissionDenied
    scraper_info = request.POST.dict()
    valid_scraper_label, err_msg = check_if_scraper_new_label_is_valid(scraper_info, False)
    if not valid_scraper_label:
        save_log_message(request.user.id, request.user.username,
                         'Adding a new label (F) for scraper. Error: ' + err_msg)
        return HttpResponse(json.dumps(err_msg), content_type='application/json', status=404)
    scraper = Scrapers.objects.filter(scraper=User.objects.filter(id=scraper_info['scraper_id']).first()).first()
    false_labels = ''
    if scraper.false_labels:
        false_labels = scraper.false_labels + ','
    Scrapers.objects.filter(id=scraper.id).update(false_labels=false_labels +
                                                  scraper_info['scraper_label'])
    update_scrapers_comments_verdicts(scraper.scraper.id)
    save_log_message(request.user.id, request.user.username,
                     'Adding a new label (F) for scraper - ' + scraper.scraper_name)
    return user_page(return_get_request_to_user(request.user), scraper.scraper.id)


# This function deletes the specified false label from the scraper
def delete_false_label_from_scraper(request):
    from claims.views import return_get_request_to_user
    if not request.user.is_superuser or request.method != 'POST':
        raise PermissionDenied
    scraper_info = request.POST.dict()
    valid_scraper_label, err_msg = check_if_scraper_label_delete_is_valid(scraper_info)
    if not valid_scraper_label:
        save_log_message(request.user.id, request.user.username,
                         'Deleting a label (F) from scraper. Error: ' + err_msg)
        return HttpResponse(json.dumps(err_msg), content_type='application/json', status=404)
    false_labels = request.POST.getlist('scraper_label[]')
    valid_false_labels, err_msg = check_if_scraper_labels_already_exist(scraper_info['scraper_id'], false_labels, False)
    if not valid_false_labels:
        save_log_message(request.user.id, request.user.username,
                         'Deleting a label (F) from scraper. Error: ' + err_msg)
        return HttpResponse(json.dumps(err_msg), content_type='application/json', status=404)
    scraper = Scrapers.objects.filter(scraper=User.objects.filter(id=scraper_info['scraper_id']).first()).first()
    new_scraper_false_labels = []
    for false_label in scraper.false_labels.split(','):
        if false_label not in false_labels:
            new_scraper_false_labels.append(false_label)
    Scrapers.objects.filter(id=scraper.id).update(false_labels=','.join(new_scraper_false_labels))
    update_scrapers_comments_verdicts(scraper.scraper.id)
    save_log_message(request.user.id, request.user.username,
                     'Deleting a label (F) from scraper - ' + scraper.scraper_name)
    return user_page(return_get_request_to_user(request.user), scraper.scraper.id)


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
                           for label in Scrapers.objects.filter(scraper=User.objects.filter(id=scraper_info['scraper_id']).first()).first().true_labels.split(',')):
        err += 'Label ' + scraper_info['scraper_label'] + ' already belongs to scraper\'s true labels'
    elif not add_label and any(scraper_info['scraper_label'].lower() == label
                               for label in Scrapers.objects.filter(scraper=User.objects.filter(id=scraper_info['scraper_id']).first()).first().false_labels.split(',')):
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
            scraper=User.objects.filter(id=scraper_id).first()).first().true_labels.split(',')
        if not all(true_label in scraper_true_labels_list for true_label in labels_list):
            err += 'Label(s) does not(do not) belong to scraper\'s true labels'
    else:  # false label case
        scraper_false_labels_list = Scrapers.objects.filter(
            scraper=User.objects.filter(id=scraper_id).first()).first().false_labels.split(',')
        if not all(false_label in scraper_false_labels_list for false_label in labels_list):
            err += 'Label(s) does not(do not) belong to scraper\'s false labels'
    if len(err) > 0:
        return False, err
    return True, err


# This function updates scrapers comments verdicts after scrapers labels were updated
def update_scrapers_comments_verdicts(scraper_id):
    if not check_if_user_exists_by_user_id(scraper_id):
        err_msg = 'Scraper with id ' + str(scraper_id) + ' does not exists'
        return HttpResponse(json.dumps(err_msg), content_type='application/json', status=404)
    scraper = Scrapers.objects.filter(scraper=User.objects.filter(id=scraper_id).first()).first()
    for comment in Comment.objects.filter(user=scraper_id):
        label = comment.label.lower().strip()
        if label in scraper.true_labels:
            Comment.objects.filter(id=comment.id).update(system_label='True')
        elif label in scraper.false_labels:
            Comment.objects.filter(id=comment.id).update(system_label='False')
        else:
            Comment.objects.filter(id=comment.id).update(system_label='Unknown')


# This function checks if a given user is a scraper
def check_if_user_is_scraper(user_id):
    user = User.objects.filter(id=user_id)
    if len(user) == 0:
        return False
    user = user.first()
    return len(Scrapers.objects.filter(scraper=user)) > 0


# This function uploads an image for a user
def upload_user_img(request):
    if not request.user.is_authenticated or request.method != "POST":
        raise PermissionDenied
    from claims.views import return_get_request_to_user
    user_id = request.POST.get('user_id')
    file = request.FILES.get('profile_img')
    user = User.objects.filter(id=user_id).first()
    user_img = Users_Images.objects.filter(user=user).first()
    form = ImageUploadForm(request.POST,
                           request.FILES,
                           instance=user_img)
    if form.is_valid():
        import os
        if os.path.exists("media/images/{}".format(user_id)):
            import shutil
            shutil.rmtree("media/images/{}".format(user_id))
        user_and_img = form.save(commit=False)
        user_and_img.user = user
        user_and_img.profile_img = file
        user_and_img.save()
    return user_page(return_get_request_to_user(request.user), user_id)


# This function return an HTML page for adding a new scraper
def notifications_page(request):
    return render(request, 'users/notifications.html')


# This function marks user's notification as read
def read_notification(request):
    from claims.views import return_get_request_to_user
    if not request.user.is_authenticated or request.method != 'POST':
        raise PermissionDenied
    notification_info = request.POST.dict()
    notification_info["user_id"] = request.user.id
    valid_notification, err_msg = check_if_notification_is_valid(notification_info)
    if not valid_notification:
        save_log_message(request.user.id, request.user.username,
                         'Marking notification as read. Error: ' + err_msg)
        return HttpResponse(json.dumps(err_msg), content_type='application/json', status=404)
    Notification.objects.filter(id=notification_info["notification_id"]).mark_all_as_read()
    save_log_message(request.user.id, request.user.username,
                     'Marking notification with id ' + str(notification_info["notification_id"]) + ' as read', True)
    return notifications_page(return_get_request_to_user(request.user))


# This function deletes user's notification
def delete_notification(request):
    from claims.views import return_get_request_to_user
    if not request.user.is_authenticated or request.method != 'POST':
        raise PermissionDenied
    notification_info = request.POST.dict()
    notification_info["user_id"] = request.user.id
    valid_notification, err_msg = check_if_notification_is_valid(notification_info)
    if not valid_notification:
        save_log_message(request.user.id, request.user.username,
                         'Deleteing notification. Error: ' + err_msg)
        return HttpResponse(json.dumps(err_msg), content_type='application/json', status=404)
    Notification.objects.filter(id=notification_info["notification_id"]).delete()
    save_log_message(request.user.id, request.user.username,
                     'Deleting notification with id ' + str(notification_info["notification_id"]), True)
    return notifications_page(return_get_request_to_user(request.user))


# This function checks if a given notification's info is valid,
# i.e. the info has all the fields with the correct format.
# The function returns true in case the info is valid, otherwise false and an error
def check_if_notification_is_valid(notification_info):
    err = ''
    if 'notification_id' not in notification_info or not notification_info['notification_id']:
        err += 'Missing value for notification id'
    elif 'user_id' not in notification_info or not notification_info['user_id']:
        err += 'Missing value for user id'
    elif len(Notification.objects.filter(id=notification_info['notification_id'])) == 0:
        err += 'Notification ' + str(notification_info['notification_id']) + ' does not exist'
    elif not check_if_user_exists_by_user_id(notification_info['user_id']):
        err += 'User ' + str(notification_info['notification_id']) + ' does not exist'
    elif len(Notification.objects.filter(id=notification_info['notification_id'], recipient=User.objects.filter(id=notification_info['user_id']).first())) == 0:
        err += 'Notification ' + str(notification_info['notification_id']) + ' does not belong to user with id ' + \
               str(notification_info['user_id'])
    if len(err) > 0:
        return False, err
    return True, err
