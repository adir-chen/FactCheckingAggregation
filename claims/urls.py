from django.urls import path

from . import views

urlpatterns =[
    path('add_claim', views.add_claim, name='add_claim'),
    path('claim', views.view_claim, name='view_claim'),
]
