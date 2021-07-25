import lvgl as lv
lv.init()

lv.log_register_print_cb(lambda level,path,line,msg: print('LOG: %s(%d): %s' % (path, line, msg)))

# Initialize ILI9341 display

import lvesp32
from ili9341 import ili9341
disp = ili9341()

HRES = lv.disp_get_hor_res(lv.disp_t.cast(None))
VRES = lv.disp_get_ver_res(lv.disp_t.cast(None))

# Register raw resistive touch driver

import rtch
touch = rtch.touch(xp = 32, yp = 33, xm = 25, ym = 26, touch_rail = 27, touch_sense = 33, cal_x0=0, cal_x1 = HRES, cal_y0=0, cal_y1 = VRES)
touch.init()
indev_drv = lv.indev_drv_t()
lv.indev_drv_init(indev_drv) 
indev_drv.type = lv.INDEV_TYPE.POINTER;
indev_drv.read_cb = touch.read;
lv.indev_drv_register(indev_drv);

# Point class, with both display and touch coordiantes

class Tpcal_point():
    def __init__(self, x, y, name):
        self.display_coordinates = lv.point_t({'x': x, 'y': y})
        self.touch_coordinate = None
        self.name = name

    def __repr__(self):
        return "%s: (%d, %d)" % (self.name, 
                self.touch_coordinate.x,
                self.touch_coordinate.y)

# Calibration helper class

class Tpcal():
        
    # Create a screen with a button and a label

    CIRCLE_SIZE = const(20)
    CIRCLE_OFFSET = const(20)
    TP_MAX_VALUE = const(10000)

    LV_COORD_MAX = const((1 << (8 * 2 - 1)) - 1000)
    LV_RADIUS_CIRCLE = const(LV_COORD_MAX) # TODO use lv.RADIUS_CIRCLE constant when it's available!

    def __init__(self, points, calibrate, touch_count = 5):

        self.points = points
        self.calibrate = calibrate
        self.touch_count = touch_count

        self.med = [lv.point_t() for i in range(0,self.touch_count)] # Storage point to calculate median

        self.cur_point = 0
        self.cur_touch = 0

        self.scr = lv.obj(None, None)
        self.scr.set_size(TP_MAX_VALUE, TP_MAX_VALUE)
        lv.scr_load(self.scr)

        # Create a big transparent button screen to receive clicks

        self.big_btn = lv.btn(lv.scr_act(), None)
        self.big_btn.set_size(TP_MAX_VALUE, TP_MAX_VALUE)
        self.big_btn.set_style(lv.btn.STYLE.REL, lv.style_transp)
        self.big_btn.set_style(lv.btn.STYLE.PR, lv.style_transp)
        self.big_btn.set_layout(lv.LAYOUT.OFF)
        self.big_btn.set_event_cb(lambda obj, event, self=self: self.calibrate_clicked() if event == lv.EVENT.CLICKED else None) 

        # Create the screen, circle and label

        self.label_main = lv.label(lv.scr_act(), None)

        style_circ = lv.style_t()
        lv.style_copy(style_circ, lv.style_pretty_color)
        style_circ.body.radius = LV_RADIUS_CIRCLE

        self.circ_area = lv.obj(lv.scr_act(), None)
        self.circ_area.set_size(CIRCLE_SIZE, CIRCLE_SIZE)
        self.circ_area.set_style(style_circ)
        self.circ_area.set_click(False)

        self.show_circle()

    def show_text(self, txt):
        self.label_main.set_text(txt)
        self.label_main.set_align(lv.label.ALIGN.CENTER)
        self.label_main.set_pos((HRES - self.label_main.get_width() ) // 2,
                           (VRES - self.label_main.get_height()) // 2)
    def show_circle(self):
        point = self.points[self.cur_point]
        self.show_text("Click the circle in\n" + \
              point.name + "\n" + \
              "%d left" % (self.touch_count - self.cur_touch))
        if point.display_coordinates.x < 0: point.display_coordinates.x += HRES
        if point.display_coordinates.y < 0: point.display_coordinates.y += VRES
        self.circ_area.set_pos(point.display_coordinates.x - CIRCLE_SIZE // 2,
                               point.display_coordinates.y - CIRCLE_SIZE // 2)

    def calibrate_clicked(self):
        point = self.points[self.cur_point]
        indev = lv.indev_get_act()
        lv.indev_get_point(indev, self.med[self.cur_touch])

        self.cur_touch += 1

        if self.cur_touch == self.touch_count:
            med_x = sorted([med.x for med in self.med])
            med_y = sorted([med.y for med in self.med])
            x = med_x[len(med_x) // 2]
            y = med_y[len(med_y) // 2]
            point.touch_coordinate = lv.point_t({
                'x': x,
                'y': y})

            self.cur_point += 1
            self.cur_touch = 0

        if self.cur_point == len(self.points):
            self.calibrate(self.points)
            self.cur_point = 0
            self.show_text("Click/drag on screen\n" + \
                           "to check calibration")
            self.big_btn.set_event_cb(lambda obj, event, self=self: self.check() if event == lv.EVENT.PRESSING else None) 
        else:
            self.show_circle()

    def check(self):
        point = lv.point_t()
        indev = lv.indev_get_act()
        lv.indev_get_point(indev, point)
        self.circ_area.set_pos(point.x - CIRCLE_SIZE // 2,
                               point.y - CIRCLE_SIZE // 2)

# Calculate calibration, and calibrate

def calibrate(points):
    visual_width = points[1].display_coordinates.x - points[0].display_coordinates.x
    visual_height = points[1].display_coordinates.y - points[0].display_coordinates.y
    touch_width = points[1].touch_coordinate.x - points[0].touch_coordinate.x
    touch_height = points[1].touch_coordinate.y - points[0].touch_coordinate.y

    pixel_width = touch_width / visual_width
    pixel_height = touch_height / visual_height

    x0 = points[0].touch_coordinate.x - points[0].display_coordinates.x * pixel_width
    y0 = points[0].touch_coordinate.y - points[0].display_coordinates.y * pixel_height

    x1 = points[1].touch_coordinate.x + (HRES - points[1].display_coordinates.x) * pixel_width
    y1 = points[1].touch_coordinate.y + (VRES - points[1].display_coordinates.y) * pixel_height

    print("Calibration result: x0=%d, y0=%d, x1=%d, y1=%d" % (round(x0), round(y0), round(x1), round(y1)))
    touch.calibrate(round(x0), round(y0), round(x1), round(y1))
    
# Run calibrationh

tpcal = Tpcal([
        Tpcal_point(20,  20, "upper left-hand corner"),
        Tpcal_point(-40, -40, "lower right-hand corner"),
    ], calibrate)

# while True:
#    pass
