import logging

from google.appengine.runtime import DeadlineExceededError

from . import utils

logger = logging.getLogger(__name__)


class DefferedTask(object):

    name = lambda self: self.__class__.__name__

    def __call__(self, cursor=None):
        if cursor:
            logger.debug("DefferedTask: %s, started at cursor %s."
                         % (self.name, self.cursor))
        else:
            logger.debug("DefferedTask: %s, started." % self.name)

        utils.flush_logs()

        try:
            self.cursor = cursor
            self.job()
        except DeadlineExceededError:
            logger.debug(
                "DefferedTask: %s, time limit hit at cursor %s .Restarting"
                % (self.name, self.cursor)
            )
            self.__call__(self.cursor)
