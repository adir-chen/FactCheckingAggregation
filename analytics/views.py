from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render
from analytics.GoogleAPI.AnalyticReports import get_report_view_by_time, get_report_top_n_claims
from claims.views import get_claim_by_id
import json
import datetime
from dateutil.relativedelta import relativedelta


# This function returns analytics page
def view_analytics(request):
    if not request.user.is_superuser or request.method != 'GET':
        raise Http404("Permission denied")
    today = datetime.date.today()
    past = today - relativedelta(months=3)
    start_date = "{:04d}-{:02d}-{:02d}".format(past.year, past.month, past.day)
    end_date = "{:04d}-{:02d}-{:02d}".format(today.year, today.month, today.day)
    months_reports = get_report_view_by_time(start_date=start_date, end_date=end_date,
                                             dimensions='ga:year, ga:month')
    days_reports = get_report_view_by_time(start_date=start_date, end_date=end_date,
                                           dimensions='ga:year, ga:month, ga:day')
    return render(request,
                  'analytics/analytics.html',
                  {'reports_monthly': months_reports,
                   'reports_days': days_reports,
                   'current_date': "{:04d}-{:02d}".format(today.year,
                                                          today.month)})


def view_analytics_customized(request):
    data = request.POST.dict()
    reports_1 = get_report_view_by_time(start_date=data['start_date'],
                                        end_date=data['end_date'],
                                        dimensions=data['dimensions'])
    return HttpResponse(
        json.dumps([reports_1]),
        content_type="application/json"
    )


def view_top_n_claims(request):
    data = request.POST.dict()
    reports = get_report_top_n_claims(num_of_claims=int(data['n']),
                                      start_date=data['start_date'],
                                      end_date=data['end_date'])
    results, reports_json = ([] for i in range(2))
    for [claim_id, views] in reports:
        claim = get_claim_by_id(claim_id)
        if claim is None:
            continue
        results.append([claim_id, claim, views])

    for report in results:
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
