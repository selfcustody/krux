// Include required definitions first.
#include "py/obj.h"
#include "py/runtime.h"
#include "py/builtin.h"
#include "wordlist_bip39.h"
#include "wordlist_slip39.h"

/****************************** MODULE uembit.wordlists.bip39 ******************************/

STATIC mp_obj_t bip39_wordlist_get(mp_obj_t index_obj){
    mp_int_t idx = mp_obj_get_int(index_obj);
    if(idx < 0 || idx >= WORDLIST_BIP39_LENGTH){
        mp_raise_ValueError("Invalid index");
        return mp_const_none;
    }
    const char * word = wordlist_bip39_english[idx];
    vstr_t w;
    vstr_init_len(&w, strlen(word));
    memcpy((byte*)w.buf, word, strlen(word));
    return mp_obj_new_str_from_vstr(&mp_type_str, &w);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(bip39_wordlist_get_obj, bip39_wordlist_get);

STATIC mp_obj_t bip39_wordlist_index(mp_obj_t word){
    mp_buffer_info_t wordbuf;
    mp_get_buffer_raise(word, &wordbuf, MP_BUFFER_READ);
    for(int i=0; i < WORDLIST_BIP39_LENGTH; i++){
        if(strlen(wordlist_bip39_english[i]) == wordbuf.len){
            if(memcmp(wordlist_bip39_english[i], wordbuf.buf, wordbuf.len) == 0){
                return mp_obj_new_int(i);
            }
        }
    }
    return mp_obj_new_int(-1);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(bip39_wordlist_index_obj, bip39_wordlist_index);

STATIC const mp_rom_map_elem_t uembit_bip39_wordlist_module_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_ubip39) },
    { MP_ROM_QSTR(MP_QSTR_get), MP_ROM_PTR(&bip39_wordlist_get_obj) },
    { MP_ROM_QSTR(MP_QSTR_index), MP_ROM_PTR(&bip39_wordlist_index_obj) },
    { MP_ROM_QSTR(MP_QSTR_len), MP_ROM_INT(WORDLIST_BIP39_LENGTH) },
};
STATIC MP_DEFINE_CONST_DICT(uembit_bip39_wordlist_module_globals, uembit_bip39_wordlist_module_globals_table);

// Define module object.
const mp_obj_module_t uembit_bip39_wordlist_module = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t*)&uembit_bip39_wordlist_module_globals,
};


/****************************** MODULE uembit.wordlists.slip39 ******************************/

STATIC mp_obj_t slip39_wordlist_get(mp_obj_t index_obj){
    mp_int_t idx = mp_obj_get_int(index_obj);
    if(idx < 0 || idx >= WORDLIST_SLIP39_LENGTH){
        mp_raise_ValueError("Invalid index");
        return mp_const_none;
    }
    const char * word = wordlist_slip39_english[idx];
    vstr_t w;
    vstr_init_len(&w, strlen(word));
    memcpy((byte*)w.buf, word, strlen(word));
    return mp_obj_new_str_from_vstr(&mp_type_str, &w);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(slip39_wordlist_get_obj, slip39_wordlist_get);

STATIC mp_obj_t slip39_wordlist_index(mp_obj_t word){
    mp_buffer_info_t wordbuf;
    mp_get_buffer_raise(word, &wordbuf, MP_BUFFER_READ);
    for(int i=0; i < WORDLIST_SLIP39_LENGTH; i++){
        if(strlen(wordlist_slip39_english[i]) == wordbuf.len){
            if(memcmp(wordlist_slip39_english[i], wordbuf.buf, wordbuf.len) == 0){
                return mp_obj_new_int(i);
            }
        }
    }
    return mp_obj_new_int(-1);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(slip39_wordlist_index_obj, slip39_wordlist_index);

STATIC const mp_rom_map_elem_t uembit_slip39_wordlist_module_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_uslip39) },
    { MP_ROM_QSTR(MP_QSTR_get), MP_ROM_PTR(&slip39_wordlist_get_obj) },
    { MP_ROM_QSTR(MP_QSTR_index), MP_ROM_PTR(&slip39_wordlist_index_obj) },
    { MP_ROM_QSTR(MP_QSTR_len), MP_ROM_INT(WORDLIST_SLIP39_LENGTH) },
};
STATIC MP_DEFINE_CONST_DICT(uembit_slip39_wordlist_module_globals, uembit_slip39_wordlist_module_globals_table);

// Define module object.
const mp_obj_module_t uembit_slip39_wordlist_module = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t*)&uembit_slip39_wordlist_module_globals,
};

/****************************** MODULE uembit.wordlists ******************************/

STATIC const mp_rom_map_elem_t uembit_wordlists_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_wordlists) },
    { MP_ROM_QSTR(MP_QSTR_bip39), MP_ROM_PTR(&uembit_bip39_wordlist_module) },
    { MP_ROM_QSTR(MP_QSTR_slip39), MP_ROM_PTR(&uembit_slip39_wordlist_module) },
};
STATIC MP_DEFINE_CONST_DICT(uembit_wordlists_globals, uembit_wordlists_globals_table);

// Define module object.
const mp_obj_module_t uembit_wordlists_user_cmodule = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t*)&uembit_wordlists_globals,
};

/****************************** MODULE uembit ******************************/

STATIC const mp_rom_map_elem_t uembit_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_uembit) },
    { MP_ROM_QSTR(MP_QSTR_wordlists), MP_ROM_PTR(&uembit_wordlists_user_cmodule) },
};
STATIC MP_DEFINE_CONST_DICT(uembit_globals, uembit_globals_table);

// Define module object.
const mp_obj_module_t uembit_user_cmodule = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t*)&uembit_globals,
};

// Register the module to make it available in Python
MP_REGISTER_MODULE(MP_QSTR_uembit, uembit_user_cmodule, MODULE_UEMBIT_ENABLED);

