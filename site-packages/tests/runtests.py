#!/usr/bin/env python
import os
import sys
from django.conf import settings

parent = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..")
)

sys.path.insert(0, parent)

if not settings.configured:
    settings.configure(
        DEFAULT_FILE_STORAGE='rocket_engine.storage.BlobStorage',
        DATABASE_ENGINE='sqlite3',
        INSTALLED_APPS=[
            'rocket_engine',
            'tests',
        ]
    )

from django.test.simple import run_tests


def runtests():
    failures = run_tests(['tests'], verbosity=1, interactive=True)
    sys.exit(failures)


if __name__ == '__main__':
    runtests()
