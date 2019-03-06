from django.shortcuts import render
from analytics.GoogleAPI.AnalyticReports import getReport_viewsByMonth, getReport_DaysOfWeek


# This function returns analytics page
def view_analytics(request):
    reports1 = getReport_viewsByMonth(start_date='2019-01-01', end_date='today')
    reports2 = getReport_DaysOfWeek(start_date='2019-01-01', end_date='today')
    return render(request, 'analytics/analytics.html', {'reports_monthly': reports1, 'reports_days': reports2})