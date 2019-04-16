from functools import reduce
from django.http import Http404, HttpResponse
from django.shortcuts import render
from logger.models import Logger
from datetime import datetime
from django.db.models import Q
import operator
import json
import csv


# This function returns a HTML for the log page
def view_log(request):
    if not request.user.is_superuser or request.method != "GET":
        raise Http404("Permission denied")
    return render(request, 'logger/logger.html', {'logger': Logger.objects.all().order_by('-id')})


# This function saves a new log in the logger
def save_log_message(user_id, username, action, result=False):
    if not user_id:
        user_id = -1
        username = 'Unknown'
    log = Logger(user_id=user_id,
                 username=username,
                 action=action,
                 result=result)
    log.save()


# This function checks for a duplicate log (action) of a given user's id
def check_duplicate_log_for_user(user_id, action):
    return len(Logger.objects.filter(user_id=user_id, action__icontains=action)) > 0


# This function returns a csv which contains all the details of the logger in the website
def export_to_csv(request):
    if not request.user.is_superuser or request.method != "POST":
        save_log_message(request.user.id, request.user.username,
                         'Exporting website logger to a csv. Error: user does not have permissions')
        raise Http404("Permission denied")
    csv_fields = request.POST.dict()
    valid_csv_fields, err_msg = check_if_csv_fields_are_valid(csv_fields)
    if not valid_csv_fields:
        save_log_message(request.user.id, request.user.username,
                         'Exporting website logger to a csv. Error: ' + err_msg)
        return HttpResponse(json.dumps(err_msg), content_type='application/json', status=404)
    actions_to_export = request.POST.getlist('actions_to_export[]')
    date_start = datetime.strptime(csv_fields['date_start'], '%d/%m/%Y').date()
    date_end = datetime.strptime(csv_fields['date_end'], '%d/%m/%Y').date()
    error = request.POST.get('errors')
    valid_actions_list, err_msg = check_if_actions_list_valid(actions_to_export)
    if not valid_actions_list:
        save_log_message(request.user.id, request.user.username,
                         'Exporting website logger to a csv. Error: ' + err_msg)
        return HttpResponse(json.dumps(err_msg), content_type='application/json', status=404)
    df_logger = create_df_for_logger(actions_to_export, error, date_start, date_end)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="logger.csv"'
    writer = csv.writer(response)
    writer.writerow(['Date', 'User Id', 'Username', 'Action', 'Result'])
    for index, row in df_logger.iterrows():
        logger_info = []
        for col in df_logger:
            logger_info.append(row[col])
        writer.writerow(logger_info)
    save_log_message(request.user.id, request.user.username,
                     'Exporting website logger to a csv', True)
    return response


# This function checks if given csv fields are valid, i.e. the csv fields have all the fields with the correct format.
# The function returns true in case csv fields are valid, otherwise false and an error
def check_if_csv_fields_are_valid(csv_fields):
    from comments.views import convert_date_format
    err = ''
    if 'actions_to_export[]' not in csv_fields:
        err += 'Missing values for actions'
    elif 'errors' not in csv_fields:
        err += 'Missing value for error choice'
    elif 'date_start' not in csv_fields:
        err += 'Missing value for date start'
    elif 'date_end' not in csv_fields:
        err += 'Missing value for date end'
    else:
        err = convert_date_format(csv_fields, 'date_start')
        if len(err) == 0:
            err = convert_date_format(csv_fields, 'date_end')
    if len(err) > 0:
        return False, err
    return True, err


# This function checks if exported actions are valid,
# The function returns true in case they are valid, otherwise false and an error
def check_if_actions_list_valid(actions_to_export):
    err = ''
    valid_actions_to_export = ["Adding a new claim", "Adding a new comment", "Adding a new tweet",
                               "Editing a claim", "Editing a comment",
                               "Deleting a claim", "Deleting a comment", "Deleting a tweet",
                               "Reporting a claim as spam", "Up voting a comment", "Down voting a comment",
                               "Sending an email"]
    for action in actions_to_export:
        if action not in valid_actions_to_export:
            err += 'Action ' + str(action) + ' is not valid'
            return False, err
    return True, ''


# This function creates a df which contains all the details of the logger in the website
def create_df_for_logger(actions_to_export, error, date_start, date_end):
    import pandas as pd
    df_logger = pd.DataFrame(columns=['Date', 'User Id', 'Username', 'Action', 'Result'])
    dates, users_ids, users_names, actions, results = ([] for i in range(5))
    query = reduce(operator.or_, (Q(action__icontains=action) for action in actions_to_export))
    log_result = Logger.objects.filter(query)
    if error == 'without_errors':
        log_result = log_result.exclude(action__icontains='Error')
    elif error == 'just_errors':
        log_result = log_result.filter(action__icontains='Error')
    log_result = log_result.order_by('-id')
    for log in log_result:
        dates.append(log.date.date())
        users_ids.append(log.user_id)
        users_names.append(log.username)
        actions.append(log.action)
        if log.result:
            results.append('Success')
        else:
            results.append('Failure')
    df_logger['Date'] = dates
    df_logger['User Id'] = users_ids
    df_logger['Username'] = users_names
    df_logger['Action'] = actions
    df_logger['Result'] = results
    df_logger = df_logger[(df_logger['Date'] >= date_start) &
                          (df_logger['Date'] <= date_end)]
    return df_logger
