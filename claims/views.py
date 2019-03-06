from django.contrib.auth import logout, authenticate
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from comments.models import Comment
from comments.views import add_comment
from django.contrib.auth.models import User
from logger.models import Logger
from logger.views import save_log_message
from users.models import Users_Images, Scrapers, Users_Reputations
from users.views import check_if_user_exists_by_user_id
from .models import Claim
from django.views.decorators.csrf import ensure_csrf_cookie


# This function adds a new claim to the website, followed with a comment on it
def add_claim(request):
    if not request.user.is_authenticated:  # scraper case
        if not request.POST.get('username') or not request.POST.get('password') or not \
                authenticate(request, username=request.POST.get('username'), password=request.POST.get('password')):
            raise Http404("Permission denied")
        request.user = authenticate(request, username=request.POST.get('username'), password=request.POST.get('password'))
    if request.method == "POST":
        claim_info = request.POST.dict()
        claim_info['user_id'] = request.user.id
        valid_claim, err_msg = check_if_claim_is_valid(claim_info)
        if not valid_claim:
            save_log_message(request.user.id, request.user.username,
                             'Adding a new claim. Error: ' + err_msg)
            raise Exception(err_msg)
        claim = Claim(
            user_id=claim_info['user_id'],
            claim=claim_info['claim'],
            category=claim_info['category'],
            tags=', '.join(claim_info['tags'].split()),
            authenticity_grade=0,
            image_src=claim_info['image_src']
        )
        claim.save()
        save_log_message(request.user.id, request.user.username,
                         'Adding a new claim', True)
        claim_info['claim_id'] = claim.id
        request.POST = claim_info
        if claim_info['add_comment'] == 'true':
            try:
                add_comment(request)
            except Exception as e:
                claim.delete()
                save_log_message(request.user.id, request.user.username,
                                 'Adding a new comment on claim with id ' + str(
                                     claim.id) + '. Error: ' + str(e) +
                                 '. This claim has been deleted because ' +
                                 'the user does not succeed to add a new claim with a comment on it.')
                raise Exception(e)
        return view_claim(request, claim.id)
    raise Http404("Invalid method")


# This function checks if a given claim is valid, i.e. the claim has all the fields with the correct format.
# The function returns true in case the claim is valid, otherwise false and an error
def check_if_claim_is_valid(claim_info):
    err = ''
    if 'tags' not in claim_info or not claim_info['tags']:
        claim_info['tags'] = ''
    if not check_if_tags_are_valid(claim_info['tags']):
        err += 'Incorrect format for tags. Tags should be separated by space'
    elif 'user_id' not in claim_info:
        err += 'Missing value for user'
    elif 'claim' not in claim_info or not claim_info['claim']:
        err += 'Missing value for claim'
    elif 'category' not in claim_info or not claim_info['category']:
        err += 'Missing value for category'
    elif 'image_src' not in claim_info:
        err += 'Missing value for image source'
    elif 'add_comment' not in claim_info:
        err += 'Missing value for adding a comment option'
    elif len(Claim.objects.filter(claim=claim_info['claim'])) > 0:
        err += 'Claim ' + claim_info['claim'] + ' already exists'
    elif not check_if_user_exists_by_user_id(claim_info['user_id']):
        err += 'User ' + str(claim_info['user_id']) + ' does not exist'
    elif not is_english_input(claim_info['claim']) or \
            not is_english_input(claim_info['category']) or \
            not is_english_input(claim_info['tags']):
        err += 'Input should be in the English language'
    elif post_above_limit(claim_info['user_id']):
        err += 'You have exceeded the amount limit of adding new claims today'
    if len(err) > 0:
        return False, err
    return True, err


# This function checks if given claim's tags are valid, i.e. the tags are in the correct format.
# The function returns true in case the claim's tags are valid, otherwise false
def check_if_tags_are_valid(tags):
    return tags == '' or all(tag.isdigit() or tag.isalpha() or tag.isspace() for tag in tags)


# This function checks if a given user's input is valid, i.e. the input is in the English language.
# The function returns true in case the user's input is valid, otherwise false
def is_english_input(user_input):
    try:
        user_input.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    return True


# This function checks if a given user posted new claims above the maximum limit (per day).
# The function returns true in case the user exceeded the maximum limit, otherwise false and an error
def post_above_limit(user_id):
    limit = 10
    from datetime import datetime
    return len(Logger.objects.filter(date__date=datetime.today(),
                                     user_id=user_id,
                                     action__icontains='Adding a new claim')) >= limit


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


# This function returns a claim page of a given claim id
# The function returns the claim page in case the claim is found, otherwise Http404
def view_claim(request, claim_id):
    import math
    claim = get_claim_by_id(claim_id)
    if claim is None:
        raise Http404('Claim with id ' + str(claim_id) + ' does not exist')
    comment_objects = Comment.objects.filter(claim_id=claim_id)
    comments = {}
    for comment in comment_objects:
        user_img = Users_Images.objects.filter(user_id=comment.user_id)
        if len(user_img) == 0:
            new_user_img = Users_Images.objects.create(user_id=User.objects.filter(id=comment.user_id).first())
            new_user_img.save()
            user_img = new_user_img
        else:
            user_img = user_img.first()
        user_rep = Users_Reputations.objects.filter(user_id=comment.user_id)
        if len(user_rep) == 0:
            new_user_rep = Users_Reputations.objects.create(user_id=User.objects.filter(id=comment.user_id).first())
            new_user_rep.save()
            user_rep = new_user_rep
        else:
            user_rep = user_rep.first()
        comments[comment] = {'user': User.objects.filter(id=comment.user_id).first(),
                             'user_img': user_img,
                             'user_rep': math.ceil(user_rep.user_rep / 20)}
    return render(request, 'claims/claim.html', {
        'claim': claim,
        'comments': comments,
    })


# This function returns the home page of the website
@ensure_csrf_cookie
def view_home(request):
    from django.core.paginator import Paginator
    claims = list(get_users_images_for_claims(Claim.objects.all().order_by('-id')).items())
    page = request.GET.get('page')
    paginator = Paginator(claims, 7)
    return render(request, 'claims/index.html', {'claims': paginator.get_page(page)})


# This function returns a dict with pairs of (claim, user_image)
# where user_image is a link to user's profile image who posts the claim
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


# This function disconnects the user from the website
def logout_view(request):
    logout(request)
    return view_home(request)


# This function return a HTML page for adding a new claim to the website
def add_claim_page(request):
    return render(request, 'claims/add_claim.html')


# This function return a HTML page for adding a new claim to the website
def export_claims_page(request):
    return render(request, 'claims/export_claims.html', {'all_scrapers': Scrapers.objects.all()})


# This function edits a claim in the website
def edit_claim(request):
    if not request.user.is_authenticated:
        raise Http404("Permission denied")
    new_claim_fields = request.POST.dict()
    new_claim_fields['user_id'] = request.user.id
    valid_new_claim, err_msg = check_claim_new_fields(new_claim_fields)
    if not valid_new_claim:
        save_log_message(request.user.id, request.user.username,
                         'Editing a claim. Error: ' + err_msg)
        raise Exception(err_msg)
    claim = get_object_or_404(Claim, id=request.POST.get('claim_id'))
    Claim.objects.filter(id=claim.id, user_id=request.user.id).update(
        claim=new_claim_fields['claim'],
        category=new_claim_fields['category'],
        tags=', '.join(new_claim_fields['tags'].split()),
        image_src=new_claim_fields['image_src'])
    save_log_message(request.user.id, request.user.username,
                     'Editing a claim with id ' + str(request.POST.get('claim_id')), True)
    return view_claim(request, claim.id)


# This function checks if the given new fields for a claim are valid,
# i.e. the claim has all the fields with the correct format.
# The function returns true in case the claim's new fields are valid, otherwise false and an error
def check_claim_new_fields(new_claim_fields):
    from django.utils import timezone
    err = ''
    max_minutes_to_edit_claim = 5
    if 'tags' not in new_claim_fields or not new_claim_fields['tags']:
        new_claim_fields['tags'] = ''
    if not check_if_tags_are_valid(new_claim_fields['tags']):
        err += 'Incorrect format for tags. Tags should be separated by space'
    elif 'user_id' not in new_claim_fields or not new_claim_fields['user_id']:
        err += 'Missing value for user id'
    elif 'claim_id' not in new_claim_fields or not new_claim_fields['claim_id']:
        err += 'Missing value for claim id'
    elif 'claim' not in new_claim_fields or not new_claim_fields['claim']:
        err += 'Missing value for claim'
    elif 'category' not in new_claim_fields or not new_claim_fields['category']:
        err += 'Missing value for category'
    elif 'image_src' not in new_claim_fields or not new_claim_fields['image_src']:
        err += 'Missing value for image source'
    elif not check_if_user_exists_by_user_id(new_claim_fields['user_id']):
        err += 'User with id ' + str(new_claim_fields['user_id']) + ' does not exist'
    elif len(Claim.objects.filter(id=new_claim_fields['claim_id'], user_id=new_claim_fields['user_id'])) == 0:
        err += 'Claim does not belong to user with id ' + str(new_claim_fields['user_id'])
    elif len(Claim.objects.exclude(id=new_claim_fields['claim_id']).filter(claim=new_claim_fields['claim'])) > 0:
        err += 'Claim already exists'
    elif (timezone.now() - Claim.objects.filter(id=new_claim_fields['claim_id']).first().timestamp).total_seconds() \
            / 60 > max_minutes_to_edit_claim:
        err += 'You can no longer edit your comment'
    elif not is_english_input(new_claim_fields['claim']) or \
            not is_english_input(new_claim_fields['category']) or \
            not is_english_input(new_claim_fields['tags']):
        err += 'Input should be in the English language'
    if len(err) > 0:
        return False, err
    return True, err


# This function deletes a claim from the website
def delete_claim(request):
    if not request.user.is_authenticated:
        raise Http404("Permission denied")
    valid_delete_claim, err_msg = check_if_delete_claim_is_valid(request)
    if not valid_delete_claim:
        save_log_message(request.user.id, request.user.username,
                         'Deleting a claim. Error: ' + err_msg)
        raise Exception(err_msg)
    from users.views import update_reputation_for_user
    for comment in Comment.objects.filter(claim_id=request.POST.get('claim_id')):
        update_reputation_for_user(comment.user_id, False, comment.up_votes.count())
        update_reputation_for_user(comment.user_id, True, comment.down_votes.count())
    Claim.objects.filter(id=request.POST.get('claim_id'), user_id=request.user.id).delete()
    save_log_message(request.user.id, request.user.username,
                     'Deleting a claim with id ' + str(request.POST.get('claim_id')), True)
    return view_home(request)


# This function checks if the given new fields for a claim are valid,
# i.e. the claim has all the fields with the correct format.
# The function returns true in case the claim's new fields are valid, otherwise false and an error
def check_if_delete_claim_is_valid(request):
    err = ''
    if not request.POST.get('claim_id'):
        err += 'Missing value for claim id'
    elif len(Claim.objects.filter(id=request.POST.get('claim_id'))) == 0:
        err += 'Claim with id ' + str(request.user.id) + ' does not exist'
    elif not check_if_user_exists_by_user_id(request.user.id):
        err += 'User with id ' + str(request.user.id) + ' does not exist'
    elif len(Claim.objects.filter(id=request.POST.get('claim_id'), user=request.user.id)) == 0:
        err += 'Claim with id ' + str(request.POST.get('claim_id')) + ' does not belong to user with id ' + str(request.user.id)
    if len(err) > 0:
        return False, err
    return True, err


# This function returns 400 error page
def handler_400(request):
    return render(request, 'claims/400.html', status=400)


# This function returns 403 error page
def handler_403(request):
    return render(request, 'claims/403.html', status=403)


# This function returns 404 error page
def handler_404(request):
    return render(request, 'claims/404.html', status=404)


# This function returns 500 error page
def handler_500(request):
    return render(request, 'claims/500.html', status=500)


def about_page(request):
    return render(request, 'claims/about.html')
