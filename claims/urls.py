from django.urls import path
from . import views

app_name = "claims"
urlpatterns =[
    path('', views.view_home, name='home_page'),
    path('add_claim', views.add_claim, name='add_claim'),
    # view_claim should have: data="claim_id:#"
    path('claim/<int:claim_id>', views.view_claim, name='view_claim'),
    path('logout', views.logout_view, name='logout_view'),
    path('add_claim_page', views.add_claim_page, name='add_claim_page'),
    path('edit_claim', views.edit_claim, name='edit_claim'),
    path('delete_claim', views.delete_claim, name='delete_claim'),
]
