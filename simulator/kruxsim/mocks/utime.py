import time

if not getattr(time, "sleep_ms", None):
    setattr(time, "sleep_ms", lambda ms: time.sleep(ms / 1000))

start_time = int(time.time() * 1000)


def ticks():
    return int(time.time() * 1000) - start_time


if not getattr(time, "ticks_ms", None):
    setattr(time, "ticks_ms", ticks)
