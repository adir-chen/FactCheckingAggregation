from django.db.models import Q
from django.http import Http404
from django.shortcuts import render
from claims.models import Claim
from claims.views import get_users_images_for_claims
from django.core.paginator import Paginator


# This function returns all the claims that are found in a search
def search(request):
    if request.method != "GET":
        raise Http404("Permission denied")
    keywords = request.GET.get('search_keywords')
    claims = Claim.objects.filter(Q(claim__icontains=keywords) | Q(tags__icontains=keywords) |
                                  Q(user__username__icontains=keywords)).order_by('-id')
    search_result = list(get_users_images_for_claims(claims).items())
    page = request.GET.get('page')
    paginator = Paginator(search_result, 24)
    return render(request, 'search/search.html', {'search_result': paginator.get_page(page)})
