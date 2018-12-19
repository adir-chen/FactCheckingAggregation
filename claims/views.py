from comments.views import add_comment
from users.views import get_user_id_by_username
from .models import Claim


# add a new claim to the website.
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


def get_all_claims():
    Claim.objects.all()


def reset_claims():
    Claim.objects.all().delete()
