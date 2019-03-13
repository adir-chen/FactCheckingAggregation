from django.http import Http404
from django.shortcuts import render
from analytics.GoogleAPI.AnalyticReports import getReport_viewsByMonth, getReport_DaysOfWeek


# This function returns analytics page
def view_analytics(request):
    if not request.user.is_superuser:
        raise Http404("Permission denied")
    reports_1 = getReport_viewsByMonth(start_date='2019-01-01', end_date='today')
    reports_2 = getReport_DaysOfWeek(start_date='2019-01-01', end_date='today')
    return render(request, 'analytics/analytics.html', {'reports_monthly': reports_1, 'reports_days': reports_2})