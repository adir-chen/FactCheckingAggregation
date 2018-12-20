from django.urls import path

from . import views

urlpatterns =[
    path('', views.view_home, name='home_page'),
    path('add_claim', views.add_claim, name='add_claim'),
    # view_claim should have: data="claim_id:#"
    path('claim/<int:id>', views.view_claim, name='view_claim'),
]
