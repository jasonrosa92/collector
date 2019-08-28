from django.conf import settings
#from django.contrib.sites.models import Site

MONETARY_LOCALE = getattr(settings, 'MONETARY_LOCALE', '')
THOUSANDS_SEPARATOR = getattr(settings, 'THOUSANDS_SEPARATOR', '')

