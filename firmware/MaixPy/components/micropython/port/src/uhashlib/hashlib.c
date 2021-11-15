#include <assert.h>
#include <string.h>
#include "py/obj.h"
#include "py/runtime.h"
#include "py/builtin.h"
#include "crypto/sha2.h"
#include "crypto/ripemd160.h"
#include "crypto/pbkdf2.h"
#include "crypto/hmac.h"

typedef struct _mp_obj_hash_t {
    mp_obj_base_t base;
    char state[0];
} mp_obj_hash_t;

/****************************** SHA1 ******************************/

STATIC mp_obj_t hashlib_sha1_update(mp_obj_t self_in, mp_obj_t arg);

STATIC mp_obj_t hashlib_sha1_make_new(const mp_obj_type_t *type, size_t n_args, size_t n_kw, const mp_obj_t *args) {
    mp_arg_check_num(n_args, n_kw, 0, 1, false);
    mp_obj_hash_t *o = m_new_obj_var(mp_obj_hash_t, char, sizeof(SHA1_CTX));
    o->base.type = type;
    sha1_Init((SHA1_CTX*)o->state);
    if (n_args == 1) {
        hashlib_sha1_update(MP_OBJ_FROM_PTR(o), args[0]);
    }
    return MP_OBJ_FROM_PTR(o);
}

STATIC mp_obj_t hashlib_sha1_copy(mp_obj_t self_in) {
    mp_obj_hash_t *o = m_new_obj_var(mp_obj_hash_t, char, sizeof(SHA1_CTX));
    mp_obj_hash_t *self = MP_OBJ_TO_PTR(self_in);
    o->base.type = self->base.type;
    memcpy(o->state, self->state, sizeof(SHA1_CTX));
    return MP_OBJ_FROM_PTR(o);
}

STATIC mp_obj_t hashlib_sha1_update(mp_obj_t self_in, mp_obj_t arg) {
    mp_obj_hash_t *self = MP_OBJ_TO_PTR(self_in);
    mp_buffer_info_t bufinfo;
    mp_get_buffer_raise(arg, &bufinfo, MP_BUFFER_READ);
    sha1_Update((SHA1_CTX*)self->state, bufinfo.buf, bufinfo.len);
    return mp_const_none;
}

STATIC mp_obj_t hashlib_sha1_digest(mp_obj_t self_in) {
    mp_obj_hash_t *self = MP_OBJ_TO_PTR(self_in);
    vstr_t vstr;
    vstr_init_len(&vstr, SHA1_DIGEST_LENGTH);
    sha1_Final((SHA1_CTX*)self->state, (byte*)vstr.buf);
    return mp_obj_new_str_from_vstr(&mp_type_bytes, &vstr);
}

STATIC MP_DEFINE_CONST_FUN_OBJ_2(hashlib_sha1_update_obj, hashlib_sha1_update);
STATIC MP_DEFINE_CONST_FUN_OBJ_1(hashlib_sha1_digest_obj, hashlib_sha1_digest);
STATIC MP_DEFINE_CONST_FUN_OBJ_1(hashlib_sha1_copy_obj, hashlib_sha1_copy);

STATIC const mp_rom_map_elem_t hashlib_sha1_locals_dict_table[] = {
    { MP_ROM_QSTR(MP_QSTR_update), MP_ROM_PTR(&hashlib_sha1_update_obj) },
    { MP_ROM_QSTR(MP_QSTR_digest), MP_ROM_PTR(&hashlib_sha1_digest_obj) },
    { MP_ROM_QSTR(MP_QSTR_digest_size), MP_ROM_INT(SHA1_DIGEST_LENGTH) },
    { MP_ROM_QSTR(MP_QSTR_block_size), MP_ROM_INT(SHA1_BLOCK_LENGTH) },
    { MP_ROM_QSTR(MP_QSTR_copy), MP_ROM_PTR(&hashlib_sha1_copy_obj) },
};

STATIC MP_DEFINE_CONST_DICT(hashlib_sha1_locals_dict, hashlib_sha1_locals_dict_table);

STATIC const mp_obj_type_t hashlib_sha1_type = {
    { &mp_type_type },
    .name = MP_QSTR_sha1,
    .make_new = hashlib_sha1_make_new,
    .locals_dict = (void*)&hashlib_sha1_locals_dict,
};

/****************************** SHA256 ******************************/

STATIC mp_obj_t hashlib_sha256_update(mp_obj_t self_in, mp_obj_t arg);

STATIC mp_obj_t hashlib_sha256_make_new(const mp_obj_type_t *type, size_t n_args, size_t n_kw, const mp_obj_t *args) {
    mp_arg_check_num(n_args, n_kw, 0, 1, false);
    mp_obj_hash_t *o = m_new_obj_var(mp_obj_hash_t, char, sizeof(SHA256_CTX));
    o->base.type = type;
    sha256_Init((SHA256_CTX*)o->state);
    if (n_args == 1) {
        hashlib_sha256_update(MP_OBJ_FROM_PTR(o), args[0]);
    }
    return MP_OBJ_FROM_PTR(o);
}

STATIC mp_obj_t hashlib_sha256_copy(mp_obj_t self_in) {
    mp_obj_hash_t *o = m_new_obj_var(mp_obj_hash_t, char, sizeof(SHA256_CTX));
    mp_obj_hash_t *self = MP_OBJ_TO_PTR(self_in);
    o->base.type = self->base.type;
    memcpy(o->state, self->state, sizeof(SHA256_CTX));
    return MP_OBJ_FROM_PTR(o);
}

STATIC mp_obj_t hashlib_sha256_update(mp_obj_t self_in, mp_obj_t arg) {
    mp_obj_hash_t *self = MP_OBJ_TO_PTR(self_in);
    mp_buffer_info_t bufinfo;
    mp_get_buffer_raise(arg, &bufinfo, MP_BUFFER_READ);
    sha256_Update((SHA256_CTX*)self->state, bufinfo.buf, bufinfo.len);
    return mp_const_none;
}

STATIC mp_obj_t hashlib_sha256_digest(mp_obj_t self_in) {
    mp_obj_hash_t *self = MP_OBJ_TO_PTR(self_in);
    vstr_t vstr;
    vstr_init_len(&vstr, SHA256_DIGEST_LENGTH);
    sha256_Final((SHA256_CTX*)self->state, (byte*)vstr.buf);
    return mp_obj_new_str_from_vstr(&mp_type_bytes, &vstr);
}

STATIC MP_DEFINE_CONST_FUN_OBJ_2(hashlib_sha256_update_obj, hashlib_sha256_update);
STATIC MP_DEFINE_CONST_FUN_OBJ_1(hashlib_sha256_digest_obj, hashlib_sha256_digest);
STATIC MP_DEFINE_CONST_FUN_OBJ_1(hashlib_sha256_copy_obj, hashlib_sha256_copy);

STATIC const mp_rom_map_elem_t hashlib_sha256_locals_dict_table[] = {
    { MP_ROM_QSTR(MP_QSTR_update), MP_ROM_PTR(&hashlib_sha256_update_obj) },
    { MP_ROM_QSTR(MP_QSTR_digest), MP_ROM_PTR(&hashlib_sha256_digest_obj) },
    { MP_ROM_QSTR(MP_QSTR_digest_size), MP_ROM_INT(SHA256_DIGEST_LENGTH) },
    { MP_ROM_QSTR(MP_QSTR_block_size), MP_ROM_INT(SHA256_BLOCK_LENGTH) },
    { MP_ROM_QSTR(MP_QSTR_copy), MP_ROM_PTR(&hashlib_sha256_copy_obj) },
};

STATIC MP_DEFINE_CONST_DICT(hashlib_sha256_locals_dict, hashlib_sha256_locals_dict_table);

STATIC const mp_obj_type_t hashlib_sha256_type = {
    { &mp_type_type },
    .name = MP_QSTR_sha256,
    .make_new = hashlib_sha256_make_new,
    .locals_dict = (void*)&hashlib_sha256_locals_dict,
};

/****************************** SHA512 ******************************/

STATIC mp_obj_t hashlib_sha512_update(mp_obj_t self_in, mp_obj_t arg);

STATIC mp_obj_t hashlib_sha512_make_new(const mp_obj_type_t *type, size_t n_args, size_t n_kw, const mp_obj_t *args) {
    mp_arg_check_num(n_args, n_kw, 0, 1, false);
    mp_obj_hash_t *o = m_new_obj_var(mp_obj_hash_t, char, sizeof(SHA512_CTX));
    o->base.type = type;
    sha512_Init((SHA512_CTX*)o->state);
    if (n_args == 1) {
        hashlib_sha512_update(MP_OBJ_FROM_PTR(o), args[0]);
    }
    return MP_OBJ_FROM_PTR(o);
}

STATIC mp_obj_t hashlib_sha512_copy(mp_obj_t self_in) {
    mp_obj_hash_t *o = m_new_obj_var(mp_obj_hash_t, char, sizeof(SHA512_CTX));
    mp_obj_hash_t *self = MP_OBJ_TO_PTR(self_in);
    o->base.type = self->base.type;
    memcpy(o->state, self->state, sizeof(SHA512_CTX));
    return MP_OBJ_FROM_PTR(o);
}

STATIC mp_obj_t hashlib_sha512_update(mp_obj_t self_in, mp_obj_t arg) {
    mp_obj_hash_t *self = MP_OBJ_TO_PTR(self_in);
    mp_buffer_info_t bufinfo;
    mp_get_buffer_raise(arg, &bufinfo, MP_BUFFER_READ);
    sha512_Update((SHA512_CTX*)self->state, bufinfo.buf, bufinfo.len);
    return mp_const_none;
}

STATIC mp_obj_t hashlib_sha512_digest(mp_obj_t self_in) {
    mp_obj_hash_t *self = MP_OBJ_TO_PTR(self_in);
    vstr_t vstr;
    vstr_init_len(&vstr, SHA512_DIGEST_LENGTH);
    sha512_Final((SHA512_CTX*)self->state, (byte*)vstr.buf);
    return mp_obj_new_str_from_vstr(&mp_type_bytes, &vstr);
}

STATIC MP_DEFINE_CONST_FUN_OBJ_2(hashlib_sha512_update_obj, hashlib_sha512_update);
STATIC MP_DEFINE_CONST_FUN_OBJ_1(hashlib_sha512_digest_obj, hashlib_sha512_digest);
STATIC MP_DEFINE_CONST_FUN_OBJ_1(hashlib_sha512_copy_obj, hashlib_sha512_copy);

STATIC const mp_rom_map_elem_t hashlib_sha512_locals_dict_table[] = {
    { MP_ROM_QSTR(MP_QSTR_update), MP_ROM_PTR(&hashlib_sha512_update_obj) },
    { MP_ROM_QSTR(MP_QSTR_digest), MP_ROM_PTR(&hashlib_sha512_digest_obj) },
    { MP_ROM_QSTR(MP_QSTR_digest_size), MP_ROM_INT(SHA512_DIGEST_LENGTH) },
    { MP_ROM_QSTR(MP_QSTR_block_size), MP_ROM_INT(SHA512_BLOCK_LENGTH) },
    { MP_ROM_QSTR(MP_QSTR_copy), MP_ROM_PTR(&hashlib_sha512_copy_obj) },
};

STATIC MP_DEFINE_CONST_DICT(hashlib_sha512_locals_dict, hashlib_sha512_locals_dict_table);

STATIC const mp_obj_type_t hashlib_sha512_type = {
    { &mp_type_type },
    .name = MP_QSTR_sha512,
    .make_new = hashlib_sha512_make_new,
    .locals_dict = (void*)&hashlib_sha512_locals_dict,
};

/****************************** RIPEMD160 ******************************/

STATIC mp_obj_t hashlib_ripemd160_update(mp_obj_t self_in, mp_obj_t arg);

STATIC mp_obj_t hashlib_ripemd160_make_new(const mp_obj_type_t *type, size_t n_args, size_t n_kw, const mp_obj_t *args) {
    mp_arg_check_num(n_args, n_kw, 0, 1, false);
    mp_obj_hash_t *o = m_new_obj_var(mp_obj_hash_t, char, sizeof(RIPEMD160_CTX));
    o->base.type = type;
    ripemd160_Init((RIPEMD160_CTX*)o->state);
    if (n_args == 1) {
        hashlib_ripemd160_update(MP_OBJ_FROM_PTR(o), args[0]);
    }
    return MP_OBJ_FROM_PTR(o);
}

STATIC mp_obj_t hashlib_ripemd160_copy(mp_obj_t self_in) {
    mp_obj_hash_t *o = m_new_obj_var(mp_obj_hash_t, char, sizeof(RIPEMD160_CTX));
    mp_obj_hash_t *self = MP_OBJ_TO_PTR(self_in);
    o->base.type = self->base.type;
    memcpy(o->state, self->state, sizeof(RIPEMD160_CTX));
    return MP_OBJ_FROM_PTR(o);
}

STATIC mp_obj_t hashlib_ripemd160_update(mp_obj_t self_in, mp_obj_t arg) {
    mp_obj_hash_t *self = MP_OBJ_TO_PTR(self_in);
    mp_buffer_info_t bufinfo;
    mp_get_buffer_raise(arg, &bufinfo, MP_BUFFER_READ);
    ripemd160_Update((RIPEMD160_CTX*)self->state, bufinfo.buf, bufinfo.len);
    return mp_const_none;
}

STATIC mp_obj_t hashlib_ripemd160_digest(mp_obj_t self_in) {
    mp_obj_hash_t *self = MP_OBJ_TO_PTR(self_in);
    vstr_t vstr;
    vstr_init_len(&vstr, RIPEMD160_DIGEST_LENGTH);
    ripemd160_Final((RIPEMD160_CTX*)self->state, (byte*)vstr.buf);
    return mp_obj_new_str_from_vstr(&mp_type_bytes, &vstr);
}

STATIC MP_DEFINE_CONST_FUN_OBJ_2(hashlib_ripemd160_update_obj, hashlib_ripemd160_update);
STATIC MP_DEFINE_CONST_FUN_OBJ_1(hashlib_ripemd160_digest_obj, hashlib_ripemd160_digest);
STATIC MP_DEFINE_CONST_FUN_OBJ_1(hashlib_ripemd160_copy_obj, hashlib_ripemd160_copy);

STATIC const mp_rom_map_elem_t hashlib_ripemd160_locals_dict_table[] = {
    { MP_ROM_QSTR(MP_QSTR_update), MP_ROM_PTR(&hashlib_ripemd160_update_obj) },
    { MP_ROM_QSTR(MP_QSTR_digest), MP_ROM_PTR(&hashlib_ripemd160_digest_obj) },
    { MP_ROM_QSTR(MP_QSTR_digest_size), MP_ROM_INT(RIPEMD160_DIGEST_LENGTH) },
    { MP_ROM_QSTR(MP_QSTR_block_size), MP_ROM_INT(RIPEMD160_BLOCK_LENGTH) },
    { MP_ROM_QSTR(MP_QSTR_copy), MP_ROM_PTR(&hashlib_ripemd160_copy_obj) },
};

STATIC MP_DEFINE_CONST_DICT(hashlib_ripemd160_locals_dict, hashlib_ripemd160_locals_dict_table);

STATIC const mp_obj_type_t hashlib_ripemd160_type = {
    { &mp_type_type },
    .name = MP_QSTR_ripemd160,
    .make_new = hashlib_ripemd160_make_new,
    .locals_dict = (void*)&hashlib_ripemd160_locals_dict,
};

/************************** pbkdf2_hmac **************************/

// hashlib.pbkdf2_hmac(hash_name, password, salt, iterations, dklen=None)
STATIC mp_obj_t hashlib_pbkdf2_hmac(size_t n_args, const mp_obj_t *args) {
    // hash_name
    mp_buffer_info_t typebuf;
    mp_get_buffer_raise(args[0], &typebuf, MP_BUFFER_READ);
    // password
    mp_buffer_info_t pwdbuf;
    mp_get_buffer_raise(args[1], &pwdbuf, MP_BUFFER_READ);
    // salt
    mp_buffer_info_t saltbuf;
    mp_get_buffer_raise(args[2], &saltbuf, MP_BUFFER_READ);
    // number of iterations
    mp_int_t iter = mp_obj_get_int(args[3]);

    // only sha256 or sha512 are supported
    if(strcmp(typebuf.buf, "sha256") == 0){
        // output length (dklen) if available
        mp_int_t l = SHA256_DIGEST_LENGTH;
        if(n_args > 4){
            l = mp_obj_get_int(args[4]);
        }
        vstr_t vstr;
        vstr_init_len(&vstr, l);
        pbkdf2_hmac_sha256(pwdbuf.buf, pwdbuf.len, saltbuf.buf, saltbuf.len, iter, (byte*)vstr.buf, l);
        return mp_obj_new_str_from_vstr(&mp_type_bytes, &vstr);
    }
    if(strcmp(typebuf.buf, "sha512") == 0){
        // output length (dklen) if available
        mp_int_t l = SHA512_DIGEST_LENGTH;
        if(n_args > 4){
            l = mp_obj_get_int(args[4]);
        }
        vstr_t vstr;
        vstr_init_len(&vstr, l);
        pbkdf2_hmac_sha512(pwdbuf.buf, pwdbuf.len, saltbuf.buf, saltbuf.len, iter, (byte*)vstr.buf, l);
        return mp_obj_new_str_from_vstr(&mp_type_bytes, &vstr);
    }
    mp_raise_ValueError("Unsupported hash type");
    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR(hashlib_pbkdf2_hmac_obj, 4, hashlib_pbkdf2_hmac);

/************************** hmac_sha512 **************************/

STATIC mp_obj_t hashlib_hmac_sha512(mp_uint_t n_args, const mp_obj_t *args){
    //mp_obj_t key, mp_obj_t msg
    mp_buffer_info_t keybuf;
    mp_get_buffer_raise(args[0], &keybuf, MP_BUFFER_READ);
    mp_buffer_info_t msgbuf;
    mp_get_buffer_raise(args[1], &msgbuf, MP_BUFFER_READ);
    vstr_t vstr;
    vstr_init_len(&vstr, 64);
    hmac_sha512_oneline(keybuf.buf, keybuf.len, msgbuf.buf, msgbuf.len, (byte*)vstr.buf);
    return mp_obj_new_str_from_vstr(&mp_type_bytes, &vstr);
}

STATIC MP_DEFINE_CONST_FUN_OBJ_VAR(hashlib_hmac_sha512_obj, 2, hashlib_hmac_sha512);

STATIC mp_obj_t hashlib_new(size_t n_args, const mp_obj_t *args) {
    mp_buffer_info_t typebuf;
    mp_get_buffer_raise(args[0], &typebuf, MP_BUFFER_READ);
    if(strcmp(typebuf.buf, "ripemd160") == 0){
        return hashlib_ripemd160_make_new(&hashlib_ripemd160_type, n_args-1, 0, args+1);
    }
    if(strcmp(typebuf.buf, "sha256") == 0){
        return hashlib_sha256_make_new(&hashlib_sha256_type, n_args-1, 0, args+1);
    }
    if(strcmp(typebuf.buf, "sha512") == 0){
        return hashlib_sha512_make_new(&hashlib_sha512_type, n_args-1, 0, args+1);
    }
    if(strcmp(typebuf.buf, "sha1") == 0){
        return hashlib_sha1_make_new(&hashlib_sha1_type, n_args-1, 0, args+1);
    }
    mp_raise_ValueError("Unsupported hash type");
    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR(hashlib_new_obj, 1, hashlib_new);


/****************************** MODULE ******************************/

STATIC const mp_rom_map_elem_t hashlib_module_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_hashlib) },
    { MP_ROM_QSTR(MP_QSTR_new), MP_ROM_PTR(&hashlib_new_obj) },
    { MP_ROM_QSTR(MP_QSTR_sha1), MP_ROM_PTR(&hashlib_sha1_type) },
    { MP_ROM_QSTR(MP_QSTR_sha256), MP_ROM_PTR(&hashlib_sha256_type) },
    { MP_ROM_QSTR(MP_QSTR_sha512), MP_ROM_PTR(&hashlib_sha512_type) },
    { MP_ROM_QSTR(MP_QSTR_ripemd160), MP_ROM_PTR(&hashlib_ripemd160_type) },
    { MP_ROM_QSTR(MP_QSTR_pbkdf2_hmac), MP_ROM_PTR(&hashlib_pbkdf2_hmac_obj) },
    { MP_ROM_QSTR(MP_QSTR_hmac_sha512), MP_ROM_PTR(&hashlib_hmac_sha512_obj) },
};

STATIC MP_DEFINE_CONST_DICT(hashlib_module_globals, hashlib_module_globals_table);

const mp_obj_module_t hashlib_user_cmodule = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t*)&hashlib_module_globals,
};

MP_REGISTER_MODULE(MP_QSTR_hashlib, hashlib_user_cmodule, MODULE_HASHLIB_ENABLED);
