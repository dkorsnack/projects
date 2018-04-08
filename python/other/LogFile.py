# $Id: LogFile.py 91 2014-04-24 01:19:13Z korsnack $
#!/bin/python

import logging
import datetime

class LogFile(object):

    def __init__(self):
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s %(levelname)s %(message)s',
            handlers=[logging.StreamHandler()],
        )
        logging.addLevelName(logging.DEBUG, "\033[0;36m[DEBUG]\033[0;38m")
        logging.addLevelName(logging.INFO, "\033[0;37m[INFO]\033[0;38m")
        logging.addLevelName(logging.WARNING, "\033[0;33m[WARN]\033[0;38m")
        logging.addLevelName(logging.ERROR, "\033[0;35m[ERROR]\033[0;38m")
        self.lg = logging.getLogger()

    def debug(self, msg):
        self.lg.debug(msg)

    def info(self, msg):
        self.lg.info(msg)

    def warn(self, msg):
        self.lg.warn(msg)

    def error(self, msg):
        self.lg.error(msg)
