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
import gc
import machine
from pmu import axp192
from context import Context
from login import Login
from home import Home

pmu = axp192()

# Enable power management so that if power button is held down 6 secs, 
# it shuts off as expected
pmu.enablePMICSleepMode(True)

ctx = Context()

ctx.display.flash_text(""" 
++-+-+-++

 K r u x 

++-+-+-++
""")
       
pages = [Login, Home]
page_index = 0
while True:
	page = pages[page_index](ctx)
	shutdown = page.run()
	if shutdown:
		break
	page = None
	gc.collect()
	page_index = (page_index + 1) % len(pages)
	
ctx.display.flash_text('Shutting down..')

ctx.clear()
  
pmu.setEnterSleepMode()
machine.reset()