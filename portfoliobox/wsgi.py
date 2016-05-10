"""
WSGI config for portfoliobox project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""
import django

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "portfoliobox.settings")

from django.core.wsgi import get_wsgi_application
from whitenoise.django import DjangoWhiteNoise

application = django.core.handlers.wsgi.WSGIHandler()
application = get_wsgi_application()
application = DjangoWhiteNoise(application)
