from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.contrib.auth import logout, authenticate
from django.http import Http404, HttpRequest, QueryDict, HttpResponse
from django.shortcuts import render, get_object_or_404
from comments.models import Comment
from comments.views import add_comment
from django.contrib.auth.models import AnonymousUser
from logger.models import Logger
from users.models import Scrapers
from logger.views import save_log_message, check_duplicate_log_for_user
from users.views import check_if_user_exists_by_user_id, check_if_user_is_scraper
from .models import Claim, Merging_Suggestions
from django.conf import settings
import json


# This function adds a new claim to the website, may followed with a comment on it
def add_claim(request):
    if request.method != "POST":
        raise PermissionDenied
    if not request.user.is_authenticated:  # scraper case
        if not request.POST.get('username') or not request.POST.get('password') or not \
                authenticate(request, username=request.POST.get('username'), password=request.POST.get('password')):
            raise PermissionDenied
        request.user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
    claim_info = request.POST.dict()
    claim_info['user_id'] = request.user.id
    claim_info['is_superuser'] = request.user.is_superuser
    valid_claim, err_msg = check_if_claim_is_valid(claim_info)
    if not valid_claim:
        save_log_message(request.user.id, request.user.username,
                         'Adding a new claim. Error: ' + err_msg)
        return HttpResponse(json.dumps(err_msg), content_type='application/json', status=404)
    claim = Claim(
        user_id=claim_info['user_id'],
        claim=claim_info['claim'],
        category=claim_info['category'],
        tags=','.join([tag.strip() for tag in claim_info['tags'].split(',')]),
        authenticity_grade=50,
        image_src=claim_info['image_src']
    )
    claim.save()
    save_log_message(request.user.id, request.user.username,
                     'Adding a new claim', True)
    claim_info['claim_id'] = claim.id
    claim_info['validate_g_recaptcha'] = True
    request.POST = claim_info
    if claim_info['add_comment'] == 'true':
        response = add_comment(request)
        if response.status_code == 404:  # error case
            claim_id = str(claim.id)
            claim.delete()
            err_msg = response.content.decode('utf-8')
            save_log_message(request.user.id, request.user.username,
                             'Adding a new comment on claim with id ' + claim_id + '. Error: ' + err_msg +
                             '. This claim has been deleted because ' +
                             'the user does not succeed to add a new claim with a comment on it.')
            return HttpResponse(json.dumps(err_msg), content_type='application/json', status=404)
    check_for_similar_claims(claim)
    return view_claim(return_get_request_to_user(request.user), claim.id)


# This function checks if a given claim is valid, i.e. the claim has all the fields with the correct format.
# The function returns true in case the claim is valid, otherwise false and an error
def check_if_claim_is_valid(claim_info):
    err = ''
    validate_g_recaptcha = False
    if 'validate_g_recaptcha' in claim_info and claim_info['validate_g_recaptcha']:
        validate_g_recaptcha = True
    if 'tags' not in claim_info or not claim_info['tags']:
        claim_info['tags'] = ''
    if 'image_src' not in claim_info or not claim_info['image_src']:
        claim_info['image_src'] = static('claims/assets/images/claim_default_image.jpg')
    if 'user_id' not in claim_info or not claim_info['user_id']:
        err += 'Missing value for user id'
    elif not check_if_user_is_scraper(claim_info['user_id']) and not validate_g_recaptcha and \
            ('g_recaptcha_response' not in claim_info or not check_g_recaptcha_response(claim_info['g_recaptcha_response'])):
        err += 'Invalid Captcha'
    elif not check_if_input_format_is_valid(claim_info['tags']):
        err += 'Incorrect format for tags'
    elif 'is_superuser' not in claim_info:
        err += 'Missing value for user type'
    elif 'claim' not in claim_info or not claim_info['claim']:
        err += 'Missing value for claim'
    elif 'category' not in claim_info or not claim_info['category']:
        err += 'Missing value for category'
    elif 'add_comment' not in claim_info:
        err += 'Missing value for adding a comment option'
    elif not check_if_user_exists_by_user_id(claim_info['user_id']):
        err += 'User ' + str(claim_info['user_id']) + ' does not exist'
    elif len(Claim.objects.filter(claim=claim_info['claim'], user_id=claim_info['user_id'])) > 0:
        err += 'Claim already exists'
    elif not is_english_input(claim_info['claim']) or \
            not is_english_input(claim_info['category']) or \
            not is_english_input(claim_info['tags']):
        err += 'Input should be in the English language'
    elif (not claim_info['is_superuser']) and post_above_limit(claim_info['user_id']):
        err += 'You have exceeded the amount limit of adding new claims today'
    if len(err) > 0:
        return False, err
    return True, err


def check_g_recaptcha_response(user_recaptcha_response):
    import requests
    data = {
        'secret': settings.GOOGLE_RECAPTCHA_V2_SECRET_KEY,
        'response': user_recaptcha_response
    }
    r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
    result = r.json()
    return result['success']


# This function checks if given claim's tags are valid, i.e. the tags are in the correct format.
# The function returns true in case the claim's tags are valid, otherwise false
def check_if_input_format_is_valid(user_input):
    import string
    if user_input == '':
        return True
    if not all(user_inp.isdigit() or
               user_inp.isalpha() or
               user_inp.isspace() or
               user_inp == ',' or
               user_inp not in string.punctuation for user_inp in user_input):
        return False
    first_tag = True
    for user_inp in user_input.split(','):
        if not user_inp or user_inp.isspace():
            return False
        elif first_tag and user_inp[0].isspace():
            return False
        first_tag = False
        num_spaces = 0
        for char in user_inp:
            if char.isspace():
                num_spaces += 1
                if num_spaces == 2:
                    return False
            else:
                num_spaces = 0
    return True


# This function checks if a given user's input is valid, i.e. the input is in the English language.
# The function returns true in case the user's input is valid, otherwise false
def is_english_input(user_input):
    for char in user_input:
        if char.isalpha():
            try:
                char.encode(encoding='utf-8').decode('ascii')
            except UnicodeDecodeError:
                return False
    return True


# This function checks if a given user posted new claims above the maximum limit (per day).
# The function returns true in case the user exceeded the maximum limit, otherwise false
def post_above_limit(user_id):
    limit = 10
    from datetime import datetime
    return (not check_if_user_is_scraper(user_id)) and \
        len(Logger.objects.filter(date__date=datetime.today(),
                                  user_id=user_id,
                                  action__icontains='Adding a new claim')) >= limit


# This function edits a claim in the website
def edit_claim(request):
    if not request.user.is_authenticated or request.method != "POST":
        raise PermissionDenied
    new_claim_fields = request.POST.dict()
    new_claim_fields['user_id'] = request.user.id
    new_claim_fields['is_superuser'] = request.user.is_superuser
    valid_new_claim, err_msg = check_claim_new_fields(new_claim_fields)
    if not valid_new_claim:
        save_log_message(request.user.id, request.user.username,
                         'Editing a claim. Error: ' + err_msg)
        return HttpResponse(json.dumps(err_msg), content_type='application/json', status=404)
    claim = get_object_or_404(Claim, id=request.POST.get('claim_id'))
    Claim.objects.filter(id=claim.id).update(
        claim=new_claim_fields['claim'],
        category=new_claim_fields['category'],
        tags=','.join([tag.strip() for tag in new_claim_fields['tags'].split(',')]),
        image_src=new_claim_fields['image_src'])
    save_log_message(request.user.id, request.user.username,
                     'Editing a claim with id ' + str(request.POST.get('claim_id')), True)
    return view_claim(return_get_request_to_user(request.user), claim.id)


# This function checks if the given new fields for a claim are valid,
# i.e. the claim has all the fields with the correct format.
# The function returns true in case the claim's new fields are valid, otherwise false and an error
def check_claim_new_fields(new_claim_fields):
    from django.utils import timezone
    err = ''
    max_minutes_to_edit_claim = 10
    if 'tags' not in new_claim_fields or not new_claim_fields['tags']:
        new_claim_fields['tags'] = ''
    if 'image_src' not in new_claim_fields or not new_claim_fields['image_src']:
        new_claim_fields['image_src'] = static('claims/assets/images/claim_default_image.jpg')
    if not check_if_input_format_is_valid(new_claim_fields['tags']):
        err += 'Incorrect format for tags'
    elif 'user_id' not in new_claim_fields or not new_claim_fields['user_id']:
        err += 'Missing value for user id'
    elif 'is_superuser' not in new_claim_fields:
        err += 'Missing value for user type'
    elif 'claim_id' not in new_claim_fields or not new_claim_fields['claim_id']:
        err += 'Missing value for claim id'
    elif 'claim' not in new_claim_fields or not new_claim_fields['claim']:
        err += 'Missing value for claim'
    elif 'category' not in new_claim_fields or not new_claim_fields['category']:
        err += 'Missing value for category'
    elif not check_if_user_exists_by_user_id(new_claim_fields['user_id']):
        err += 'User with id ' + str(new_claim_fields['user_id']) + ' does not exist'
    elif len(Claim.objects.filter(id=new_claim_fields['claim_id'])) == 0:
        err += 'Claim ' + str(new_claim_fields['claim_id']) + ' does not exist'
    elif (not new_claim_fields['is_superuser']) and len(Claim.objects.filter(id=new_claim_fields['claim_id'],
                                                                             user_id=new_claim_fields['user_id'])) == 0:
        err += 'Claim does not belong to user with id ' + str(new_claim_fields['user_id'])
    elif len(Claim.objects.exclude(id=new_claim_fields['claim_id']).filter(claim=new_claim_fields['claim'],
                                                                           user_id=new_claim_fields['user_id'])) > 0:
        err += 'Claim already exists'
    elif (not new_claim_fields['is_superuser']) and (timezone.now() - Claim.objects.filter(id=new_claim_fields['claim_id']).first().timestamp).total_seconds() \
            / 60 > max_minutes_to_edit_claim:
        err += 'You can no longer edit your claim'
    elif not is_english_input(new_claim_fields['claim']) or \
            not is_english_input(new_claim_fields['category']) or \
            not is_english_input(new_claim_fields['tags']):
        err += 'Input should be in the English language'
    if len(err) > 0:
        return False, err
    return True, err


# This function deletes a claim from the website
def delete_claim(request):
    if not request.user.is_authenticated or request.method != "POST":
        raise PermissionDenied
    valid_delete_claim, err_msg = check_if_delete_claim_is_valid(request)
    if not valid_delete_claim:
        save_log_message(request.user.id, request.user.username,
                         'Deleting a claim. Error: ' + err_msg)
        return HttpResponse(json.dumps(err_msg), content_type='application/json', status=404)
    from users.views import update_reputation_for_user
    for comment in Comment.objects.filter(claim_id=request.POST.get('claim_id')):
        update_reputation_for_user(comment.user_id, False, comment.up_votes.count())
        update_reputation_for_user(comment.user_id, True, comment.down_votes.count())
    Claim.objects.filter(id=request.POST.get('claim_id')).delete()
    save_log_message(request.user.id, request.user.username,
                     'Deleting a claim with id ' + str(request.POST.get('claim_id')), True)
    return view_home(return_get_request_to_user(request.user))


# This function checks if the given new fields for a claim are valid,
# i.e. the claim has all the fields with the correct format.
# The function returns true in case the claim's new fields are valid, otherwise false and an error
def check_if_delete_claim_is_valid(request):
    err = ''
    if not request.POST.get('claim_id'):
        err += 'Missing value for claim id'
    elif len(Claim.objects.filter(id=request.POST.get('claim_id'))) == 0:
        err += 'Claim ' + str(request.user.id) + ' does not exist'
    elif not check_if_user_exists_by_user_id(request.user.id):
        err += 'User with id ' + str(request.user.id) + ' does not exist'
    elif not request.user.is_superuser and len(Claim.objects.filter(id=request.POST.get('claim_id'),
                                                                    user=request.user.id)) == 0:
        err += 'Claim ' + str(request.POST.get('claim_id')) + ' does not belong to user with id ' + \
               str(request.user.id)
    if len(err) > 0:
        return False, err
    return True, err


# This function reports a claim as spam
def report_spam(request):
    from django.contrib.auth.models import User
    from notifications.signals import notify
    if not request.user.is_authenticated or request.method != "POST":
        raise PermissionDenied
    valid_spam_report, err_msg = check_if_spam_report_is_valid(request)
    if not valid_spam_report:
        save_log_message(request.user.id, request.user.username,
                         'Reporting a claim as spam. Error: ' + err_msg)
        return HttpResponse(json.dumps(err_msg), content_type='application/json', status=404)
    save_log_message(request.user.id, request.user.username,
                     'Reporting a claim with id ' + str(request.POST.get('claim_id')) + ' as spam', True)
    superusers = User.objects.filter(is_superuser=True).exclude(id=request.user.id)
    notify.send(request.user, recipient=superusers, verb='reported claim https://wtfact.ise.bgu.ac.il/claim/' + str(request.POST.get('claim_id')) + ' as spam', target=Claim.objects.filter(id=request.POST.get('claim_id')).first())
    return view_claim(return_get_request_to_user(request.user), request.POST.get('claim_id'))


# This function checks if the given fields for reporting a claim as spam are valid,
# i.e. the fields are with the correct format.
# The function returns true in case the fields are valid, otherwise false and an error
def check_if_spam_report_is_valid(request):
    err = ''
    if not request.POST.get('claim_id'):
        err += 'Missing value for claim id'
    elif len(Claim.objects.filter(id=request.POST.get('claim_id'))) == 0:
        err += 'Claim ' + str(request.POST.get('claim_id')) + ' does not exist'
    elif not check_if_user_exists_by_user_id(request.user.id):
        err += 'User ' + str(request.user.id) + ' does not exist'
    elif check_duplicate_log_for_user(request.user.id, 'Reporting a claim with id ' + str(request.POST.get('claim_id')) + ' as spam'):
        err += 'You already reported this claim as spam'
    if len(err) > 0:
        return False, err
    return True, err


# This function saves all the user's claims (from the request) in the system
def download_claims(request):
    import csv
    if not request.user.is_superuser or request.method != "POST" or 'csv_file' not in request.FILES:
        raise PermissionDenied
    claims = request.FILES['csv_file'].read().decode('utf-8-sig')
    if [header.lower().strip() for header in claims.split('\n')[0].split(',')] != \
            ['claim', 'category', 'tags', 'image_src', 'add_comment',
             'title', 'description', 'url', 'verdict_date', 'label']:
        raise Http404("Error - invalid header file")
    reader = csv.DictReader(claims.splitlines())
    reader.fieldnames = [name.lower() for name in reader.fieldnames]
    for claim in reader:
        claim_info = {'claim': claim['claim'],
                      'category': claim['category'],
                      'tags': claim['tags'],
                      'image_src': claim['image_src'],
                      'add_comment': claim['add_comment'],
                      'title': claim['title'],
                      'description': claim['description'],
                      'url': claim['url'],
                      'verdict_date': claim['verdict_date'],
                      'label': claim['label'],
                      'validate_g_recaptcha': True}
        post_request = HttpRequest()
        post_request.method = 'POST'
        post_request.user = request.user
        query_dict = QueryDict('', mutable=True)
        query_dict.update(claim_info)
        post_request.POST = query_dict
        add_claim(post_request)
    return view_home(return_get_request_to_user(request.user))


# This function merges two claims that have been found as identical
def merging_claims(request):
    if not request.user.is_superuser or request.method != "POST":
        raise PermissionDenied
    from comments.views import update_authenticity_grade
    merge_claims_info = request.POST.copy()
    merge_claims_info['user_id'] = request.user.id
    merge_claims_info['is_superuser'] = request.user.is_superuser
    valid_merging, err_msg = check_if_suggestion_is_valid(merge_claims_info)
    if not valid_merging:
        save_log_message(request.user.id, request.user.username,
                         'Merging claims. Error: ' + err_msg)
        return HttpResponse(json.dumps(err_msg), content_type='application/json', status=404)
    suggestion = Merging_Suggestions.objects.filter(id=merge_claims_info['suggestion_id']).first()
    Comment.objects.filter(claim_id=suggestion.claim_to_merge_id).update(claim_id=suggestion.claim_id)
    update_authenticity_grade(suggestion.claim_id)
    Claim.objects.filter(id=suggestion.claim_to_merge_id).delete()
    save_log_message(request.user.id, request.user.username,
                     'Merging claims - claim with id ' + str(suggestion.claim_to_merge_id) +
                     ' and claim with id ' + str(suggestion.claim_id), True)
    return merging_claims_page(return_get_request_to_user(request.user))


# This function checks if the given fields for merging two claims are valid,
# i.e. the fields are with the correct format.
# The function returns true in case the fields are valid, otherwise false and an error
def check_if_suggestion_is_valid(merge_claims_info):
    err = ''
    if 'suggestion_id' not in merge_claims_info or not merge_claims_info['suggestion_id']:
        err += 'Missing value for suggestion id'
    elif 'user_id' not in merge_claims_info or not merge_claims_info['user_id']:
        err += 'Missing value for user id'
    elif 'is_superuser' not in merge_claims_info:
        err += 'Missing value for user type'
    elif len(Merging_Suggestions.objects.filter(id=merge_claims_info['suggestion_id'])) == 0:
        err += 'Suggestion ' + str(merge_claims_info['suggestion_id']) + ' does not exist'
    elif not check_if_user_exists_by_user_id(merge_claims_info['user_id']):
        err += 'User with id ' + str(merge_claims_info['user_id']) + ' does not exist'
    elif not merge_claims_info['is_superuser']:
        err += 'Permission Denied'
    if len(err) > 0:
        return False, err
    return True, err


# This function switch two claims that have been found as identical
def switching_claims(request):
    if not request.user.is_superuser or request.method != "POST":
        raise PermissionDenied
    switch_claims_info = request.POST.copy()
    switch_claims_info['user_id'] = request.user.id
    switch_claims_info['is_superuser'] = request.user.is_superuser
    valid_switching, err_msg = check_if_suggestion_is_valid(switch_claims_info)
    if not valid_switching:
        save_log_message(request.user.id, request.user.username,
                         'Switching claims. Error: ' + err_msg)
        return HttpResponse(json.dumps(err_msg), content_type='application/json', status=404)
    suggestion = Merging_Suggestions.objects.filter(id=switch_claims_info['suggestion_id']).first()
    Merging_Suggestions.objects.filter(id=suggestion.id).update(
        claim_id=suggestion.claim_to_merge_id,
        claim_to_merge_id=suggestion.claim_id)
    save_log_message(request.user.id, request.user.username,
                     'Switching claims - claim with id ' + str(suggestion.claim_id) +
                     ' and claim with id ' + str(suggestion.claim_to_merge_id), True)
    return merging_claims_page(return_get_request_to_user(request.user))


# This function deletes a suggestion for merging two claims
def delete_suggestion_for_merging_claims(request):
    if not request.user.is_superuser or request.method != "POST":
        raise PermissionDenied
    suggestion_to_delete = request.POST.copy()
    suggestion_to_delete['user_id'] = request.user.id
    suggestion_to_delete['is_superuser'] = request.user.is_superuser
    valid_suggestion_to_delete, err_msg = check_if_suggestion_is_valid(suggestion_to_delete)
    if not valid_suggestion_to_delete:
        save_log_message(request.user.id, request.user.username,
                         'Deleting a suggestion for merging claims. Error: ' + err_msg)
        return HttpResponse(json.dumps(err_msg), content_type='application/json', status=404)
    suggestion = Merging_Suggestions.objects.filter(id=suggestion_to_delete['suggestion_id']).first()
    claim_id = suggestion.claim_id
    claim_id_to_merge = suggestion.claim_to_merge_id
    Merging_Suggestions.objects.filter(id=suggestion_to_delete['suggestion_id']).delete()
    save_log_message(request.user.id, request.user.username,
                     'Deleting a suggestion for merging claims - claim with id ' + str(claim_id) +
                     ' with claim with id ' + str(claim_id_to_merge), True)
    return merging_claims_page(return_get_request_to_user(request.user))


# This function returns the home page of the website
@ensure_csrf_cookie
def view_home(request):
    if request.method != "GET":
        raise PermissionDenied
    from django.utils import timezone
    current_day = timezone.now()
    delta = current_day - timezone.timedelta(days=14)
    claims = Claim.objects.filter(timestamp__range=(delta, current_day))
    newest = get_different_user_claims(claims.order_by('-id'))
    most_commented = get_different_user_claims(sort_claims_by_comments(claims))
    most_controversial = get_different_user_claims(sort_claims_by_controversial(claims))
    return render(request, 'claims/index.html',
                  {'newest': newest,
                   'most_commented': most_commented,
                   'most_controversial': most_controversial})


def get_different_user_claims(claims):
    different_user_claims = {}
    back_up_claims, different_claims = [], []
    for claim in claims:
        if claim.user_id not in different_user_claims:
            different_user_claims[claim.user_id] = claim
        else:
            back_up_claims.append(claim)
    different_claims = list(different_user_claims.values())
    for i in range(4 - min(4, len(different_claims))):
        if len(back_up_claims) > i:
            different_claims.append(back_up_claims[i])
        else:
            break
    if len(different_claims) < 4:
        return different_claims
    return different_claims[0:4]


# This function returns the claims page of the website
@ensure_csrf_cookie
def view_claims(request):
    if request.method != "GET":
        raise PermissionDenied
    from django.core.paginator import Paginator
    claims = Claim.objects.all().order_by('-id')
    sort_method = request.GET.get('sort_method')
    if sort_method == 'Most controversial':
        claims = sort_claims_by_controversial()
    elif sort_method == 'Most commented':
        claims = sort_claims_by_comments()
    else:
        sort_method = 'Newest'
    page = request.GET.get('page')
    paginator = Paginator(claims, 24)
    return render(request, 'claims/claims.html', {'claims': paginator.get_page(page), 'sort_method': sort_method})


# This function sorts the claims by num of comments
def sort_claims_by_comments(claims=None):
    res = {}
    if not claims:
        claims = Claim.objects.all()
    for claim in claims:
        res[claim] = claim.num_of_true_comments() + claim.num_of_false_comments()
    return sorted(res, key=res.__getitem__, reverse=True)


# This function sorts the claims by controversial
def sort_claims_by_controversial(claims=None):
    if not claims:
        claims = Claim.objects.all()
    res = list(claims)
    return sorted(res, key=lambda x: abs(x.authenticity_grade-50))


# This function returns a claim page of a given claim id
# The function returns the claim page in case the claim is found, otherwise Http404
def view_claim(request, claim_id):
    claim = get_claim_by_id(claim_id)
    if claim is None:
        raise Http404('Error - claim ' + str(claim_id) + ' does not exist')
    elif request.method != "GET":
        raise PermissionDenied
    tweets = claim.get_tweets_for_claim()
    page = request.GET.get('tweets_page')
    from django.core.paginator import Paginator
    paginator = Paginator(tweets, 3)
    return render(request, 'claims/claim.html', {'claim': claim, 'tweets': paginator.get_page(page)})


# This function returns all the claims in the website
def get_all_claims():
    return Claim.objects.all()


# This function returns the newest claims in the website (up to 20 claims)
def get_newest_claims():
    result = Claim.objects.all().order_by('-id')
    if len(result) < 20:
        return result
    return result[0:20]


# This function returns a claim of a given claim's id
# The function returns the claim in case it is found, otherwise None
def get_claim_by_id(claim_id):
    result = Claim.objects.filter(id=claim_id)
    if len(result) > 0:
        return result[0]
    return None


# This function returns the category for a given claim's id
# The function returns claim's category in case it is found, otherwise None
def get_category_for_claim(claim_id):
    result = Claim.objects.filter(id=claim_id)
    if len(result) > 0:
        return result[0].category
    return None


# This function returns the tags for a given claim's id
# The function returns claim's tags in case they are found, otherwise None
def get_tags_for_claim(claim_id):
    result = Claim.objects.filter(id=claim_id)
    if len(result) > 0:
        return result[0].tags
    return None


# This function disconnects the user from the website
def logout_view(request):
    logout(request)
    request.session.flush()
    request.user = AnonymousUser()
    return view_home(request)


# This function return a HTML page for adding a new claim to the website
def add_claim_page(request):
    if not request.user.is_authenticated or request.method != 'GET':
        raise PermissionDenied
    return render(request, 'claims/add_claim.html')


# This function return a HTML page for exporting website claims to a csv file
def export_claims_page(request):
    if not request.user.is_superuser or request.method != 'GET':
        raise PermissionDenied
    return render(request, 'claims/export_claims.html', {'all_scrapers': Scrapers.objects.all()})


# This function return a HTML page for posting new claims\tweets to the website
def post_claims_tweets_page(request):
    if not request.user.is_authenticated or request.method != 'GET':
        raise PermissionDenied
    return render(request, 'claims/import_claims_tweets.html')


# This function return a HTML page for posting new claims\tweets to the website
def merging_claims_page(request):
    if not request.user.is_superuser or request.method != 'GET':
        raise PermissionDenied
    return render(request, 'claims/merging_claims_page.html', {'suggestions': Merging_Suggestions.objects.all()})


# This function returns about page
def about_page(request):
    return render(request, 'claims/about.html')


# This function returns 400 error page
def handler_400(request, exception):
    return render(request, 'claims/400.html', status=400)


# This function returns 403 error page
def handler_403(request, exception):
    return render(request, 'claims/403.html', status=403)


# This function returns 404 error page
def handler_404(request, exception):
    return render(request, 'claims/404.html', {'exception': exception}, status=404)


# This function returns 500 error page
def handler_500(request):
    return render(request, 'claims/500.html', status=500)


# This function returns a new GET request for a user
def return_get_request_to_user(user):
    request = HttpRequest()
    request.user = user
    request.stats_code = 200
    request.method = 'GET'
    return request


# This function add all similar claims for the given claim
def check_for_similar_claims(claim):
    from difflib import SequenceMatcher
    from claims.models import Merging_Suggestions
    for c in Claim.objects.exclude(id=claim.id):
        score = SequenceMatcher(None, claim.claim, c.claim).ratio()
        if score > 0.65:
            Merging_Suggestions.objects.create(claim=c, claim_to_merge=claim)


# def update_tags_for_all_claims_and_comments(request):
#     for claim in Claim.objects.all():
#         if claim.tags:
#             Claim.objects.filter(id=claim.id).update(tags=','.join(
#                 [tag for tag in claim.tags.split(',') if len(tag) > 1]))
#     for comment in Comment.objects.all():
#         if comment.tags:
#             Comment.objects.filter(id=comment.id).update(tags=','.join(
#                 [tag for tag in comment.tags.split(',') if len(tag) > 1]))
#     return view_home(request)
