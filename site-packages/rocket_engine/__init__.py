import os
import sys


from django.core.handlers.wsgi import WSGIHandler
from django.core import signals

on_appengine_remote = os.getenv('SERVER_SOFTWARE','')\
                        .startswith('Google App Engine')

on_appengine = on_appengine_remote
os.path.abspath(os.curdir)

PROJECT_DIR = os.path.abspath(os.getcwd())


def get_appengine_sdk_path():
    typical_sdk_paths = [
        os.environ.get('APP_ENGINE_SDK',""),
        '/usr/local/google_appengine',
        '/Applications/GoogleAppEngineLauncher.app/Contents/Resources/GoogleAppEngine-default.bundle/Contents/Resources/google_appengine'
    ] + os.environ.get('PATH', '').split(os.pathsep)

    # List of files which will be used as a test for SQK lookup.
    is_appengine_sdk = lambda path: all([
      x in os.listdir(path) for x in [
          'appcfg.py',
          'dev_appserver.py',
          'google'
      ]
    ])

    for path in typical_sdk_paths:
        if os.path.exists(path) and is_appengine_sdk(path):
            return path

    sys.stderr.write(
        'The Google App Engine SDK could not be found!\n'
        "Make sure it's accessible via your PATH "
        "environment and called google_appengine.\n"
    )
    sys.exit(1)


def setup_appendine_sdk():
    try:
        import dev_appserver
    except ImportError:

        sdk_path = get_appengine_sdk_path()
        sys.path.append(sdk_path)

        import dev_appserver

        sys.path.extend(dev_appserver.EXTRA_PATHS)
        sys.path.extend(dev_appserver.GOOGLE_SQL_EXTRA_PATHS)


def path_appendine_sdk():

    if not os.environ.get('DJANGO_SETTINGS_MODULE'):
        os.environ.update({'DJANGO_SETTINGS_MODULE': 'settings'})

    if not on_appengine_remote:
        # add SQLlite to allowed modules
        from google.appengine.tools import dev_appserver
        from google.appengine import dist27
        dist27.MODULE_OVERRIDES = []
        dev_appserver.HardenedModulesHook._WHITE_LIST_C_MODULES.extend(
            ('parser', '_ssl', '_io', '_sqlite3', 'os', '_os', 'tempfile'))

        dev_appserver.HardenedModulesHook._MODULE_OVERRIDES['os'] = os.__dict__
        dev_appserver.HardenedModulesHook._PY27_ALLOWED_MODULES.append('os')
        dev_appserver.HardenedModulesHook._HardenedModulesHook__PY27_OPTIONAL_ALLOWED_MODULES = {}
        dev_appserver.FakeFile.NOT_ALLOWED_DIRS = set([])
        dev_appserver.FakeFile.IsFileAccessible = staticmethod(
            lambda *args, **kwargs: True
        )
    else:

        # loogging exceptions hook
        from .utils import log_traceback
        signals.got_request_exception.connect(log_traceback)

        # add production site
        import site
        site.addsitedir(os.path.join(PROJECT_DIR, 'appengine_libs'))


if not on_appengine_remote:
    setup_appendine_sdk()
path_appendine_sdk()

wsgi = WSGIHandler()
