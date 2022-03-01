# The MIT License (MIT)

# Copyright (c) 2021 Tom J. Sun

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import sys
import io
import os

NONE = 99
ERROR = 40
WARN = 30
INFO = 20
DEBUG = 10

LEVEL_NAMES = {
    NONE: "NONE",
    ERROR: "ERROR",
    WARN: "WARN",
    INFO: "INFO",
    DEBUG: "DEBUG",
}


def level_name(level):
    """Returns the string name for the log level"""
    return LEVEL_NAMES[level]


class Logger:
    """Logger logs"""

    def __init__(self, filepath, level):
        self.filepath = filepath
        self.level = level
        self.file = None
        try:
            os.remove(self.filepath)
        except:
            pass

    def log(self, level, msg):
        """Logs a message if the given level is equal to or higher than the logger's level"""
        if level < self.level:
            return
        self._write("%s:%s\n" % (level_name(level), msg))

    def _write(self, msg):
        try:
            if self.file is None:
                self.file = open(self.filepath, "w")
            self.file.write(msg)
            self.file.flush()
        except:
            self.file = None

    def debug(self, msg):
        """Logs a message at DEBUG level"""
        self.log(DEBUG, msg)

    def info(self, msg):
        """Logs a message at INFO level"""
        self.log(INFO, msg)

    def warn(self, msg):
        """Logs a message at WARN level"""
        self.log(WARN, msg)

    def error(self, msg):
        """Logs a message at ERROR level"""
        self.log(ERROR, msg)

    def exception(self, msg):
        """Logs a message including exception at ERROR level"""
        self._exc(sys.exc_info()[1], msg)

    def _exc(self, e, msg):
        buf = io.StringIO()
        sys.print_exception(e, buf)
        self.log(ERROR, msg + "\n" + buf.getvalue())
