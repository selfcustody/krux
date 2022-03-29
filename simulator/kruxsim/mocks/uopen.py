import builtins

old_open = open


def new_open(path, *args, **kwargs):
    path = path.lstrip("/") if path.startswith("/sd") else path
    return old_open(path, *args, **kwargs)


builtins.open = new_open
