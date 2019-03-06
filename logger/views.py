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
    if not user_id:
        user_id = -1
        username = 'Unknown'
    log = Logger(user_id=user_id,
                 username=username,
                 action=action,
                 result=result)
    log.save()


def check_duplicate_log_for_user(user_id, action):
    return len(Logger.objects.filter(user_id=user_id, action__icontains=action)) > 0
