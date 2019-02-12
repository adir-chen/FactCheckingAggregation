from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render
from comments.models import Comment
from comments.views import build_comment
from django.contrib.auth.models import User
from users.models import Users_Images
from users.views import add_all_scrapers, check_if_user_exists_by_user_id
from .models import Claim
from django.views.decorators.csrf import ensure_csrf_cookie
from datetime import datetime


# This function adds a new claim to the website, following with a comment on it
# @login_required()
def add_claim(request):
    if request.method == "POST":
        claim_info = request.POST.dict()
        valid_claim, err_msg = check_if_claim_is_valid(claim_info)
        if not valid_claim:
            raise Http404(err_msg)
        tags_arr = claim_info['tags'].split(' ')
        new_tags = ''
        for tag in tags_arr:
            new_tags += tag + ', '
        new_tags = new_tags[:-2]
        claim = Claim(
            claim=claim_info['claim'],
            category=claim_info['category'],
            tags=new_tags,
            authenticity_grade=0,
            image_src=claim_info['img_src']
        )
        claim.save()
        build_comment(claim.id, claim_info['user_id'], claim_info['title'],
                    claim_info['description'], claim_info['url'], claim_info['verdict_date'], claim_info['label'])
        return render(request, 'claims/claim.html', {
            'claim': claim.claim,
            'category': claim.category,
            'authenticity_grade': claim.authenticity_grade,
            'image_url': claim.image_src,
            'comments': Comment.objects.filter(claim_id=claim.id),
        })
    raise Http404("Invalid method")


# This function checks if a given claim is valid, i.e. the claim has all the fields with the correct format.
# The function returns true in case the claim is valid, otherwise false and an error
def check_if_claim_is_valid(claim_info):
    err = ''
    if 'user_id' not in claim_info:
        err += 'Missing value for user'
    elif 'claim' not in claim_info:
        err += 'Missing value for claim'
    elif 'category' not in claim_info:
        err += 'Missing value for category'
    elif 'title' not in claim_info:
        err += 'Missing value for title'
    elif 'description' not in claim_info:
        err += 'Missing value for description'
    elif 'url' not in claim_info:
        err += 'Missing value for url'
    elif 'verdict_date' not in claim_info:
        err += 'Missing value for verdict_date'
    elif 'tags' not in claim_info:
        err += 'Missing value for tags'
    elif 'label' not in claim_info:
        err += 'Missing value for label'
    elif 'img_src' not in claim_info:
        err += 'Missing value for img_src'
    elif len(Claim.objects.filter(claim=claim_info['claim'])) > 0:
        err += 'Claim ' + claim_info['claim'] + 'already exists'
    elif not check_if_user_exists_by_user_id(claim_info['user_id']):
        err += 'User ' + claim_info['user_id'] + ' does not exist'
    elif not is_valid_verdict_date(claim_info['verdict_date']):
        err += 'Date ' + claim_info['verdict_date'] + ' is invalid'
    if len(err) > 0:
        return False, err
    return True, err


# This function checks if the verdict date of a claim is valid
# The function returns true in case the verdict date is valid, otherwise false
def is_valid_verdict_date(verdict_date):
    try:
        verdict_datetime = datetime.strptime(verdict_date, "%d/%m/%Y")
        return datetime.today() >= verdict_datetime
    except:
        return False


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
# The function returns claim's tags in case it is found, otherwise None
def get_tags_for_claim(claim_id):
    result = Claim.objects.filter(id=claim_id)
    if len(result) > 0:
        return result[0].tags
    return None


# This function returns a claim page of a given claim id
# The function returns the claim page in case the claim is found, otherwise Http404
def view_claim(request, claim_id):
    claim = get_claim_by_id(claim_id)
    if claim is None:
        raise Http404("Claim with the given id: " + str(claim_id) + " does not exist")
    comment_objs = Comment.objects.filter(claim_id=claim_id)
    comments = {}
    for comment in comment_objs:
        comments[User.objects.filter(id=comment.user_id)[0]] = comment
    return render(request, 'claims/claim.html', {
        'claim': claim,
        'comments': comments,
    })


# This function returns the home page of the website
@ensure_csrf_cookie
def view_home(request):
    # add_all_scrapers()
    headlines_size = 2
    claims_size = 40
    claim_objs = Claim.objects.all().order_by('-id')[:claims_size]
    headlines = {}
    sub_headlines = {}
    for claim in claim_objs[:headlines_size]:
        comment_objs = Comment.objects.filter(claim_id=claim.id)
        users_imgs = []
        for comment in comment_objs:
            user_img = Users_Images.objects.filter(user_id=comment.user_id)
            if len(user_img) > 0:
                users_imgs.append(user_img[0].user_img)
        headlines[claim] = users_imgs
    for claim in claim_objs[headlines_size:]:
        comment_objs = Comment.objects.filter(claim_id=claim.id)
        users_imgs = []
        for comment in comment_objs:
            user_img = Users_Images.objects.filter(user_id=comment.user_id)
            if len(user_img) > 0:
                users_imgs.append(user_img[0].user_img)
        sub_headlines[claim] = users_imgs

    try:
        if request.user.is_authenticated and len(User.objects.filter(email=request.user.email)) == 0:
            new_user = User(username=request.user.username, email=request.user.email)
            new_user.save()
    except:
        '' # do nothing
    return render(request, 'claims/index.html', {'headlines': headlines, 'sub_headlines': sub_headlines})


def logout_view(request):
    logout(request)
    return view_home(request)
