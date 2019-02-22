from django.http import Http404
from django.shortcuts import render
from django.core.mail import send_mail
from validate_email import validate_email


# This function sends an email from a website user
from logger.views import save_log_message


def send_email(request):
    if request.method == "POST":
        mail_info = request.POST.dict()
        valid_mail, err_msg = check_if_email_is_valid(mail_info)
        if not valid_mail:
            save_log_message(request.user.id, request.user.username,
                             ' failed send an email. Error: ' + err_msg)
            raise Exception(err_msg)
        send_mail(mail_info['user_email'] + ': ' + mail_info['subject'],
                  mail_info['description'],
                  'wtfactnews@gmail.com',
                  ['wtfactnews@gmail.com'])
        save_log_message(request.user.id, request.user.username, ' send an email successfully')
        return contact_us_page(request)
    raise Http404("Invalid method")


# This function checks if a given e-mail is valid, i.e. the e-mail has all the fields with the correct format.
# The function returns true in case the e-mail is valid, otherwise false and an error
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
    if len(err) > 0:
        return False, err
    return True, err


# This function return an HTML page for sending a new e-mail
def contact_us_page(request):
    return render(request, 'contact_us/contact_us.html')
