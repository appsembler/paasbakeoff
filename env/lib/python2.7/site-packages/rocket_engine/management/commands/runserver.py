from django.core.management.base import BaseCommand
from google.appengine.tools import dev_appserver_main

from ... import PROJECT_DIR

class Command(BaseCommand):

    def run_from_argv(self, argv):
        dev_appserver_main.PrintUsageExit = lambda x: ""

        # this is crap, things like this will lead you to problems
        # only to keep compatibility with Django default 8000 port
        if not any( arg.startswith("--port=") or "-p" == arg for arg in argv ):
            argv.append("--port=8000")


        dev_appserver_main.main(['runserver', PROJECT_DIR] + argv[2:])
