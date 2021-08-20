try:
	import utime
except ImportError:
	import time as utime
import sys
try:
	import uio
except ImportError:
	import io as uio

CRITICAL = 50
ERROR    = 40
WARNING  = 30
INFO     = 20
DEBUG    = 10
NOTSET   = 0

_level_dict = {
	CRITICAL: "CRITICAL",
	ERROR: "ERROR",
	WARNING: "WARNING",
	INFO: "INFO",
	DEBUG: "DEBUG",
}


_nameToLevel = {v: k for k, v in _level_dict.items()}


def addLevelName(level, name):
	_level_dict[level] = name

class Logger:

	level = NOTSET

	def __init__(self, name):
		self.name = name
		self.handlers = None
		self.parent = None

	def _level_str(self, level):
		l = _level_dict.get(level)
		if l is not None:
			return l
		return "LVL%s" % level

	def setLevel(self, level):
		self.level = level

	def isEnabledFor(self, level):
		return level >= self.level

	def log(self, level, msg, *args):
		dest = self
		while dest.level == NOTSET and dest.parent:
			dest = dest.parent
		if level >= dest.level:
			record = LogRecord(
				self.name, level, None, None, msg, args, None, None, None
			)

			if dest.handlers:
				for hdlr in dest.handlers:
					hdlr.emit(record)

	def debug(self, msg, *args):
		self.log(DEBUG, msg, *args)

	def info(self, msg, *args):
		self.log(INFO, msg, *args)

	def warning(self, msg, *args):
		self.log(WARNING, msg, *args)

	warn = warning

	def error(self, msg, *args):
		self.log(ERROR, msg, *args)

	def critical(self, msg, *args):
		self.log(CRITICAL, msg, *args)

	def exc(self, e, msg, *args):
		buf = uio.StringIO()
		sys.print_exception(e, buf)
		self.log(ERROR, msg + "\n" + buf.getvalue(), *args)

	def exception(self, msg, *args):
		self.exc(sys.exc_info()[1], msg, *args)

	def addHandler(self, hdlr):
		if self.handlers is None:
			self.handlers = []
		self.handlers.append(hdlr)


def getLogger(name=None):
	if name is None:
		name = "root"
	if name in _loggers:
		return _loggers[name]
	l = Logger(name)
	# For now, we have shallow hierarchy, where parent of each logger is root.
	l.parent = root
	_loggers[name] = l
	return l

def info(msg, *args):
	getLogger(None).info(msg, *args)

def debug(msg, *args):
	getLogger(None).debug(msg, *args)

def warning(msg, *args):
	getLogger(None).warning(msg, *args)

warn = warning

def error(msg, *args):
	getLogger(None).error(msg, *args)

def critical(msg, *args):
	getLogger(None).critical(msg, *args)

def exception(msg, *args):
	getLogger(None).exception(msg, *args)

def basicConfig(level=INFO, filename=None, stream=None, format=None, style="%"):
	root.setLevel(level)
	if filename:
		h = FileHandler(filename)
	else:
		h = StreamHandler(stream)
	h.setFormatter(Formatter(format or "%(levelname)s:%(name)s:%(message)s", style=style))
	root.handlers.clear()
	root.addHandler(h)


class Handler:
	def __init__(self):
		self.formatter = Formatter()

	def setFormatter(self, fmt):
		self.formatter = fmt


class StreamHandler(Handler):
	def __init__(self, stream=None):
		super().__init__()
		self._stream = stream or sys.stderr
		self.terminator = "\n"

	def emit(self, record):
		self._stream.write(self.formatter.format(record) + self.terminator)
		self.flush()

	def flush(self):
		self._stream.flush()


class FileHandler(StreamHandler):
	def __init__(self, filename, mode="a", encoding=None, delay=False):
		super().__init__(None)

		self.encoding = encoding
		self.mode = mode
		self.delay = delay
		self.filename = filename

		if not delay:
			self._stream = open(self.filename, self.mode)

	def emit(self, record):
		if self._stream is None:
			self._stream = open(self.filename, self.mode)

		super().emit(record)

	def close(self):
		if self._stream is not None:
			self._stream.close()


class Formatter:

	converter = utime.localtime

	def __init__(self, fmt=None, datefmt=None, style="%"):
		self.fmt = fmt or "%(message)s"
		self.datefmt = datefmt

		if style not in ("%", "{"):
			raise ValueError("Style must be one of: %, {")

		self.style = style

	def usesTime(self):
		if self.style == "%":
			return "%(asctime)" in self.fmt
		elif self.style == "{":
			return "{asctime" in self.fmt

	def format(self, record):
		# The message attribute of the record is computed using msg % args.
		record.message = record.msg % record.args

		# If the formatting string contains '(asctime)', formatTime() is called to
		# format the event time.
		if self.usesTime():
			record.asctime = self.formatTime(record, self.datefmt)

		# If there is exception information, it is formatted using formatException()
		# and appended to the message. The formatted exception information is cached
		# in attribute exc_text.
		if record.exc_info is not None:
			record.exc_text += self.formatException(record.exc_info)
			record.message += "\n" + record.exc_text

		# The record’s attribute dictionary is used as the operand to a string
		# formatting operation.
		if self.style == "%":
			return self.fmt % record.__dict__
		elif self.style == "{":
			return self.fmt.format(**record.__dict__)
		else:
			raise ValueError(
				"Style {0} is not supported by logging.".format(self.style)
			)

	def formatTime(self, record, datefmt=None):
		assert datefmt is None  # datefmt is not supported
		ct = utime.localtime(record.created)
		return "{0}-{1}-{2} {3}:{4}:{5}".format(*ct)

	def formatException(self, exc_info):
		raise NotImplementedError()

	def formatStack(self, stack_info):
		raise NotImplementedError()


class LogRecord:
	def __init__(
		self, name, level, pathname, lineno, msg, args, exc_info, func=None, sinfo=None
	):
		ct = utime.time()
		self.created = ct
		self.msecs = (ct - int(ct)) * 1000
		self.name = name
		self.levelno = level
		self.levelname = _level_dict.get(level, None)
		self.pathname = pathname
		self.lineno = lineno
		self.msg = msg
		self.args = args
		self.exc_info = exc_info
		self.func = func
		self.sinfo = sinfo

# From: https://gist.github.com/sungitly/3f75cb297572dace2937
def todict(obj, classkey=None):
    if isinstance(obj, dict):
        data = {}
        for (k, v) in obj.items():
            data[k] = todict(v, classkey)
        return data
    elif hasattr(obj, "_ast"):
        return todict(obj._ast())
    elif hasattr(obj, "__iter__"):
        return [todict(v, classkey) for v in obj]
    elif hasattr(obj, "__dict__"):
        data = dict([(key, todict(value, classkey))
                     for key, value in obj.__dict__.items()
                     if not callable(value) and not key.startswith('_') and key not in ['name']])
        if classkey is not None and hasattr(obj, "__class__"):
            data[classkey] = obj.__class__.__name__
        return data
    else:
        return obj
    
root = Logger("root")
root.setLevel(WARNING)
sh = StreamHandler()
sh.formatter = Formatter()
root.addHandler(sh)
_loggers = {"root": root}