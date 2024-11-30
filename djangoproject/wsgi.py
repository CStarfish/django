"""
WSGI config for djangoproject project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoproject.settings')
os.environ['MAPBOX_ACCESS_TOKEN'] = 'pk.eyJ1IjoiY3N0YXJmaXNoIiwiYSI6ImNtNDNndGhoZzBidnEyaXE1NXVjaW0zMzcifQ.C86l5PThLpBfatE4yeoIxw'

application = get_wsgi_application()
