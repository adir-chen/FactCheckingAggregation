from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import render
from claims.models import Claim
from django.core.paginator import Paginator


# This function returns all the claims that are found in a search
def search(request):
    if request.method != "GET":
        raise PermissionDenied
    keywords = ' '.join([keyword.strip() for keyword in request.GET.get('search_keywords').split()])
    search_results = Claim.objects.filter(Q(claim__icontains=keywords) | Q(tags__icontains=keywords) |
                                          Q(user__username__icontains=keywords)).order_by('-id')
    page = request.GET.get('page')
    paginator = Paginator(search_results, 24)
    return render(request, 'search/search.html', {'search_result': paginator.get_page(page)})
