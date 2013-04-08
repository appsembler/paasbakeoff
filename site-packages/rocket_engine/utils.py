import os
import logging

from google.appengine.api import logservice
from google.appengine.runtime import apiproxy_errors

from django.utils.importlib import import_module


class ImportHook(object):
    #TODO, ipdb, logging

    def find_module(self, fullname, path=None):
        pass

    def load_module(self, fullname):
        return import_module(fullname)


def log_traceback(*args, **kwargs):
    logging.exception('Exception in request:')


def validate_models():
    """
    Since BaseRunserverCommand is only run once, we need to call
    model valdidation here to ensure it is run every time the code
    changes.
    """
    from django.core.management.validation import get_validation_errors
    try:
        from cStringIO import StringIO
    except ImportError:
        from StringIO import StringIO

    logging.info("Validating models...")

    s = StringIO()
    num_errors = get_validation_errors(s, None)

    if num_errors:
        s.seek(0)
        error_text = s.read()
        logging.critical("One or more models did not validate:\n%s" % error_text)
    else:
        logging.info("All models validated.")


def flush_logs():
  try:
    logservice.flush()
  except apiproxy_errors.CancelledError:
    pass
