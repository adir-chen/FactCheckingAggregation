from django.http import Http404
from django.shortcuts import render
from logger.models import Logger


# This function returns log page
def view_log(request):
    if not request.user.is_superuser:
        raise Http404("Permission denied")
    return render(request, 'logger/logger.html', {'logger': Logger.objects.all()})


# This function saves a new log in the logger
def save_log_message(user_id, username, action, result=False):
    log = Logger(user_id=user_id,
                 username=username,
                 action=action,
                 result=result)
    log.save()
