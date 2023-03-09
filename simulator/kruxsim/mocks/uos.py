# The MIT License (MIT)

# Copyright (c) 2021-2022 Krux contributors

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
import os

old_listdir = os.listdir
old_remove = os.remove
old_isdir = os.path.isdir
old_isfile = os.path.isfile


def new_listdir(path, *args, **kwargs):
    path = path.lstrip("/") if path.startswith("/sd") else path
    return old_listdir(path, *args, **kwargs)


def new_remove(path, *args, **kwargs):
    path = path.lstrip("/") if path.startswith("/sd") else path
    return old_remove(path, *args, **kwargs)


def new_isdir(path, *args, **kwargs):
    path = path.lstrip("/") if path.startswith("/sd") else path
    return old_isdir(path, *args, **kwargs)

def new_isfile(path, *args, **kwargs):
    path = path.lstrip("/") if path.startswith("/sd") else path
    return old_isfile(path, *args, **kwargs)


setattr(os, "listdir", new_listdir)
setattr(os, "remove", new_remove)
setattr(os.path, "isdir", new_isdir)
setattr(os.path, "isfile", new_isfile)
