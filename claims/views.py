from django.shortcuts import render
from comments.models import Comment
from comments.views import add_comment
from users.views import get_user_id_by_username
from .models import Claim
from django.views.decorators.csrf import csrf_protect, csrf_exempt


# add a new claim to system.
@csrf_exempt
def add_claim(request):
    if request.method == "POST":
        claim_info = request.POST.dict()
        claim = Claim(
            title=claim_info['claim'],
            category=claim_info['category'],
            authentic_grade = -1,
            image_src=claim_info['img_src']
        )
        try:
            claim.save()
            add_comment(claim.id, get_user_id_by_username(claim_info['username']), claim_info['title'],
                        claim_info['description'], claim_info['url'], claim_info['verdict_date'],
                        claim_info['tags'], claim_info['label'])
        except Exception as e:
            print('Adding new comment failed ' + str(e))
    #return export_to_csv()


def get_all_claims():
    return Claim.objects.all()


def reset_claims():
    Claim.objects.all().delete()


def get_newest_claims():
    result = Claim.objects.all().order_by('-id')
    if len(result) < 20:
        return result
    return result[0:20]


def get_claim_by_id(id):
    result = Claim.objects.filter(id = id)
    if len(result) > 0:
        return result[0]
    return None


def view_claim(request, id):
    data = request.POST.dict()
    #Claim.objects.get(id=data['claim_id'])
    claim = get_claim_by_id(id)
    # comments = get_all_comments_for_claim_id(id)
    #print("comments")
    #print(Comment.objects.filter(claim_id=34))
    #request.session['comments'] = get_all_comments_for_claim_id(data['claim_id'])
    return render(request, 'claims/claim.html', {
        'title': claim.title,
        'category': claim.category,
        'authenticity_grade': claim.authentic_grade,
        'image_url': claim.image_src,
        'comments': Comment.objects.filter(claim_id=id),
    })


def view_home(request):
    return render(request, 'claims/index.html', {'headlines': Claim.objects.all()[:2], 'sub_headlines': Claim.objects.all()[2:15]})
