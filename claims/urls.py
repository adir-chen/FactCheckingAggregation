from django.urls import path
from . import views

app_name = "claims"
urlpatterns = [
    path('', views.view_home, name='home_page'),
    path('add_claim', views.add_claim, name='add_claim'),
    # view_claim should have: data="claim_id:#"
    path('claim/<int:claim_id>', views.view_claim, name='view_claim'),
    path('logout', views.logout_view, name='logout_view'),
    path('add_claim_page', views.add_claim_page, name='add_claim_page'),
    path('export_claims_page', views.export_claims_page, name='export_claims_page'),
    path('edit_claim', views.edit_claim, name='edit_claim'),
    path('delete_claim', views.delete_claim, name='delete_claim'),
    path('about', views.about_page, name='about'),
    path('report_spam', views.report_spam, name='report_spam'),
]
