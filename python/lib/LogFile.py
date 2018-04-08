#!/usr/local/bin/python3

import logging
import datetime

class LogFile(object):

    def __add_color(self, color_tag, tag):
        if self.filename:
            return "["+tag+"]"
        else:
            return "\033[0;{0}[{1}]\033[0;38m".format(color_tag, tag)

    def __init__(self, filename=None):
        logging.basicConfig(
            filename=filename,
            level=logging.DEBUG,
            format='%(asctime)s %(levelname)s %(message)s',
        )
        self.filename = filename
        logging.addLevelName(logging.DEBUG, self.__add_color("36m", "DEBUG"))
        logging.addLevelName(logging.INFO, self.__add_color("37m", "INFO"))
        logging.addLevelName(logging.WARNING, self.__add_color("38m", "WARN"))
        logging.addLevelName(logging.ERROR, self.__add_color("35m", "ERROR"))
        self.lg = logging.getLogger()

    def localTime(self):
        return datetime.datetime.now()

    def debug(self, msg):
        self.lg.debug(msg)

    def info(self, msg):
        self.lg.info(msg)

    def warn(self, msg):
        self.lg.warn(msg)

    def error(self, msg):
        self.lg.error(msg)
