from django.http import HttpResponse
from django.shortcuts import render
from .models import Claim
from django.views.decorators.csrf import csrf_protect, csrf_exempt
import json

# add a new claims to system.
@csrf_exempt
def add_claim(request):
    #TODO: check for a post request
    # request should contain body with all details.

    body = request.POST.dict()
    claim = Claim(
        title=body['title'],
        category=body['category'],
        authentic_grade = 1
    )

    claim.save()
    return HttpResponse(status=204)


def view_claim(request):
    return render(request, 'claims/claim.html', {
        'claim': 'Did CNN’s Don Lemon Say the ‘Biggest Terror Threat in This Country Is White Men’?',
        'authenticity_grade': 'True'
    })
