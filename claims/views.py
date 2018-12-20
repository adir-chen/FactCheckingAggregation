from django.shortcuts import render
from comments.views import add_comment, export_to_csv
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
            authentic_grade = -1
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


def view_claim(request):
    return render(request, 'claims/claim.html', {
        'claim': 'Did CNN’s Don Lemon Say the ‘Biggest Terror Threat in This Country Is White Men’?',
        'authenticity_grade': 'True'
    })
