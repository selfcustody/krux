#
# This example shows how to register and use the generic indev device driver.
# The generic indev is an input device that is implemented in pure micropython
# So you can control the input from micropython instead of from C device driver.
#
# This example creates a draggable button and moves it by changing the 
# coordinates of the input device, as if you were dragging it with the mouse.

# General Initializations 

import utime
import lvgl as lv
lv.init()

import SDL
SDL.init()

# Register SDL display driver.

disp_drv = lv.disp_drv_t()
lv.disp_drv_init(disp_drv)
disp_drv.disp_flush = SDL.monitor_flush
disp_drv.disp_fill = SDL.monitor_fill
disp_drv.disp_map = SDL.monitor_map
lv.disp_drv_register(disp_drv)

# Create the generic indev 

import lvindev as indev

# "point" and "state" are two global parameters that represents the mouse coordinates 
# and current button push state

point = lv.point_t({'x':100,'y':100})
state = lv.INDEV_STATE.REL

# "cb" is a callback called by lvgl to get the input device paramerters.
# Its input is a pointer that needs to be casted to lv.indev_data_t struct.
# lvgl expects the callback to update this struct.
# The callback simply copies "point" and "state" globals to the struct.
# It returns False to indicate there is no further input (no need for lvgl to call the callback again now)

def cb(ptr):
    data = lv.indev_data_t.cast(ptr)
    data.point = point
    data.state = state
    return False

# Create and initialize the generic input device with the callback

dev = indev.indev(cb)
dev.init()

# Register the generic input device as an indev POINTER driver
# "dev.read" is the callback that the generic device provides.
# It simply calls the callback we defined earlier.
# If lvgl supported generic callbacks, we could have assigned the callback directly
# instead of "dev.read". Maybe on the next lvgl version.

indev_drv = lv.indev_drv_t()
lv.indev_drv_init(indev_drv)
indev_drv.type = lv.INDEV_TYPE.POINTER
indev_drv.read = dev.read
lv.indev_drv_register(indev_drv)

# Create a button and a label and load the screen

scr = lv.obj()
btn = lv.btn(scr)
btn.align(lv.scr_act(), lv.ALIGN.CENTER, 0, 0)
label = lv.label(btn)
label.set_text("Button")
lv.scr_load(scr)

# Set the buttons as draggable and set its position

btn.set_drag(True)
btn.set_x(90)
btn.set_y(90)

# Press the mouse button!
# We change "state" global which is polled by the callback

state = lv.INDEV_STATE.PR

# Move the mouse in a loop!
# We change "point" global which is polled by the callback

while True:
    for i in range (0,100):
        utime.sleep_ms(10)
        point = lv.point_t({'x':100+i,'y':100})

    for i in range (0,100):
        utime.sleep_ms(10)
        point = lv.point_t({'x':200-i,'y':100})
        
   

