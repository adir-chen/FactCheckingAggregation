from django.urls import path
from . import views

app_name = "replies"
urlpatterns = [
    path('add_reply', views.add_reply, name='add_reply'),
    path('edit_reply', views.edit_reply, name='edit_reply'),
    path('delete_reply', views.delete_reply, name='delete_reply'),
]
