from django.urls import path
from . import views

app_name = "analytics"
urlpatterns = [
    path('', views.view_analytics_default, name='view_analytics_default'),
    path('custom1', views.view_analytics_customized, name='view_analytics_customized'),
    path('custom2', views.view_analytics_customized_days, name='view_analytics_customized_days'),
    path('top_claims', views.view_N_top_claims, name='view_N_top_claims'),


]
