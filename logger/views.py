import datetime

from django.http import Http404
from django.shortcuts import render
from logger.models import Logger


def view_log(request):
    if not request.user.is_superuser:
        raise Http404("Permission denied")
    return render(request, 'logger/logger.html', {'logger': Logger.objects.all()})


def save_log_message(user_id, username, message):
    log = Logger(date=datetime.datetime.today(), activity='User with id ' + str(user_id) + '- ' + username +
                                                          ' ' + message)
    log.save()
