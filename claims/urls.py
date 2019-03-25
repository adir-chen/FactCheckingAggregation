from django.urls import path
from . import views

app_name = "claims"
urlpatterns = [
    path('add_claim', views.add_claim, name='add_claim'),
    path('edit_claim', views.edit_claim, name='edit_claim'),
    path('delete_claim', views.delete_claim, name='delete_claim'),
    path('report_spam', views.report_spam, name='report_spam'),
    path('download_claims', views.download_claims, name='download_claims'),
    path('', views.view_home, name='home_page'),
    path('claim/<int:claim_id>', views.view_claim, name='view_claim'),
    path('logout', views.logout_view, name='logout_view'),
    path('add_claim_page', views.add_claim_page, name='add_claim_page'),
    path('export_claims_page', views.export_claims_page, name='export_claims_page'),
    path('post_claims_tweets_page', views.post_claims_tweets_page, name='post_claims_tweets_page'),
    path('about', views.about_page, name='about'),
]
