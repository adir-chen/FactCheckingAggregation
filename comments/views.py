import csv
from django.shortcuts import get_object_or_404
from comments.models import Comment
from claims.models import Claim
from django.http import HttpResponse, Http404
from users.views import check_if_user_exists_by_user_id
import datetime


# This function converts a request to a new comment to a claim in the website
def add_comment(request):
    from claims.views import view_claim
    build_comment(request.GET.get('claim_id'),
                       request.user.id,
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
        system_label=get_system_label_to_comment(label),

    )
    comment.save()
    update_authenticity_grade(comment.claim_id)


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
        err += 'Claim ' + str(comment_info['claim_id']) + 'does not exist'
    elif not check_if_user_exists_by_user_id(comment_info['user_id']):
        err += 'User with id ' + str(comment_info['user_id']) + ' does not exist'
    elif not is_valid_verdict_date(comment_info['verdict_date']):
        err += 'Date ' + comment_info['verdict_date'] + ' is invalid'
    if len(err) > 0:
        return False, err
    return True, err


def get_system_label_to_comment(comment_label):
    true_label_arr = ['true', 'accurate']
    for true_label in true_label_arr:
        if true_label.lower() in comment_label.lower():
            return True
    return False


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


# This function returns a csv which contains all the details of the claims in the website
def export_to_csv():
    from claims.views import get_category_for_claim, get_tags_for_claim
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="claims.csv"'
    writer = csv.writer(response)
    writer.writerow(['Title', 'Description', 'Url', 'Category', 'Verdict_Date', 'Tags', 'Label'])
    for comment in Comment.objects.all():
        writer.writerow([comment.title, comment.description, comment.url, get_category_for_claim(comment.claim_id),
                        comment.verdict_date, get_tags_for_claim(comment.claim_id), comment.label])
    return response


def up_vote(request):
    from claims.views import view_claim
    comment = get_object_or_404(Comment, id=request.POST.get('comment_id'))
    if comment.up_votes.filter(id=request.user.id).exists():
        comment.up_votes.remove(request.user)
    else:
        comment.up_votes.add(request.user)
        if comment.down_votes.filter(id=request.user.id).exists():
            comment.down_votes.remove(request.user)
    return view_claim(request, comment.claim_id)


def down_vote(request):
    from claims.views import view_claim
    comment = get_object_or_404(Comment, id=request.POST.get('comment_id'))
    if comment.down_votes.filter(id=request.POST.get('user_id')).exists():
        comment.down_votes.remove(request.user)
    else:
        comment.down_votes.add(request.user)
        if comment.up_votes.filter(id=request.POST.get('user_id')).exists():
            comment.up_votes.remove(request.user)
    return view_claim(request, comment.claim_id)


def edit_comment(request):
    from claims.views import view_claim
    valid_new_comment, err_msg = check_comment_new_fields(request)
    if not valid_new_comment:
        raise Exception(err_msg)
    comment = get_object_or_404(Comment, id=request.POST.get('comment_id'))
    Comment.objects.filter(id=comment.id, user_id=request.POST.get('user_id')).update(
        title=request.POST.get('comment_title'),
        description=request.POST.get('comment_description'),
        url=request.POST.get('comment_reference'),
        verdict_date=datetime.datetime.strftime(datetime.datetime.now(), '%d/%m/%Y'),
        label=request.POST.get('comment_label'))
    update_authenticity_grade(comment.claim_id)
    return view_claim(request, comment.claim_id)


def check_comment_new_fields(request):
    err = ''
    if not request.POST.get('comment_title'):
        err += 'Missing value for comment title'
    elif not request.POST.get('comment_description'):
        err += 'Missing value for comment description'
    elif not request.POST.get('comment_reference'):
        err += 'Missing value for comment reference'
    elif not request.POST.get('comment_label'):
        err += 'Missing value for comment label'
    if len(err) > 0:
        return False, err
    return True, err


def delete_comment(request):
    from claims.views import view_claim
    comment = get_object_or_404(Comment, id=request.POST.get('comment_id'))
    Comment.objects.filter(id=comment.id).delete()
    update_authenticity_grade(comment.claim_id)
    return view_claim(request, comment.claim_id)


def update_authenticity_grade(claim_id):
    num_of_true_label = 0
    num_of_false_label = 0
    result = Comment.objects.filter(claim_id=claim_id)
    for res in result:
        if res.up_votes.count() - res.down_votes.count() >= 0:
            if res.label == 'True':
                num_of_true_label += 1
            else:
                num_of_false_label += 1
    authenticity_grade = (num_of_true_label/(num_of_true_label + num_of_false_label)) * 100
    Claim.objects.filter(id=claim_id).update(authenticity_grade=authenticity_grade)

