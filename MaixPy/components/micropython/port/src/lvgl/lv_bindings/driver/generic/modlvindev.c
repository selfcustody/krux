//////////////////////////////////////////////////////////////////////////////
// Includes
//////////////////////////////////////////////////////////////////////////////

#include "../include/common.h"
#include "lvgl/src/lv_hal/lv_hal_indev.h"
#include "py/obj.h"
#include "py/runtime.h"

//////////////////////////////////////////////////////////////////////////////
// Module definition
//////////////////////////////////////////////////////////////////////////////

typedef struct _indev_obj_t
{
    mp_obj_base_t base;
    mp_obj_t callback;
    mp_obj_t init;
    mp_obj_t deinit;
} indev_obj_t;

// Unfortunately, lvgl doesn't pass user_data to callbacks, so we use this global.
// This means we can have only one active touch driver instance, pointed by this global.
STATIC indev_obj_t *g_indev = NULL;

STATIC mp_obj_t mp_activate_indev(mp_obj_t self_in)
{
    indev_obj_t *self = MP_OBJ_TO_PTR(self_in);
    g_indev = self;
    return mp_const_none;
}

STATIC mp_obj_t indev_make_new(const mp_obj_type_t *type,
                                 size_t n_args,
                                 size_t n_kw,
                                 const mp_obj_t *all_args);

STATIC mp_obj_t mp_indev_init(mp_obj_t self_in);
STATIC mp_obj_t mp_indev_deinit(mp_obj_t self_in);
STATIC bool indev_read(lv_indev_data_t *data);

STATIC MP_DEFINE_CONST_FUN_OBJ_1(mp_init_indev_obj, mp_indev_init);
STATIC MP_DEFINE_CONST_FUN_OBJ_1(mp_deinit_indev_obj, mp_indev_deinit);
STATIC MP_DEFINE_CONST_FUN_OBJ_1(mp_activate_indev_obj, mp_activate_indev);
DEFINE_PTR_OBJ(indev_read);

STATIC const mp_rom_map_elem_t indev_locals_dict_table[] = {
    { MP_ROM_QSTR(MP_QSTR_init), MP_ROM_PTR(&mp_init_indev_obj) },
    { MP_ROM_QSTR(MP_QSTR_deinit), MP_ROM_PTR(&mp_deinit_indev_obj) },
    { MP_ROM_QSTR(MP_QSTR_activate), MP_ROM_PTR(&mp_activate_indev_obj) },
    { MP_ROM_QSTR(MP_QSTR_read), MP_ROM_PTR(&PTR_OBJ(indev_read)) },
};

STATIC MP_DEFINE_CONST_DICT(indev_locals_dict, indev_locals_dict_table);

STATIC const mp_obj_type_t indev_type = {
    { &mp_type_type },
    .name = MP_QSTR_indev,
    //.print = indev_print,
    .make_new = indev_make_new,
    .locals_dict = (mp_obj_dict_t*)&indev_locals_dict,
};

STATIC const mp_rom_map_elem_t indev_globals_table[] = {
        { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_indev) },
        { MP_ROM_QSTR(MP_QSTR_indev), (mp_obj_t)&indev_type},
};
         

STATIC MP_DEFINE_CONST_DICT (
    mp_module_indev_globals,
    indev_globals_table
);

const mp_obj_module_t mp_module_lvindev = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t*)&mp_module_indev_globals
};

//////////////////////////////////////////////////////////////////////////////
// Module implementation
//////////////////////////////////////////////////////////////////////////////

STATIC mp_obj_t indev_make_new(const mp_obj_type_t *type,
                               size_t n_args,
                               size_t n_kw,
                               const mp_obj_t *all_args)
{
    enum{
        ARG_callback,
        ARG_init,
        ARG_deinit
    };

    static const mp_arg_t allowed_args[] = {
        { MP_QSTR_callback, MP_ARG_REQUIRED | MP_ARG_OBJ, {.u_obj=NULL}},  
        { MP_QSTR_init, MP_ARG_OBJ, {.u_obj=NULL}},  
        { MP_QSTR_deinit, MP_ARG_OBJ, {.u_obj=NULL}},  
    };

    mp_arg_val_t args[MP_ARRAY_SIZE(allowed_args)];
    mp_arg_parse_all_kw_array(n_args, n_kw, all_args, MP_ARRAY_SIZE(allowed_args), allowed_args, args);
    indev_obj_t *self = m_new_obj(indev_obj_t);
    self->base.type = type;
    self->callback = args[ARG_callback].u_obj;
    self->init = args[ARG_init].u_obj;
    self->deinit = args[ARG_deinit].u_obj;
    return MP_OBJ_FROM_PTR(self);
}

STATIC mp_obj_t mp_indev_init(mp_obj_t self_in)
{
    indev_obj_t *self = MP_OBJ_TO_PTR(self_in);
    mp_activate_indev(self_in);
    if (self->init) mp_call_function_n_kw(self->init, 1, 0, &self_in);
    return mp_const_none;
}

STATIC mp_obj_t mp_indev_deinit(mp_obj_t self_in)
{
    indev_obj_t *self = MP_OBJ_TO_PTR(self_in);
    if (self->deinit) mp_call_function_n_kw(self->deinit, 1, 0, &self_in);
    return mp_const_none;
}

STATIC bool indev_read(lv_indev_data_t *data)
{
    indev_obj_t *self = MP_OBJ_TO_PTR(g_indev);
    if (!self || (!self->callback)) nlr_raise(
            mp_obj_new_exception_msg(
                &mp_type_RuntimeError, "indev instance needs to be created before callback is called!"));

    mp_obj_t mp_ptr = NEW_PTR_OBJ(lv_indev_data_t, data);
    mp_obj_t mp_return_value = mp_call_function_n_kw(self->callback, 1, 0, &mp_ptr);
    return mp_obj_is_true(mp_return_value);
}


