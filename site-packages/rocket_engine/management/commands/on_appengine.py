import os

from django.conf import settings, Settings
from django.utils import importlib

from django.core.management.base import BaseCommand
from django.core import management
from django import db

import rocket_engine


class Command(BaseCommand):
    help = 'Runs a command with access to the remote App Engine production ' \
           'server (e.g. manage.py on_appengine shell)'
    args = 'remotecommand'

    def reload_settings(self):
        settings_module = os.environ["DJANGO_SETTINGS_MODULE"]

        mod = importlib.import_module(settings_module)
        reload(mod)
        settings._wrapped = Settings(settings_module)

    def handle(self, *args, **kwargs):
        rocket_engine.on_appengine = True

        self.reload_settings()

        db.connections = db.utils.ConnectionHandler(settings.DATABASES)
        db.router = db.utils.ConnectionRouter(settings.DATABASE_ROUTERS)

        management.call_command(*args, **kwargs)
