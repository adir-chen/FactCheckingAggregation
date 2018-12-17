from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def index(request):
    #return HttpResponse(request.body)
    return render(request, 'Intensely/index.html')