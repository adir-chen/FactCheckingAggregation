from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render
from analytics.GoogleAPI.AnalyticReports import get_report_view_by_time, get_report_top_n_claims
from claims.views import get_claim_by_id
from dateutil.relativedelta import relativedelta
from logger.views import save_log_message
import calendar
import json
import datetime


# This function returns analytics page
def view_analytics(request):
    if not request.user.is_superuser or request.method != 'GET':
        raise Http404("Permission denied")
    today = datetime.date.today()
    past = today - relativedelta(months=3)
    start_date_month = "{:04d}-{:02d}-{:02d}".format(past.year, past.month, past.day)
    end_date_month = "{:04d}-{:02d}-{:02d}".format(today.year, today.month, today.day)
    start_date_day = "{:04d}-{:02d}-{:02d}".format(today.year, today.month, 1)
    end_date_day = "{:04d}-{:02d}-{:02d}".format(today.year, today.month,
                                                 calendar.monthrange(today.year, today.month)[1])
    months_reports = get_report_view_by_time(start_date=start_date_month, end_date=end_date_month,
                                             dimensions='ga:year, ga:month')
    days_reports = get_report_view_by_time(start_date=start_date_day, end_date=end_date_day,
                                           dimensions='ga:year, ga:month, ga:day')
    return render(request,
                  'analytics/analytics.html',
                  {'reports_months': months_reports,
                   'reports_days': days_reports,
                   'past_date': "{:04d}-{:02d}".format(past.year,
                                                       past.month),
                   'current_date': "{:04d}-{:02d}".format(today.year,
                                                          today.month)})


def view_customized_analytics(request):
    customized_analytics_info = request.POST.dict()
    valid_customized_analytics_info, err_msg = check_if_customized_analytics_is_valid(customized_analytics_info)
    if not valid_customized_analytics_info:
        save_log_message(request.user.id, request.user.username,
                         'Viewing customized analytics. Error: ' + err_msg)
        raise Exception(err_msg)
    reports = get_report_view_by_time(start_date=customized_analytics_info['start_date'],
                                      end_date=customized_analytics_info['end_date'],
                                      dimensions=customized_analytics_info['dimensions'])
    return HttpResponse(
        json.dumps([reports]),
        content_type="application/json"
    )


def check_if_customized_analytics_is_valid(top_claims_info):
    err = ''
    if 'dimensions' not in top_claims_info or not top_claims_info['dimensions']:
        err += 'Missing value for dimensions'
    else:
        err = check_valid_dates(top_claims_info)
    if len(err) > 0:
        return False, err
    return True, err


def check_valid_dates(info):
    err = ''
    if 'start_date' not in info or not info['start_date']:
        err += 'Missing value for starting date'
    elif 'end_date' not in info or not info['end_date']:
        err += 'Missing value for ending date'
    elif not datetime.datetime.strptime(info['end_date'], "%Y-%m-%d") >= \
            datetime.datetime.strptime(info['start_date'], "%Y-%m-%d"):
        err += 'Ending date should be greater or equal to starting date'
    return err


def view_top_n_claims(request):
    top_claims_info = request.POST.dict()
    valid_top_claims_info, err_msg = check_if_top_claims_is_valid(top_claims_info)
    if not valid_top_claims_info:
        save_log_message(request.user.id, request.user.username,
                         'Viewing top n claims. Error: ' + err_msg)
        raise Exception(err_msg)
    reports = get_report_top_n_claims(num_of_claims=int(top_claims_info['n']),
                                      start_date=top_claims_info['start_date'],
                                      end_date=top_claims_info['end_date'])
    results, reports_json = ([] for i in range(2))
    for [claim_id, views] in reports:
        claim = get_claim_by_id(claim_id)
        if claim is None:
            continue
        results.append([claim, views])
        if len(results) == int(top_claims_info['n']):
            break

    for report in results:
        reports_json.append({
            'claim': get_claim_as_json(report[0]),
            'views': report[1]
        })
    return JsonResponse({
        'reports': reports_json
    })


def check_if_top_claims_is_valid(top_claims_info):
    err = ''
    if 'n' not in top_claims_info or not top_claims_info['n']:
        err += 'Missing value for num of claims'
    elif not top_claims_info['n'].isdigit():
        err += 'Incorrect format for num of claims (integer)'
    elif not (1 <= int(top_claims_info['n']) <= 10):
        err += 'Num of claims should be between 1 - 10'
    else:
        err = check_valid_dates(top_claims_info)
    if len(err) > 0:
        return False, err
    return True, err


def get_claim_as_json(claim):
    claim_json = {
        'id': claim.id,
        'claim': claim.claim,
    }
    return claim_json
