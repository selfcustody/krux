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
def load(setting, default, strip=True):
    """Loads a setting from the settings directory with name <setting>.txt, optionally stripping
       the value before returning.

       If setting does not exist, default will be returned.
    """
    try:
        with open('/sd/settings/%s.txt' % setting, 'r') as setting_file:
            value = setting_file.read()
            if strip:
                return value.strip()
            return value
    except:
        return default

def save(setting, value):
    """Writes a setting to the settings directory with name <setting>.txt"""
    try:
        with open('/sd/settings/%s.txt' % setting, 'w') as setting_file:
            setting_file.write(value)
    except:
        pass
