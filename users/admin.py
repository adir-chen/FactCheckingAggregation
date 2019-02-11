from django.contrib import admin

from users.models import UsersImages, Scrapers
from users.models import UsersReputations

admin.site.register(UsersImages)
admin.site.register(UsersReputations)
admin.site.register(Scrapers)