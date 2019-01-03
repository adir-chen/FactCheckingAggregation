from django.http import Http404
from django.shortcuts import render
from comments.models import Comment
from comments.views import add_comment
from users.views import get_user_id_by_username
from users.views import get_username_by_user_id
from .models import Claim
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from datetime import datetime


# This function adds a new claim to the website, following with a comment on it
@csrf_exempt
def add_claim(request):
    if request.method == "POST":
        claim_info = request.POST.dict()
        valid_claim, err_msg = check_if_claim_is_valid(claim_info)
        if not valid_claim:
            raise Http404(err_msg)

        claim = Claim(
            claim=claim_info['claim'],
            category=claim_info['category'],
            authentic_grade=-1,
            image_src=claim_info['img_src']
        )
        claim.save()
        add_comment(claim.id, get_user_id_by_username(claim_info['username']), claim_info['title'],
                    claim_info['description'], claim_info['url'], claim_info['verdict_date'],
                    claim_info['tags'], claim_info['label'])
        return render(request, 'claims/claim.html', {
            'claim': claim.claim,
            'category': claim.category,
            'authenticity_grade': claim.authentic_grade,
            'image_url': claim.image_src,
            'comments': Comment.objects.filter(claim_id=claim.id),
        })
    raise Http404("Invalid method")


# This function checks if a given claim is valid, i.e. the claim has all the fields with the correct format.
# The function returns true in case the claim is valid, otherwise false and an error
def check_if_claim_is_valid(claim_info):
    err = ''
    if 'claim' not in claim_info:
        err += 'Missing value for claim'
    elif 'category' not in claim_info:
        err += 'Missing value for category'
    elif 'img_src' not in claim_info:
        err += 'Missing value for img_src'
    elif 'username' not in claim_info:
        err += 'Missing value for username'
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
    elif len(Claim.objects.filter(claim=claim_info['claim'])) > 0:
        err += 'Claim ' + claim_info['claim'] + 'already exists'
    elif get_user_id_by_username(claim_info['username']) is None:
        err += 'User ' + claim_info['username'] + ' does not exist'
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


# This function deletes all the claims in the website
def reset_claims():
    Claim.objects.all().delete()


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


# This function returns a claim page of a given claim id
# The function returns the claim page in case the claim is found, otherwise Http404
def view_claim(request, id):
    claim = get_claim_by_id(id)
    if claim is None:
        raise Http404("Claim with the given id: " + str(id) + " does not exist")
    comment_objs = Comment.objects.filter(claim_id=id)
    comments = {}
    for comment in comment_objs:
        comments[get_username_by_user_id(comment.user_id)] = comment
    return render(request, 'claims/claim.html', {
        'claim': claim.claim,
        'category': claim.category,
        'authenticity_grade': claim.authentic_grade,
        'image_url': claim.image_src,
        'comments': comments,
    })


# This function returns the home page of the website
def view_home(request):
    return render(request, 'claims/index.html', {'headlines': Claim.objects.all().order_by('-id')[:2], 'sub_headlines': Claim.objects.all().order_by('-id')[2:35]})
