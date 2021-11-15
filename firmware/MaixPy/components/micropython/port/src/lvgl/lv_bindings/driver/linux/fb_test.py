# A simple test for Linux Frame Buffer
# Imports fb (frame buffer) module and uses it as lvgl display driver
# then show a button on screen.

import lvgl as lv
lv.init()
import fb
fb.init()

disp_buf1 = lv.disp_buf_t()
buf1_1 = bytes(480*10)
lv.disp_buf_init(disp_buf1,buf1_1, None, len(buf1_1)//4)
disp_drv = lv.disp_drv_t()
lv.disp_drv_init(disp_drv)
disp_drv.buffer = disp_buf1
disp_drv.flush_cb = fb.flush
disp_drv.hor_res = 480
disp_drv.ver_res = 320
lv.disp_drv_register(disp_drv)

scr = lv.obj()
btn = lv.btn(scr)
btn.align(lv.scr_act(), lv.ALIGN.CENTER, 0, 0)
label = lv.label(btn)
label.set_text("Button")

# Load the screen

lv.scr_load(scr)

while True:
   pass
