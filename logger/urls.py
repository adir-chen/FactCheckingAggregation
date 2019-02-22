from django.urls import path
from . import views

app_name = "logger"
urlpatterns = [
    path('view_log', views.view_log, name='view_log')
]
