from .... import on_appengine
from django.core.exceptions import ImproperlyConfigured

if on_appengine:
    from google.storage.speckle.python.django.backend.base import *
else:
    raise ImproperlyConfigured(
        "Using remote CloudSQL as a local backend. Check your settings.py file."
    )
