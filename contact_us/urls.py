from django.urls import path
from . import views

app_name = "contact_us"
urlpatterns = [
    path('send_email', views.send_email, name='send_email'),
    path('contact_us_page', views.contact_us_page, name='contact_us_page'),
]
