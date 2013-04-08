import os
import sys
import shutil
import shlex
import subprocess

from google.appengine.tools import appcfg
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.urlresolvers import get_callable

from ... import PROJECT_DIR

PRE_UPDATE_HOOK = getattr(
    settings, 'APPENGINE_PRE_UPDATE', 'appengine_hooks.pre_update'
)
POST_UPDATE_HOOK = getattr(
    settings, 'APPENGINE_POST_UPDATE', 'appengine_hooks.post_update'
)
APPENGINE_VIRTUALENV = getattr(
    settings, 'APPENGINE_VIRTUALENV', '.appengine'
)
APPENGINE_REQUIREMENTS_FILE = getattr(
    settings, 'APPENGINE_REQUIREMENTS_FILE', 'requirements.txt'
)


requirements_file = os.path.join(
    PROJECT_DIR, APPENGINE_REQUIREMENTS_FILE
)

virtualenv = os.path.join(PROJECT_DIR, APPENGINE_VIRTUALENV)
virtualenv_cache = os.path.join(virtualenv, 'cache')
virtualenv_appengine_libs = os.path.join(virtualenv, 'appengine_libs')

rocket_engine_path = os.path.abspath(
    os.path.join(__file__, '../../../')
)

appengine_libs = os.path.join(PROJECT_DIR, 'appengine_libs')
appengine_rocket_engine = os.path.join(PROJECT_DIR, 'rocket_engine')

pip_command = os.path.join(virtualenv, 'bin', 'pip')
python_command = os.path.join(virtualenv, 'bin', 'python')


class Command(BaseCommand):
    """Wrapper for appcfg.py with pre-update and post-update hooks"""

    help = 'Calls appcfg.py for the current project.'
    args = '[any options that normally would be applied to appcfg.py]'

    def install_requirements(self):

        if not os.path.exists(virtualenv):
            print "\nCreating environment, ...",
            sys.stdout.flush()
            subprocess.Popen(
                shlex.split('virtualenv %s --distribute' % virtualenv),
                stdout=subprocess.PIPE
            ).wait()
            print "done.\n"

        if not os.path.exists(virtualenv_appengine_libs):
            os.mkdir(virtualenv_appengine_libs)

        shutil.copytree(
            rocket_engine_path,
            os.path.join(PROJECT_DIR, 'rocket_engine')
        )

        if os.path.exists(requirements_file):
            print "\nPreparing requirements, ...",
            sys.stdout.flush()
            subprocess.Popen(
                shlex.split(
                    "%s %s install --requirement=%s --download-cache=%s --target=%s"
                    % (python_command, pip_command, requirements_file,
                       virtualenv_cache, virtualenv_appengine_libs)
                ),
                stdout=subprocess.PIPE
            ).wait()
            print "done.\n"


        shutil.move(
            virtualenv_appengine_libs,
            PROJECT_DIR
        )


    def prepare_upload(self):
        self.install_requirements()


    def clean_upload(self):
        dirs_do_delete = [
            appengine_rocket_engine,
            appengine_libs,
            virtualenv_appengine_libs
        ]

        for path in dirs_do_delete:
            try:
                shutil.rmtree(path)
            except OSError:
                pass

    def update(self, argv):
        self.clean_upload()

        try:
            self.prepare_upload()

            try:
                get_callable(PRE_UPDATE_HOOK)()
            except (AttributeError, ImportError):
                pass

            appcfg.main(argv[1:] + [PROJECT_DIR])

            try:
                get_callable(POST_UPDATE_HOOK)()
            except (AttributeError, ImportError):
                pass

        finally:
            self.clean_upload()

    def run_from_argv(self, argv):
        if len(argv) > 2 and argv[2] == 'update':
            self.update(argv)
        else:
            appcfg.main(argv[1:] + [PROJECT_DIR])
