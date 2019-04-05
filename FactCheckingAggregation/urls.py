"""FactCheckingAggregation URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import handler404, handler500, handler400, handler403

from claims import views as claims_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('claims.urls', namespace='claims')),
    path('comments/', include('comments.urls', namespace='comments')),
    path('replies/', include('replies.urls', namespace='replies')),
    path('tweets/', include('tweets.urls', namespace='tweets')),
    path('users/', include('users.urls', namespace='users')),
    path('search/', include('search.urls', namespace='search')),
    path('auth/', include('social_django.urls', namespace='social')),
    path('contact_us/', include('contact_us.urls', namespace='contact_us')),
    path('logger/', include('logger.urls', namespace='logger')),
    path('analytics/', include('analytics.urls', namespace='analytics')),
]

# handler404 = claims_views.handler_404
# handler500 = claims_views.handler_500
# handler400 = claims_views.handler_400
# handler403 = claims_views.handler_403
