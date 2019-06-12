from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from comments.models import Comment
from claims.models import Claim
from django.http import HttpResponse
from logger.views import save_log_message
from users.views import check_if_user_exists_by_user_id, get_all_scrapers_ids_arr, \
    get_user_reputation, check_if_user_is_scraper
from datetime import datetime
from django.utils import timezone
import requests
import json
import math
import csv


# This function takes care of a request to add a new comment to a claim in the website
def add_comment(request):
    from claims.views import view_claim, return_get_request_to_user
    if not request.user.is_authenticated or request.method != "POST":
        raise PermissionDenied
    comment_info = request.POST.copy()
    comment_info['user_id'] = request.user.id
    comment_info['is_superuser'] = request.user.is_superuser
    valid_comment, err_msg = check_if_comment_is_valid(comment_info)
    if not valid_comment:
        save_log_message(request.user.id, request.user.username,
                         'Adding a new comment on claim. Error: ' + err_msg)
        return HttpResponse(json.dumps(err_msg), content_type='application/json', status=404)
    build_comment(comment_info['claim_id'],
                  comment_info['user_id'],
                  comment_info['title'],
                  comment_info['description'],
                  comment_info['url'],
                  comment_info['tags'],
                  comment_info['verdict_date'],
                  comment_info['label'])
    save_log_message(request.user.id, request.user.username,
                     'Adding a new comment on claim with id ' + str(request.POST.get("claim_id")), True)
    user = Claim.objects.filter(id=comment_info['claim_id']).first().user
    from django.conf import settings
    if user.id != comment_info['user_id'] and (not settings.DEBUG):
        from notifications.signals import notify
        notify.send(request.user, recipient=user, verb='commented on your claim https://wtfact.ise.bgu.ac.il/claim/' + str(comment_info['claim_id']), target=Claim.objects.filter(id=comment_info['claim_id']).first())
    return view_claim(return_get_request_to_user(request.user), request.POST.get('claim_id'))


# This function adds a new comment to a claim in the website
def build_comment(claim_id, user_id, title, description, url, tags, verdict_date, label):
    comment = Comment(
        claim_id=claim_id,
        user_id=user_id,
        title=title,
        description=description,
        url=url,
        tags=','.join([tag.strip() for tag in tags.split(',')]),
        verdict_date=datetime.strptime(verdict_date, '%d/%m/%Y'),
        label=label,
        system_label=get_system_label_to_comment(label, user_id),
    )
    comment.save()
    update_authenticity_grade(comment.claim_id)


# This function checks if a given comment is valid, i.e. the comment has all the fields with the correct format.
# The function returns true in case the comment is valid, otherwise false and an error
def check_if_comment_is_valid(comment_info):
    from claims.views import check_g_recaptcha_response, check_if_input_format_is_valid, is_english_input
    max_comments = 5
    err = ''
    validate_g_recaptcha = False
    if 'validate_g_recaptcha' in comment_info and comment_info['validate_g_recaptcha']:
        validate_g_recaptcha = True
    if 'tags' not in comment_info or not comment_info['tags']:
        comment_info['tags'] = ''
    if 'user_id' not in comment_info or not comment_info['user_id']:
        err += 'Missing value for user id'
    elif not check_if_user_is_scraper(comment_info['user_id']) and not validate_g_recaptcha and \
            ('g_recaptcha_response' not in comment_info or not check_g_recaptcha_response(comment_info['g_recaptcha_response'])):
        err += 'Invalid Captcha'
    elif not check_if_input_format_is_valid(comment_info['tags']):
        err += 'Incorrect format for tags'
    elif 'is_superuser' not in comment_info:
        err += 'Missing value for user type'
    elif 'claim_id' not in comment_info or not comment_info['claim_id']:
        err += 'Missing value for claim id'
    elif 'title' not in comment_info or not comment_info['title']:
        err += 'Missing value for title'
    elif 'description' not in comment_info or not comment_info['description']:
        err += 'Missing value for description'
    elif 'url' not in comment_info or not comment_info['url']:
        err += 'Missing value for url'
    elif not is_valid_url(comment_info['url']):
        err += 'Invalid value for url'
    elif 'verdict_date' not in comment_info or not comment_info['verdict_date']:
        err += 'Missing value for verdict date'
    elif 'label' not in comment_info or not comment_info['label']:
        err += 'Missing value for label'
    elif len(Claim.objects.filter(id=comment_info['claim_id'])) == 0:
        err += 'Claim ' + str(comment_info['claim_id']) + ' does not exist'
    elif not check_if_user_exists_by_user_id(comment_info['user_id']):
        err += 'User with id ' + str(comment_info['user_id']) + ' does not exist'
    elif (not comment_info['is_superuser']) and len(Comment.objects.filter(claim_id=comment_info['claim_id'],
                                                                           user_id=comment_info['user_id'])) >= \
            max_comments:
        err += 'Maximum number of comments per claim is ' + str(max_comments)
    elif not is_english_input(comment_info['title']) or \
            not is_english_input(comment_info['description']) or \
            not is_english_input(comment_info['tags']):
        err += 'Input should be in the English language'
    else:
        err = convert_date_format(comment_info, 'verdict_date')
    if len(err) > 0:
        return False, err
    return True, err


# This function checks if a given url is valid
def is_valid_url(url):
    try:
        request = requests.get(url)
        return request.status_code == 200
    except Exception:
        return False


# This function converts a date field in a dict from %Y-%m-%d format to the system format which is %d/%m/%Y
# in case the date has %Y-%m-%d format.
# In addition, this function checks if the date is in the correct format according to the system format.
# In case that the date is not valid, it returns an error.
def convert_date_format(dict_info, date):
    err = ''
    if '-' in dict_info[date]:
        try:
            dict_info[date] = datetime.strptime(dict_info[date], '%Y-%m-%d').strftime('%d/%m/%Y')
        except ValueError:
            err += 'Date ' + dict_info[date] + ' is invalid'
    if len(err) == 0 and not is_valid_verdict_date(dict_info[date]):
        err += 'Date ' + dict_info[date] + ' is invalid'
    return err


# This function checks if the verdict date of a comment is valid
# The function returns true in case the verdict date is valid, otherwise false
def is_valid_verdict_date(verdict_date):
    try:
        verdict_datetime = datetime.strptime(verdict_date, "%d/%m/%Y")
        return datetime.today() >= verdict_datetime
    except ValueError:
        return False


# This function checks a comment's label and returns a basic classification for it.
# for user- 'True', 'False', 'Unknown'
# for scraper- based on dicts for true and false labels for each scraper.
def get_system_label_to_comment(comment_label, user_id):
    from users.models import Scrapers, User
    scraper = Scrapers.objects.filter(scraper_id=User.objects.filter(id=user_id).first())
    if len(scraper) == 0:
        if comment_label == 'True' or comment_label == 'False':
            return comment_label
        return 'Unknown'
    label = comment_label.lower().strip()
    scraper = scraper.first()
    if label in scraper.true_labels.split(','):
        return 'True'
    elif label in scraper.false_labels.split(','):
        return 'False'
    else:
        return 'Unknown'


# This function edits a comment in the website
def edit_comment(request):
    from claims.views import return_get_request_to_user
    if not request.user.is_authenticated or request.method != "POST":
        raise PermissionDenied
    from claims.views import view_claim
    new_comment_fields = request.POST.dict()
    new_comment_fields['user_id'] = request.user.id
    new_comment_fields['is_superuser'] = request.user.is_superuser
    valid_new_comment, err_msg = check_comment_new_fields(new_comment_fields)
    if not valid_new_comment:
        save_log_message(request.user.id, request.user.username,
                         'Editing a comment. Error: ' + err_msg)
        return HttpResponse(json.dumps(err_msg), content_type='application/json', status=404)
    Comment.objects.filter(id=new_comment_fields['comment_id']).update(
        title=new_comment_fields['comment_title'],
        description=new_comment_fields['comment_description'],
        url=new_comment_fields['comment_reference'],
        tags=','.join([tag.strip() for tag in new_comment_fields['comment_tags'].split(',')]),
        verdict_date=datetime.strptime(new_comment_fields['comment_verdict_date'], '%d/%m/%Y'),
        system_label=new_comment_fields['comment_label'])
    claim_id = Comment.objects.filter(id=new_comment_fields['comment_id']).first().claim_id
    update_authenticity_grade(claim_id)
    save_log_message(request.user.id, request.user.username,
                     'Editing a comment with id ' + str(request.POST.get('comment_id')), True)
    return view_claim(return_get_request_to_user(request.user), claim_id)


# This function checks if the given new fields for a comment are valid,
# i.e. the comment has all the fields with the correct format.
# The function returns true in case the comment's new fields are valid, otherwise false and an error
def check_comment_new_fields(new_comment_fields):
    from claims.views import check_if_input_format_is_valid, is_english_input
    err = ''
    max_minutes_to_edit_comment = 10
    if 'comment_tags' not in new_comment_fields or not new_comment_fields['comment_tags']:
        new_comment_fields['comment_tags'] = ''
    if not check_if_input_format_is_valid(new_comment_fields['comment_tags']):
        err += 'Incorrect format for tags'
    elif 'user_id' not in new_comment_fields or not new_comment_fields['user_id']:
        err += 'Missing value for user id'
    elif 'is_superuser' not in new_comment_fields:
        err += 'Missing value for user type'
    elif 'comment_id' not in new_comment_fields or not new_comment_fields['comment_id']:
        err += 'Missing value for comment id'
    elif 'comment_title' not in new_comment_fields or not new_comment_fields['comment_title']:
        err += 'Missing value for comment title'
    elif 'comment_description' not in new_comment_fields or not new_comment_fields['comment_description']:
        err += 'Missing value for comment description'
    elif 'comment_verdict_date' not in new_comment_fields or not new_comment_fields['comment_verdict_date']:
        err += 'Missing value for comment verdict date'
    elif 'comment_reference' not in new_comment_fields or not new_comment_fields['comment_reference']:
        err += 'Missing value for comment url'
    elif not is_valid_url(new_comment_fields['comment_reference']):
        err += 'Invalid value for comment url'
    elif 'comment_label' not in new_comment_fields or not new_comment_fields['comment_label']:
        err += 'Missing value for comment label'
    elif not check_if_user_exists_by_user_id(new_comment_fields['user_id']):
        err += 'User with id ' + str(new_comment_fields['user_id']) + ' does not exist'
    elif len(Comment.objects.filter(id=new_comment_fields['comment_id'])) == 0:
        err += 'Comment ' + str(new_comment_fields['comment_id']) + ' does not exist'
    elif (not new_comment_fields['is_superuser']) and len(Comment.objects.filter(id=new_comment_fields['comment_id'], user_id=new_comment_fields['user_id'])) == 0:
        err += 'Comment ' + str(new_comment_fields['comment_id']) + ' does not belong to user with id ' + \
               str(new_comment_fields['user_id'])
    elif (not new_comment_fields['is_superuser']) and (timezone.now() - Comment.objects.filter(id=new_comment_fields['comment_id']).first().timestamp).total_seconds() \
            / 60 > max_minutes_to_edit_comment:
        err += 'You can no longer edit your comment'
    elif not is_english_input(new_comment_fields['comment_title']) or \
            not is_english_input(new_comment_fields['comment_description']) or \
            not is_english_input(new_comment_fields['comment_tags']):
        err += 'Input should be in the English language'
    else:
        err = convert_date_format(new_comment_fields, 'comment_verdict_date')
    if len(err) > 0:
        return False, err
    return True, err


# This function deletes a comment from the website
def delete_comment(request):
    from claims.views import return_get_request_to_user
    if not request.user.is_authenticated or request.method != "POST":
        raise PermissionDenied
    from claims.views import view_claim
    from users.views import update_reputation_for_user
    valid_delete_claim, err_msg = check_if_delete_comment_is_valid(request)
    if not valid_delete_claim:
        save_log_message(request.user.id, request.user.username,
                         'Deleting a comment. Error: ' + err_msg)
        return HttpResponse(json.dumps(err_msg), content_type='application/json', status=404)
    comment = get_object_or_404(Comment, id=request.POST.get('comment_id'))
    claim_id = comment.claim_id
    update_reputation_for_user(comment.user_id, False, comment.up_votes.count())
    update_reputation_for_user(comment.user_id, True, comment.down_votes.count())
    Comment.objects.filter(id=request.POST.get('comment_id')).delete()
    save_log_message(request.user.id, request.user.username,
                     'Deleting a comment with id ' + str(request.POST.get('comment_id')), True)
    update_authenticity_grade(claim_id)
    return view_claim(return_get_request_to_user(request.user), claim_id)


# This function checks if the given fields for deleting a claim are valid,
# i.e. the request has all the fields with the correct format.
# The function returns true in case the given fields are valid, otherwise false and an error
def check_if_delete_comment_is_valid(request):
    err = ''
    if not request.POST.get('comment_id'):
        err += 'Missing value for comment id'
    elif len(Comment.objects.filter(id=request.POST.get('comment_id'))) == 0:
        err += 'Comment ' + str(request.user.id) + ' does not exist'
    elif not check_if_user_exists_by_user_id(request.user.id):
        err += 'User with id ' + str(request.user.id) + ' does not exist'
    elif not request.user.is_superuser and len(Comment.objects.filter(id=request.POST.get('comment_id'), user=request.user.id)) == 0:
        err += 'Comment ' + str(request.POST.get('comment_id')) + ' does not belong to user with id ' + \
               str(request.user.id)
    if len(err) > 0:
        return False, err
    return True, err


# This function increases a comment's vote by 1
def up_vote(request):
    from claims.views import return_get_request_to_user
    if not request.user.is_authenticated or request.method != "POST":
        err_msg = "Permission denied - you must sign in in order to vote on a comment"
        return HttpResponse(json.dumps(err_msg), content_type='application/json', status=404)
    from claims.views import view_claim
    from users.views import update_reputation_for_user
    vote_fields = request.POST.dict()
    vote_fields['user_id'] = request.user.id
    valid_vote, err_msg = check_if_vote_is_valid(vote_fields)
    if not valid_vote:
        save_log_message(request.user.id, request.user.username,
                         'Up voting a comment. Error: ' + err_msg)
        return HttpResponse(json.dumps(err_msg), content_type='application/json', status=404)
    comment = get_object_or_404(Comment, id=request.POST.get('comment_id'))
    if comment.up_votes.filter(id=request.user.id).exists():
        comment.up_votes.remove(request.user.id)
        update_reputation_for_user(comment.user_id, False, 1)
    else:
        comment.up_votes.add(request.user.id)
        update_reputation_for_user(comment.user_id, True, 1)
        if comment.down_votes.filter(id=request.user.id).exists():
            comment.down_votes.remove(request.user.id)
            update_reputation_for_user(comment.user_id, True, 1)
    save_log_message(request.user.id, request.user.username, 'Up voting a comment with id '
                     + str(request.POST.get('comment_id')), True)
    update_authenticity_grade(comment.claim_id)
    return view_claim(return_get_request_to_user(request.user), comment.claim_id)


# This function decreases a comment's vote by 1
def down_vote(request):
    if not request.user.is_authenticated or request.method != "POST":
        err_msg = "Permission denied - you must sign in in order to vote on a comment"
        return HttpResponse(json.dumps(err_msg), content_type='application/json', status=404)
    from claims.views import view_claim, return_get_request_to_user
    from users.views import update_reputation_for_user
    vote_fields = request.POST.dict()
    vote_fields['user_id'] = request.user.id
    valid_vote, err_msg = check_if_vote_is_valid(vote_fields)
    if not valid_vote:
        save_log_message(request.user.id, request.user.username,
                         'Down voting a comment. Error: ' + err_msg)
        return HttpResponse(json.dumps(err_msg), content_type='application/json', status=404)
    comment = get_object_or_404(Comment, id=request.POST.get('comment_id'))
    if comment.down_votes.filter(id=request.user.id).exists():
        comment.down_votes.remove(request.user.id)
        update_reputation_for_user(comment.user_id, True, 1)
    else:
        comment.down_votes.add(request.user.id)
        update_reputation_for_user(comment.user_id, False, 1)
        if comment.up_votes.filter(id=request.user.id).exists():
            comment.up_votes.remove(request.user.id)
            update_reputation_for_user(comment.user_id, False, 1)
    save_log_message(request.user.id, request.user.username,
                     'Down voting a comment with id ' + str(request.POST.get('comment_id')), True)
    update_authenticity_grade(comment.claim_id)
    return view_claim(return_get_request_to_user(request.user), comment.claim_id)


# This function checks if a given vote for a comment is valid, i.e. the vote has all the fields with the correct format.
# The function returns true in case the vote is valid, otherwise false and an error
def check_if_vote_is_valid(vote_fields):
    err = ''
    max_minutes_to_vote_comment = 10
    if 'user_id' not in vote_fields or not vote_fields['user_id']:
        err += 'Missing value for user id'
    elif not check_if_user_exists_by_user_id(vote_fields['user_id']):
        err += 'User with id ' + str(vote_fields['user_id']) + ' does not exist'
    elif 'comment_id' not in vote_fields or not vote_fields['comment_id']:
        err += 'Missing value for comment id'
    elif len(Comment.objects.filter(id=vote_fields['comment_id'])) == 0:
        err += 'Comment ' + str(vote_fields['comment_id']) + ' does not exist'
    elif (timezone.now() - Comment.objects.filter(id=vote_fields['comment_id']).first().timestamp).total_seconds() \
             / 60 <= max_minutes_to_vote_comment:
        err += 'You can not vote this comment yet. This comment has just been added, ' \
               'therefore you will be able to vote on it in a few minutes.'
    if len(err) > 0:
        return False, err
    return True, err


# This function returns a csv which contains all the details of the claims in the website
def export_to_csv(request):
    if not request.user.is_superuser or request.method != "POST":
        save_log_message(request.user.id, request.user.username,
                         'Exporting website claims to a csv. Error: user does not have permissions')
        raise PermissionDenied
    csv_fields = request.POST.dict()
    valid_csv_fields, err_msg = check_if_csv_fields_are_valid(csv_fields)
    if not valid_csv_fields:
        save_log_message(request.user.id, request.user.username,
                         'Exporting website claims to a csv. Error: ' + err_msg)
        return HttpResponse(json.dumps(err_msg), content_type='application/json', status=404)
    fields_to_export = request.POST.getlist('fields_to_export[]')
    scrapers_ids = [int(scraper_id) for scraper_id in request.POST.getlist('scrapers_ids[]')]
    regular_users = bool(csv_fields['regular_users'])
    verdict_date_start = datetime.strptime(csv_fields['verdict_date_start'], '%d/%m/%Y').date()
    verdict_date_end = datetime.strptime(csv_fields['verdict_date_end'], '%d/%m/%Y').date()
    valid_fields_and_scrapers_lists, err_msg = check_if_fields_and_scrapers_lists_valid(fields_to_export, scrapers_ids)
    if not valid_fields_and_scrapers_lists:
        save_log_message(request.user.id, request.user.username,
                         'Exporting website claims to a csv. Error: ' + err_msg)
        return HttpResponse(json.dumps(err_msg), content_type='application/json', status=404)
    df_claims = create_df_for_claims(fields_to_export, scrapers_ids, regular_users, verdict_date_start, verdict_date_end)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="claims.csv"'
    writer = csv.writer(response)
    writer.writerow(fields_to_export)
    for index, row in df_claims.iterrows():
        claim_info = []
        for col in df_claims:
            claim_info.append(row[col])
        writer.writerow(claim_info)
    save_log_message(request.user.id, request.user.username,
                     'Exporting website claims to a csv', True)
    return response


# This function checks if given csv fields are valid,
# i.e. the csv fields have all the fields with the correct format.
# The function returns true in case csv fields are valid, otherwise false and an error
def check_if_csv_fields_are_valid(csv_fields):
    err = ''
    if 'regular_users' not in csv_fields:
        csv_fields['regular_users'] = False
    if 'scrapers_ids[]' not in csv_fields:
        csv_fields['scrapers_ids[]'] = []
    if 'fields_to_export[]' not in csv_fields:
        err += 'Missing values for fields'
    elif 'verdict_date_start' not in csv_fields:
        err += 'Missing value for verdict date start'
    elif 'verdict_date_end' not in csv_fields:
        err += 'Missing value for verdict date end'
    else:
        err = convert_date_format(csv_fields, 'verdict_date_start')
        if len(err) == 0:
            err = convert_date_format(csv_fields, 'verdict_date_end')
    if len(err) > 0:
        return False, err
    return True, err


# This function checks if exported fields and list of scrapers' ids are valid.
# The function returns true in case they are valid, otherwise false and an error
def check_if_fields_and_scrapers_lists_valid(fields_to_export, scrapers_ids):
    from users.models import Scrapers
    err = ''
    valid_fields_to_export = ['Title', 'Description', 'Url', 'Category', 'Verdict Date', 'Tags',
                              'Label', 'System Label', 'Authenticity Grade']
    for field in fields_to_export:
        if field not in valid_fields_to_export:
            err += 'Field ' + str(field) + ' is not valid'
            return False, err
    for scraper_id in scrapers_ids:
        if len(User.objects.filter(id=scraper_id)) == 0 or  \
                len(Scrapers.objects.filter(scraper_id=User.objects.filter(id=scraper_id).first())) == 0:
            err += 'Scraper with id ' + str(scraper_id) + ' does not exist'
            return False, err
    return True, ''


# This function creates a df which contains all the details of the claims in the website
def create_df_for_claims(fields_to_export, scrapers_ids, regular_users, verdict_date_start, verdict_date_end):
    from claims.views import get_category_for_claim
    import pandas as pd
    df_claims = pd.DataFrame(columns=['User Id', 'Claim', 'Title', 'Description', 'Url', 'Category', 'Verdict Date', 'Tags', 'Label', 'System Label', 'Authenticity Grade'])
    users_ids, claims_ids, claims, titles, descriptions, urls, categories, verdict_dates, tags, labels, \
        system_labels, authenticity_grades = ([] for i in range(12))
    for comment in Comment.objects.all():
        claim = Claim.objects.filter(id=comment.claim_id).first()
        users_ids.append(comment.user_id)
        claims_ids.append(claim.id)
        claims.append(claim.claim)
        titles.append(comment.title)
        descriptions.append(comment.description)
        urls.append(comment.url)
        categories.append(get_category_for_claim(comment.claim_id))
        verdict_dates.append(comment.verdict_date)
        tags.append(comment.tags)
        labels.append(comment.label)
        system_labels.append(comment.system_label)
        authenticity_grades.append(claim.authenticity_grade)
    df_claims['User Id'] = users_ids
    df_claims['Claim Id'] = claims_ids
    df_claims['Claim'] = claims
    df_claims['Title'] = titles
    df_claims['Description'] = descriptions
    df_claims['Url'] = urls
    df_claims['Category'] = categories
    df_claims['Verdict Date'] = verdict_dates
    df_claims['Tags'] = tags
    df_claims['Label'] = labels
    df_claims['System Label'] = system_labels
    df_claims['Authenticity Grade'] = authenticity_grades
    if not regular_users:
        df_claims = df_claims[df_claims['User Id'].isin(scrapers_ids)]
    else:
        all_scrapers_ids = get_all_scrapers_ids_arr()
        scrapers_to_delete = [scraper_id for scraper_id in all_scrapers_ids if scraper_id not in scrapers_ids]
        df_claims = df_claims[~df_claims['User Id'].isin(scrapers_to_delete)]
    df_claims = df_claims[(df_claims['Verdict Date'] >= verdict_date_start) &
                          (df_claims['Verdict Date'] <= verdict_date_end)]
    fields_to_export.insert(0, 'Claim Id')
    df_claims = df_claims[fields_to_export]
    return df_claims


# This function returns all the comments for a given user's id
# The function returns all the comments in case they are found, otherwise None
def get_all_comments_for_user_id(user_id):
    result = Comment.objects.filter(user_id=user_id)
    if len(result) > 0:
        return result
    return None


# This function returns all the comments for a given claim's id
# The function returns all the comments in case they are found, otherwise None
def get_all_comments_for_claim_id(claim_id):
    result = Comment.objects.filter(claim_id=claim_id)
    if len(result) > 0:
        return result
    return None


# This function updates the claim's authenticity grade
def update_authenticity_grade(claim_id):
    weighted_sum_true_label, weighted_sum_false_label = 0, 0
    num_of_true_labels, num_of_false_labels = 0, 0
    for comment in Comment.objects.filter(claim_id=claim_id):
        user_rep = (math.ceil(get_user_reputation(comment.user_id) / 20)) / 5
        if comment.up_votes.count() == comment.down_votes.count() == 0:
            comment_ratio_votes = 1
        else:
            comment_ratio_votes = comment.up_votes.count() / (comment.up_votes.count() + comment.down_votes.count())
        comment_score = user_rep * comment_ratio_votes
        if comment.system_label == 'True':
            num_of_true_labels += 1
            weighted_sum_true_label += comment_score
        elif comment.system_label == 'False':
            num_of_false_labels += 1
            weighted_sum_false_label += comment_score
    if num_of_true_labels == num_of_false_labels == 0:
        total_weighted = 0
    else:
        total_weighted = (weighted_sum_true_label - weighted_sum_false_label) / \
                         (num_of_true_labels + num_of_false_labels)
    if total_weighted < 0:
        authenticity_grade = max(0, 0.5 + total_weighted)
    elif total_weighted == 0:
        authenticity_grade = 0.5
    else:
        authenticity_grade = min(1, 0.5 + total_weighted)
    authenticity_grade *= 100
    Claim.objects.filter(id=claim_id).update(authenticity_grade=authenticity_grade)


def update_authenticity_grade_for_all_claims(request):
    for claim in Claim.objects.all():
        update_authenticity_grade(claim.id)
    from claims.views import view_home
    return view_home(request)
