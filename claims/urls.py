from django.urls import path

from . import views

urlpatterns =[
    path('add_claim', views.add_claim, name='add_claim'),
    # view_claim should have: data="claim_id:#"
    path('claim', views.view_claim, name='view_claim'),
]
