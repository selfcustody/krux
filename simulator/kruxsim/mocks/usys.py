import traceback
import sys


def print_exception(e, buf):
    traceback.print_exc()


if not getattr(sys, "print_exception", None):
    setattr(sys, "print_exception", print_exception)
