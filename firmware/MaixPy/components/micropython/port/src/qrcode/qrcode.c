// Include required definitions first.
#include "py/obj.h"
#include "py/runtime.h"
#include "py/builtin.h"
#include "qrcodegen.h"
#include "string.h"

STATIC mp_obj_t qrcode_encode(mp_obj_t text_obj){
    mp_buffer_info_t bufinfo;
    mp_get_buffer_raise(text_obj, &bufinfo, MP_BUFFER_READ);

    enum qrcodegen_Ecc errCorLvl = qrcodegen_Ecc_LOW;  // Error correction level
    
    uint8_t qrcode[qrcodegen_BUFFER_LEN_MAX];
    uint8_t tempBuffer[qrcodegen_BUFFER_LEN_MAX];
    bool ok = qrcodegen_encodeText(bufinfo.buf, tempBuffer, qrcode, errCorLvl,
        qrcodegen_VERSION_MIN, qrcodegen_VERSION_MAX, qrcodegen_Mask_AUTO, true);
    if(!ok){
        mp_raise_ValueError("Failed to encode");
    }
    int size = qrcodegen_getSize(qrcode);
    // align to 8 bits and add 2-block border
    int imgsize = (size/8+1)*8+4;
    int lpad = (imgsize-size)/2;
    size_t bufsize = (imgsize*imgsize)/8;
    vstr_t vstr;
    vstr_init_len(&vstr, bufsize);
    memset((byte*)vstr.buf, 0, bufsize);
    size_t cur = imgsize*lpad;
    for(int y=0; y<imgsize-lpad; y++){
        cur+=lpad;
        for(int x=0; x<imgsize-lpad; x++){
            vstr.buf[cur/8] = vstr.buf[cur/8] << 1;
            if(x<size && y<size){
                if(qrcodegen_getModule(qrcode, x, y)){
                    vstr.buf[cur/8]++;
                }
            }
            cur++;
        }
    }
    return mp_obj_new_str_from_vstr(&mp_type_bytes, &vstr);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(qrcode_encode_obj, qrcode_encode);


STATIC mp_obj_t qrcode_encode_to_string(mp_obj_t text_obj){
    mp_buffer_info_t bufinfo;
    mp_get_buffer_raise(text_obj, &bufinfo, MP_BUFFER_READ);

    enum qrcodegen_Ecc errCorLvl = qrcodegen_Ecc_LOW;  // Error correction level
    
    uint8_t qrcode[qrcodegen_BUFFER_LEN_MAX];
    uint8_t tempBuffer[qrcodegen_BUFFER_LEN_MAX];
    bool ok = qrcodegen_encodeText(bufinfo.buf, tempBuffer, qrcode, errCorLvl,
        qrcodegen_VERSION_MIN, qrcodegen_VERSION_MAX, qrcodegen_Mask_AUTO, true);
    if(!ok){
        mp_raise_ValueError("Failed to encode");
    }
    int size = qrcodegen_getSize(qrcode);
    size_t bufsize = (size+1)*size;
    vstr_t vstr;
    vstr_init_len(&vstr, bufsize);
    memset((byte*)vstr.buf, '0', bufsize);
    for(int y=0; y<size; y++){
        for(int x=0; x<size; x++){
            if(qrcodegen_getModule(qrcode, x, y)){
                vstr.buf[y*(size+1)+x]='1';
            }
        }
        vstr.buf[y*(size+1)+size]='\n';
    }
    return mp_obj_new_str_from_vstr(&mp_type_str, &vstr);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(qrcode_encode_to_string_obj, qrcode_encode_to_string);
/****************************** MODULE ******************************/

STATIC const mp_rom_map_elem_t qrcode_module_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_qrcode) },
    { MP_ROM_QSTR(MP_QSTR_encode), MP_ROM_PTR(&qrcode_encode_obj) },
    { MP_ROM_QSTR(MP_QSTR_encode_to_string), MP_ROM_PTR(&qrcode_encode_to_string_obj) },
};
STATIC MP_DEFINE_CONST_DICT(qrcode_module_globals, qrcode_module_globals_table);

// Define module object.
const mp_obj_module_t qrcode_user_cmodule = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t*)&qrcode_module_globals,
};

// Register the module to make it available in Python
MP_REGISTER_MODULE(MP_QSTR_qrcode, qrcode_user_cmodule, MODULE_QRCODE_ENABLED);
