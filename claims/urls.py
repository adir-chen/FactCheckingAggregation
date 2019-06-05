from django.urls import path
from . import views

app_name = "claims"
urlpatterns = [
    path('add_claim', views.add_claim, name='add_claim'),
    path('edit_claim', views.edit_claim, name='edit_claim'),
    path('delete_claim', views.delete_claim, name='delete_claim'),
    path('report_spam', views.report_spam, name='report_spam'),
    path('download_claims', views.download_claims, name='download_claims'),
    path('merging_claims', views.merging_claims, name='merging_claims'),
    path('switching_claims', views.switching_claims, name='switching_claims'),
    path('delete_suggestion_for_merging_claims', views.delete_suggestion_for_merging_claims,
         name='delete_suggestion_for_merging_claims'),
    path('', views.view_home, name='home_page'),
    path('claims', views.view_claims, name='view_claims'),
    path('claim/<int:claim_id>', views.view_claim, name='view_claim'),
    path('logout', views.logout_view, name='logout_view'),
    path('add_claim_page', views.add_claim_page, name='add_claim_page'),
    path('export_claims_page', views.export_claims_page, name='export_claims_page'),
    path('post_claims_tweets_page', views.post_claims_tweets_page, name='post_claims_tweets_page'),
    path('merging_claims_page', views.merging_claims_page, name='merging_claims_page'),
    path('about', views.about_page, name='about'),
    path('update_tags_for_all_claims_and_comments', views.update_tags_for_all_claims_and_comments,
         name='update_tags_for_all_claims_and_comments'),
]
