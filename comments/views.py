import csv
from comments.models import Comment
from claims.models import Claim
from django.http import HttpResponse, Http404
from users.views import check_if_user_exists_by_user_id
import datetime


# This function converts a request to a new comment to a claim in the website
def add_comment(request):
    from claims.views import view_claim
    from users.views import get_user_id_by_username
    build_comment(request.GET.get('claim_id'),
                       get_user_id_by_username(request.GET.get('user_name')),
                       request.GET.get('title'),
                       request.GET.get('description'),
                       request.GET.get('url'),
                       datetime.datetime.strftime(datetime.datetime.now(), '%d/%m/%Y'),
                       request.GET.get('label'))

    return view_claim(request, request.GET.get('claim_id'))


# This function adds a new comment to a claim in the website
def build_comment(claim_id, user_id, title, description, url, verdict_date, label):
    valid_comment, err_msg = check_if_comment_is_valid({'claim_id': claim_id, 'user_id': user_id, 'title': title, 'description': description, 'url': url, 'verdict_date': verdict_date, 'label': label})
    if not valid_comment:
        raise Http404(err_msg)
    comment = Comment(
        claim_id=claim_id,
        user_id=user_id,
        title=title,
        description=description,
        url=url,
        verdict_date=verdict_date,
        label=label,
        pos_votes=0,
        neg_votes=0
    )
    comment.save()


def check_if_comment_is_valid(comment_info):
    from claims.views import is_valid_verdict_date
    err = ''
    if 'claim_id' not in comment_info:
        err += 'Missing value for claim'
    elif 'user_id' not in comment_info:
        err += 'Missing value for user id'
    elif 'title' not in comment_info or not comment_info['title']:
        err += 'Missing value for title'
    elif 'description' not in comment_info or not comment_info['description']:
        err += 'Missing value for description'
    elif 'url' not in comment_info or not comment_info['url']:
        err += 'Missing value for url'
    elif 'verdict_date' not in comment_info:
        err += 'Missing value for verdict_date'
    elif 'label' not in comment_info or not comment_info['label']:
        err += 'Missing value for label'
    elif len(Claim.objects.filter(id=comment_info['claim_id'])) == 0:
        err += 'Claim ' + comment_info['claim_id'] + 'does not exist'
    elif not check_if_user_exists_by_user_id(comment_info['user_id']):
        err += 'User with id ' + comment_info['user_id'] + ' does not exist'
    elif not is_valid_verdict_date(comment_info['verdict_date']):
        err += 'Date ' + comment_info['verdict_date'] + ' is invalid'
    if len(err) > 0:
        return False, err
    return True, err


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


# The function deletes all the comments in the website
def reset_comments():
    Comment.objects.all().delete()


# This function returns the category for a given claim's id
# The function returns claim's category in case it is found, otherwise None
def get_category_for_claim(claim_id):
    result = Claim.objects.filter(id=claim_id)
    if len(result) > 0:
        return result[0].category
    return None


# This function returns a csv which contains all the details of the claims in the website
def export_to_csv():
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="claims.csv"'
    writer = csv.writer(response)
    writer.writerow(['Title', 'Description', 'Url', 'Category', 'Verdict_Date', 'Tags', 'Label'])
    for comment in Comment.objects.all():
        writer.writerow([comment.title, comment.description, comment.url, get_category_for_claim(comment.claim_id),
                        comment.verdict_date, comment.tags, comment.label])
    return response


# def upvote(request):
