from django.urls import path

from . import views

app_name = "comments"
urlpatterns =[
    path('add_comment', views.add_comment, name='add_comment'),
    path('up_vote', views.up_vote, name='up_vote'),
    path('down_vote', views.down_vote, name='down_vote'),
]
