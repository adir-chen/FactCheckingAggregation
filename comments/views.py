from django.shortcuts import get_object_or_404
from comments.models import Comment
from claims.models import Claim
from django.http import HttpResponse, Http404
from users.views import check_if_user_exists_by_user_id
import csv
import datetime


# This function takes care of a request to add a new comment to a claim in the website
def add_comment(request):
    from claims.views import view_claim
    if request.method == "POST":
        comment_info = request.POST
        valid_comment, err_msg = check_if_comment_is_valid(comment_info)
        if not valid_comment:
            raise Exception(err_msg)
        build_comment(request.POST.get('claim_id'),
                      request.POST.get('user_id'),
                      request.POST.get('title'),
                      request.POST.get('description'),
                      request.POST.get('url'),
                      datetime.datetime.strftime(datetime.datetime.now(), '%d/%m/%Y'),
                      request.POST.get('label'))
        return view_claim(request, request.POST.get('claim_id'))
    raise Http404("Invalid method")


# This function adds a new comment to a claim in the website
def build_comment(claim_id, user_id, title, description, url, verdict_date, label):
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


# This function checks if a given comment is valid, i.e. the comment has all the fields with the correct format.
# The function returns true in case the comment is valid, otherwise false and an error
def check_if_comment_is_valid(comment_info):
    err = ''
    if 'claim_id' not in comment_info:
        err += 'Missing value for claim id'
    elif 'user_id' not in comment_info:
        err += 'Missing value for user id'
    elif 'title' not in comment_info or not comment_info['title']:
        err += 'Missing value for title'
    elif 'description' not in comment_info or not comment_info['description']:
        err += 'Missing value for description'
    elif 'url' not in comment_info or not comment_info['url']:
        err += 'Missing value for url'
    elif 'label' not in comment_info or not comment_info['label']:
        err += 'Missing value for label'
    elif len(Claim.objects.filter(id=comment_info['claim_id'])) == 0:
        err += 'Claim ' + str(comment_info['claim_id']) + 'does not exist'
    elif not check_if_user_exists_by_user_id(comment_info['user_id']):
        err += 'User with id ' + str(comment_info['user_id']) + ' does not exist'
    if len(err) > 0:
        return False, err
    return True, err


# This function checks a comment's label and returns a basic classification for it.
# The function returns true in case the comment's label is composed from words with 'true' meaning, otherwise false
def get_system_label_to_comment(comment_label):
    if comment_label.isdigit():
        return int(comment_label) > 5
    true_label_arr = ['true', 'accurate', 'correct']
    for true_label in true_label_arr:
        for word in comment_label.split():
            if word.lower() == true_label:
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
def export_to_csv(request):
    from claims.views import get_category_for_claim, get_tags_for_claim
    if not request.user.is_superuser:
        raise Http404("Permission denied")
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="claims.csv"'
    writer = csv.writer(response)
    writer.writerow(['Title', 'Description', 'Url', 'Category', 'Verdict_Date', 'Tags', 'Label'])
    for comment in Comment.objects.all():
        writer.writerow([comment.title, comment.description, comment.url, get_category_for_claim(comment.claim_id),
                        comment.verdict_date, get_tags_for_claim(comment.claim_id), comment.label])
    return response


# This function increases a comment's vote by 1
def up_vote(request):
    from claims.views import view_claim
    comment = get_object_or_404(Comment, id=request.POST.get('comment_id'))
    if comment.up_votes.filter(id=request.POST.get('user_id')).exists():
        comment.up_votes.remove(request.POST.get('user_id'))
    else:
        comment.up_votes.add(request.POST.get('user_id'))
        if comment.down_votes.filter(id=request.POST.get('user_id')).exists():
            comment.down_votes.remove(request.POST.get('user_id'))
    update_authenticity_grade(comment.claim_id)
    return view_claim(request, comment.claim_id)


# This function decreases a comment's vote by 1
def down_vote(request):
    from claims.views import view_claim
    comment = get_object_or_404(Comment, id=request.POST.get('comment_id'))
    if comment.down_votes.filter(id=request.POST.get('user_id')).exists():
        comment.down_votes.remove(request.POST.get('user_id'))
    else:
        comment.down_votes.add(request.POST.get('user_id'))
        if comment.up_votes.filter(id=request.POST.get('user_id')).exists():
            comment.up_votes.remove(request.POST.get('user_id'))
    update_authenticity_grade(comment.claim_id)
    return view_claim(request, comment.claim_id)


# This function edits a comment in the website
def edit_comment(request):
    from claims.views import view_claim
    valid_new_comment, err_msg = check_comment_new_fields(request)
    if not valid_new_comment:
        raise Exception(err_msg)
    if len(Comment.objects.filter(id=request.POST.get('comment_id'))) == 0:
        raise Exception("Invalid comment id")
    elif not check_if_user_exists_by_user_id(request.POST.get('user_id')):
        raise Exception('User with id ' + str(request.POST.get('user_id')) + ' does not exist')
    comment = get_object_or_404(Comment, id=request.POST.get('comment_id'))
    Comment.objects.filter(id=comment.id, user_id=request.POST.get('user_id')).update(
        title=request.POST.get('comment_title'),
        description=request.POST.get('comment_description'),
        url=request.POST.get('comment_reference'),
        verdict_date=datetime.datetime.strftime(datetime.datetime.now(), '%d/%m/%Y'),
        system_label=request.POST.get('comment_label'))
    update_authenticity_grade(comment.claim_id)
    return view_claim(request, comment.claim_id)


# This function checks if the given new fields for a comment are valid, i.e. the comment has all the fields with the correct format.
# The function returns true in case the comment's new fields are valid, otherwise false and an error
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


# This function deletes a comment from the website
def delete_comment(request):
    from claims.views import view_claim
    if len(Comment.objects.filter(id=request.POST.get('comment_id'))) == 0:
        raise Exception("Invalid comment id")
    elif not check_if_user_exists_by_user_id(request.POST.get('user_id')):
        raise Exception('User with id ' + str(request.POST.get('user_id')) + ' does not exist')
    comment = get_object_or_404(Comment, id=request.POST.get('comment_id'))
    Comment.objects.filter(id=comment.id, user_id=request.POST.get('user_id')).delete()
    update_authenticity_grade(comment.claim_id)
    return view_claim(request, comment.claim_id)


# This function updates the claim's authenticity grade
def update_authenticity_grade(claim_id):
    num_of_true_label = 0
    num_of_false_label = 0
    result = Comment.objects.filter(claim_id=claim_id)
    for res in result:
        if res.up_votes.count() - res.down_votes.count() >= 0:
            if res.system_label:
                num_of_true_label += 1
            else:
                num_of_false_label += 1
    if num_of_true_label + num_of_false_label == 0:
        authenticity_grade = 0
    else:
        authenticity_grade = (num_of_true_label/(num_of_true_label + num_of_false_label)) * 100
    Claim.objects.filter(id=claim_id).update(authenticity_grade=authenticity_grade)

