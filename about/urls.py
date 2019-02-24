from django.urls import path
from . import views

app_name = "about"
urlpatterns =[
    path('about_page', views.about_page, name='about_page'),
]