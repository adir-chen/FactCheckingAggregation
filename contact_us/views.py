from datetime import datetime
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import render
from django.core.mail import send_mail
from validate_email import validate_email
from logger.models import Logger
from logger.views import save_log_message
from ipware import get_client_ip
from claims.views import return_get_request_to_user
import json


# This function return an HTML page for contact us
def contact_us_page(request):
    return render(request, 'contact_us/contact_us.html')


# This function sends an email from a website user
def send_email(request):
    if request.method != "POST":
        raise PermissionDenied
    ip = get_client_ip(request)
    if ip[0] is None:
        ip = 'Unknown IP Address'
    else:
        ip = str(ip[0])
    mail_info = request.POST.dict()
    mail_info['ip'] = ip
    valid_mail, err_msg = check_if_email_is_valid(mail_info)
    if not valid_mail:
        save_log_message(request.user.id, request.user.username,
                         'Sending an email from ip - ' + ip + '. Error: ' + err_msg)
        return HttpResponse(json.dumps(err_msg), content_type='application/json', status=404)
    send_mail(mail_info['user_email'] + ': ' + mail_info['subject'],
              mail_info['description'],
              'wtfacteam@gmail.com',
              ['wtfacteam@gmail.com'])
    save_log_message(request.user.id, request.user.username, 'Sending an email from ip - ' + ip)
    return contact_us_page(return_get_request_to_user(request.user))


# This function checks if a given email is valid, i.e. the email has all the fields with the correct format.
# The function returns true in case the email is valid, otherwise false and an error
def check_if_email_is_valid(email_info):
    err = ''
    if 'user_email' not in email_info or not email_info['user_email']:
        err += 'Missing value for user email'
    elif not validate_email(email_info['user_email']):
        err += 'Invalid email address'
    elif 'subject' not in email_info or not email_info['subject']:
        err += 'Missing value for subject'
    elif 'description' not in email_info or not email_info['description']:
        err += 'Missing value for description'
    elif check_for_spam(email_info['ip']):
        err += 'Detected as spam'
    if len(err) > 0:
        return False, err
    return True, err


# This function checks for spam emails from a user
def check_for_spam(ip):
    return len(Logger.objects.filter(date__date=datetime.today(), action__icontains=ip)) >= 5

