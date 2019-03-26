import json
import datetime
import calendar

from django.http import Http404, HttpResponse, JsonResponse

from django.shortcuts import render
from analytics.GoogleAPI.AnalyticReports import getReport_viewsByMonth, getReport_viewsByDays,getReport_NMostViewdCalims

from claims.views import get_claim_by_id

# This function returns analytics page
def view_analytics_default(request):
    reports_1 = getReport_viewsByMonth(start_date='2019-01-01', end_date='today')
    reports_2 = getReport_viewsByDays(start_date='2019-03-01', end_date='today')
    return view_analytics(request, reports_1, reports_2)

def view_analytics_customized(request):
    # print("???")
    # print(request.POST)
    data = request.POST.dict()
    reports_1 = getReport_viewsByMonth(start_date=data['start_date'], end_date=data['end_date'])
    # reports_2 = getReport_DaysOfWeek(start_date=data['start_date'], end_date=data['end_date'])
    return HttpResponse(
        json.dumps([reports_1]),
        content_type="application/json"
    )
    # return view_analytics(request, data['start_date'], data['end_date'])


def view_analytics_customized_days(request):
    data = request.POST.dict()
    # reports_1 = getReport_viewsByMonth(start_date=data['start_date'], end_date=data['end_date'])
    reports_2 = getReport_viewsByDays(start_date=data['start_date'], end_date=data['end_date'])
    return HttpResponse(
        json.dumps([reports_2]),
        content_type="application/json"
    )
    # return view_analytics(request, data['start_date'], data['end_date'])

def view_analytics(request, reports_1, reports_2):
    # if not request.user.is_superuser:
    #     raise Http404("Permission denied")
    now = datetime.datetime.now()

    date =  "" + str(now.year) +\
            '-' + ('0' if now.month<10 else '') + str(now.month)
            # + '-' + ('0' if now.day<10 else '') + str(now.day)
    return render(request, 'analytics/analytics.html', {'reports_monthly': reports_1, 'reports_days': reports_2, 'current_date': date})


def get_N_top_claims(n, start_date, end_date):
    report = getReport_NMostViewdCalims(start_date =start_date, end_date=end_date)
    results = []
    i=0
    for [claim_id, views] in report:
        claim = get_claim_by_id(claim_id)
        if claim is None:
            continue
        results.append([claim_id, claim, views])
        i+=1
        if i == n:
            break
    return results


def view_N_top_claims(request):
    data = request.POST.dict()
    reports = get_N_top_claims(n=int(data['n']), start_date=data['start_date'], end_date=data['end_date'])
    reports_json = []
    for report in reports:
        reports_json.append({
            'claim_id': report[0],
            'claim': get_claim_as_json(report[1]),
            'views': report[2]
        })
    return JsonResponse({
        'reports': reports_json
    })

def get_claim_as_json(claim):
    claim_json = {
        'claim': claim.claim,
        'category': claim.category,
        'tags': claim.tags
    }
    return claim_json

#     user = models.ForeignKey(User, on_delete=models.CASCADE)
# claim = models.CharField(max_length=150)
# category = models.CharField(max_length=50)
# tags = models.CharField(max_length=250)
# authenticity_grade = models.IntegerField()
# image_src = models.CharField(max_length=1000)
# timestamp = models.DateTimeField(default=timezone.now)