//
// This module will take care of advancing tick count and scheduling async event for lvgl on ESP32.
// It should be imported after lvgl module is imported.
//

#include "py/obj.h"
#include "py/runtime.h"
#include "py/binary.h"
#include "../../lvgl/lvgl.h"
#include "freertos/FreeRTOS.h"
#include "freertos/timers.h"
#include "esp_log.h"

static const char TAG[] = "[LVGL]";
static TimerHandle_t xTimer;

STATIC mp_obj_t mp_lv_task_handler(mp_obj_t arg)
{
    lv_task_handler();
    return mp_const_none;
}

STATIC MP_DEFINE_CONST_FUN_OBJ_1(mp_lv_task_handler_obj, mp_lv_task_handler);

static void vTimerCallback(TimerHandle_t pxTimer)
{
    lv_tick_inc(portTICK_RATE_MS);
    mp_sched_schedule((mp_obj_t)&mp_lv_task_handler_obj, mp_const_none);
}

STATIC mp_obj_t mp_init_lvesp32()
{
    lv_init();

    xTimer = xTimerCreate(
                "lvgl_timer",
                1,              // The timer period in ticks.
                pdTRUE,         // The timers will auto-reload themselves when they expire.
                NULL,           // User data passed to callback
                vTimerCallback  // Callback function
            );

    if (xTimer == NULL || xTimerStart( xTimer, 0 ) != pdPASS){
        ESP_LOGE(TAG, "Failed creating or starting LVGL timer!");
    } 

   return mp_const_none;
}

STATIC MP_DEFINE_CONST_FUN_OBJ_0(mp_init_lvesp32_obj, mp_init_lvesp32);


STATIC const mp_rom_map_elem_t lvesp32_globals_table[] = {
        { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_lvesp32) },
        { MP_ROM_QSTR(MP_QSTR___init__), MP_ROM_PTR(&mp_init_lvesp32_obj) },
};
         

STATIC MP_DEFINE_CONST_DICT (
    mp_module_lvesp32_globals,
    lvesp32_globals_table
);

const mp_obj_module_t mp_module_lvesp32 = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t*)&mp_module_lvesp32_globals
};

