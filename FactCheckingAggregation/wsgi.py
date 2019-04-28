"""
WSGI config for FactCheckingAggregation project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os
import sys
from django.core.wsgi import get_wsgi_application
path = '/home/wtfact/Documents/FactCheckingAggregation'
sys.path.append(path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FactCheckingAggregation.settings')
application = get_wsgi_application()
