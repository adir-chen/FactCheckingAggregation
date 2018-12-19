from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from claims.views import reset_claims
from users.views import add_all_scrapers, reset_users


def index(request):
    #return HttpResponse(request.body)
    reset_users()
    reset_claims()
    add_all_scrapers()
    return render(request, 'Intensely/index.html')