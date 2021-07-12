#include "../include/common.h"
#include "SDL_monitor.h"
#include "SDL_mouse.h"
#ifdef __EMSCRIPTEN__
#include <emscripten.h>
#endif

/* Defines the LittlevGL tick rate in milliseconds. */
/* Increasing this value might help with CPU usage at the cost of lower
 * responsiveness. */
#define LV_TICK_RATE 50

//////////////////////////////////////////////////////////////////////////////

STATIC mp_obj_t mp_lv_task_handler(mp_obj_t arg)
{  
    if (monitor_active()) monitor_sdl_refr_core();
    lv_task_handler();
    return mp_const_none;
}

STATIC MP_DEFINE_CONST_FUN_OBJ_1(mp_lv_task_handler_obj, mp_lv_task_handler);

#ifndef __EMSCRIPTEN__
STATIC int tick_thread(void * data)
{
    (void)data;

    while(monitor_active()) {
        SDL_Delay(1);   /*Sleep for 1 millisecond*/
        lv_tick_inc(1); /*Tell LittelvGL that 1 milliseconds were elapsed*/
        mp_sched_schedule((mp_obj_t)&mp_lv_task_handler_obj, mp_const_none);
    }

    return 0;
}
#else
STATIC void mp_lv_main_loop(void)
{
        mp_sched_schedule((mp_obj_t)&mp_lv_task_handler_obj, mp_const_none);
        lv_tick_inc(LV_TICK_RATE);
}
#endif

STATIC mp_obj_t mp_init_SDL()
{
    monitor_init();
#ifdef __EMSCRIPTEN__
    emscripten_set_main_loop(mp_lv_main_loop, 1000 / LV_TICK_RATE, 0);
    /* Required for HTML input elements to work */
    SDL_EventState(SDL_TEXTINPUT, SDL_DISABLE);
    SDL_EventState(SDL_KEYDOWN, SDL_DISABLE);
    SDL_EventState(SDL_KEYUP, SDL_DISABLE);
#else
    SDL_CreateThread(tick_thread, "tick", NULL);
#endif
    return mp_const_none;
}

STATIC mp_obj_t mp_deinit_SDL()
{
    monitor_deinit();
    return mp_const_none;
}

STATIC MP_DEFINE_CONST_FUN_OBJ_0(mp_init_SDL_obj, mp_init_SDL);
STATIC MP_DEFINE_CONST_FUN_OBJ_0(mp_deinit_SDL_obj, mp_deinit_SDL);

DEFINE_PTR_OBJ(monitor_flush);
DEFINE_PTR_OBJ(mouse_read);

STATIC const mp_rom_map_elem_t SDL_globals_table[] = {
        { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_SDL) },
        { MP_ROM_QSTR(MP_QSTR_init), MP_ROM_PTR(&mp_init_SDL_obj) },
        { MP_ROM_QSTR(MP_QSTR_deinit), MP_ROM_PTR(&mp_deinit_SDL_obj) },
        { MP_ROM_QSTR(MP_QSTR_monitor_flush), MP_ROM_PTR(&PTR_OBJ(monitor_flush))},
        { MP_ROM_QSTR(MP_QSTR_mouse_read), MP_ROM_PTR(&PTR_OBJ(mouse_read))},
};
         

STATIC MP_DEFINE_CONST_DICT (
    mp_module_SDL_globals,
    SDL_globals_table
);

const mp_obj_module_t mp_module_SDL = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t*)&mp_module_SDL_globals
};

