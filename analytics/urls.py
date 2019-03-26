from django.urls import path
from . import views

app_name = "analytics"
urlpatterns = [
    path('', views.view_analytics, name='view_analytics'),
    path('view_analytics_customized', views.view_analytics_customized, name='view_analytics_customized'),
    path('view_top_n_claims', views.view_top_n_claims, name='view_top_n_claims'),
]
