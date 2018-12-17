from django.contrib import admin
from .models import User, Claim, Comment


admin.site.register(User)
admin.site.register(Claim)
admin.site.register(Comment)
