#include <assert.h>
#include <string.h>
#include <stdlib.h>
#include "include/secp256k1.h"
#include "include/secp256k1_preallocated.h"
#include "include/secp256k1_extrakeys.h"
#include "include/secp256k1_schnorrsig.h"
#include "include/secp256k1_recovery.h"
#include "py/obj.h"
#include "py/runtime.h"
#include "py/builtin.h"
#include "py/gc.h"

#define malloc(b) gc_alloc((b), false)
#define free gc_free

// newer versions of micropython require usage of MP_ERROR_TEXT
// but older don't know about it
#ifndef MP_ERROR_TEXT
#define MP_ERROR_TEXT(x) (x)
#endif

// global context
#define PREALLOCATED_CTX_SIZE 880 // 440 for 32-bit. FIXME: autodetect

STATIC unsigned char preallocated_ctx[PREALLOCATED_CTX_SIZE];
STATIC secp256k1_context * ctx = NULL;

void maybe_init_ctx(){
    if(ctx != NULL){
        return;
    }
    // ctx = secp256k1_context_create(SECP256K1_CONTEXT_VERIFY | SECP256K1_CONTEXT_SIGN);
    ctx = secp256k1_context_preallocated_create((void *)preallocated_ctx, SECP256K1_CONTEXT_VERIFY | SECP256K1_CONTEXT_SIGN);
}

// randomize context using 32-byte seed
STATIC mp_obj_t usecp256k1_context_randomize(const mp_obj_t seed){
    maybe_init_ctx();
    mp_buffer_info_t seedbuf;
    mp_get_buffer_raise(seed, &seedbuf, MP_BUFFER_READ);
    if(seedbuf.len != 32){
        mp_raise_ValueError(MP_ERROR_TEXT("Seed should be 32 bytes long"));
        return mp_const_none;
    }
    int res = secp256k1_context_randomize(ctx, seedbuf.buf);
    if(!res){
        mp_raise_ValueError(MP_ERROR_TEXT("Failed to randomize context"));
        return mp_const_none;
    }
    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(usecp256k1_context_randomize_obj, usecp256k1_context_randomize);

// create public key from private key
STATIC mp_obj_t usecp256k1_ec_pubkey_create(const mp_obj_t arg){
    maybe_init_ctx();
    mp_buffer_info_t secretbuf;
    mp_get_buffer_raise(arg, &secretbuf, MP_BUFFER_READ);
    if(secretbuf.len != 32){
        mp_raise_ValueError(MP_ERROR_TEXT("Private key should be 32 bytes long"));
        return mp_const_none;
    }
    secp256k1_pubkey pubkey;
    int res = secp256k1_ec_pubkey_create(ctx, &pubkey, secretbuf.buf);
    if(!res){
        mp_raise_ValueError(MP_ERROR_TEXT("Invalid private key"));
        return mp_const_none;
    }
    vstr_t vstr;
    vstr_init_len(&vstr, 64);
    memcpy((byte*)vstr.buf, pubkey.data, 64);

    return mp_obj_new_str_from_vstr(&mp_type_bytes, &vstr);
}

STATIC MP_DEFINE_CONST_FUN_OBJ_1(usecp256k1_ec_pubkey_create_obj, usecp256k1_ec_pubkey_create);

// parse sec-encoded public key
STATIC mp_obj_t usecp256k1_ec_pubkey_parse(const mp_obj_t arg){
    maybe_init_ctx();
    mp_buffer_info_t secbuf;
    mp_get_buffer_raise(arg, &secbuf, MP_BUFFER_READ);
    if(secbuf.len != 33 && secbuf.len != 65){
        mp_raise_ValueError(MP_ERROR_TEXT("Serialized pubkey should be 33 or 65 bytes long"));
        return mp_const_none;
    }
    byte * buf = (byte*)secbuf.buf;
    switch(secbuf.len){
        case 33:
            if(buf[0] != 0x02 && buf[0] != 0x03){
                mp_raise_ValueError(MP_ERROR_TEXT("Compressed pubkey should start with 0x02 or 0x03"));
                return mp_const_none;
            }
            break;
        case 65:
            if(buf[0] != 0x04){
                mp_raise_ValueError(MP_ERROR_TEXT("Uncompressed pubkey should start with 0x04"));
                return mp_const_none;
            }
            break;
    }
    secp256k1_pubkey pubkey;
    int res = secp256k1_ec_pubkey_parse(ctx, &pubkey, secbuf.buf, secbuf.len);
    if(!res){
        mp_raise_ValueError(MP_ERROR_TEXT("Failed parsing public key"));
        return mp_const_none;
    }
    vstr_t vstr;
    vstr_init_len(&vstr, 64);
    memcpy((byte*)vstr.buf, pubkey.data, 64);

    return mp_obj_new_str_from_vstr(&mp_type_bytes, &vstr);
}

STATIC MP_DEFINE_CONST_FUN_OBJ_1(usecp256k1_ec_pubkey_parse_obj, usecp256k1_ec_pubkey_parse);

// serialize public key
STATIC mp_obj_t usecp256k1_ec_pubkey_serialize(mp_uint_t n_args, const mp_obj_t *args){
    maybe_init_ctx();
    mp_buffer_info_t pubbuf;
    mp_get_buffer_raise(args[0], &pubbuf, MP_BUFFER_READ);
    if(pubbuf.len != 64){
        mp_raise_ValueError(MP_ERROR_TEXT("Pubkey should be 64 bytes long"));
        return mp_const_none;
    }
    secp256k1_pubkey pubkey;
    memcpy(pubkey.data, pubbuf.buf, 64);
    mp_int_t flag = SECP256K1_EC_COMPRESSED;
    if(n_args > 1){
        flag = mp_obj_get_int(args[1]);
    }
    byte out[65];
    size_t len = 65;
    int res = secp256k1_ec_pubkey_serialize(ctx, out, &len, &pubkey, flag);
    if(!res){
        mp_raise_ValueError(MP_ERROR_TEXT("Failed serializing public key"));
        return mp_const_none;
    }
    vstr_t vstr;
    vstr_init_len(&vstr, len);
    memcpy((byte*)vstr.buf, out, len);
    return mp_obj_new_str_from_vstr(&mp_type_bytes, &vstr);
}

STATIC MP_DEFINE_CONST_FUN_OBJ_VAR(usecp256k1_ec_pubkey_serialize_obj, 1, usecp256k1_ec_pubkey_serialize);

// parse compact ecdsa signature
STATIC mp_obj_t usecp256k1_ecdsa_signature_parse_compact(const mp_obj_t arg){
    maybe_init_ctx();
    mp_buffer_info_t buf;
    mp_get_buffer_raise(arg, &buf, MP_BUFFER_READ);
    if(buf.len != 64){
        mp_raise_ValueError(MP_ERROR_TEXT("Compact signature should be 64 bytes long"));
        return mp_const_none;
    }
    secp256k1_ecdsa_signature sig;
    int res = secp256k1_ecdsa_signature_parse_compact(ctx, &sig, buf.buf);
    if(!res){
        mp_raise_ValueError(MP_ERROR_TEXT("Failed parsing compact signature"));
        return mp_const_none;
    }
    vstr_t vstr;
    vstr_init_len(&vstr, 64);
    memcpy((byte*)vstr.buf, sig.data, 64);

    return mp_obj_new_str_from_vstr(&mp_type_bytes, &vstr);
}

STATIC MP_DEFINE_CONST_FUN_OBJ_1(usecp256k1_ecdsa_signature_parse_compact_obj, usecp256k1_ecdsa_signature_parse_compact);

// parse der ecdsa signature
STATIC mp_obj_t usecp256k1_ecdsa_signature_parse_der(const mp_obj_t arg){
    maybe_init_ctx();
    mp_buffer_info_t buf;
    mp_get_buffer_raise(arg, &buf, MP_BUFFER_READ);
    secp256k1_ecdsa_signature sig;
    int res = secp256k1_ecdsa_signature_parse_der(ctx, &sig, buf.buf, buf.len);
    if(!res){
        mp_raise_ValueError(MP_ERROR_TEXT("Failed parsing der signature"));
        return mp_const_none;
    }
    vstr_t vstr;
    vstr_init_len(&vstr, 64);
    memcpy((byte*)vstr.buf, sig.data, 64);

    return mp_obj_new_str_from_vstr(&mp_type_bytes, &vstr);
}

STATIC MP_DEFINE_CONST_FUN_OBJ_1(usecp256k1_ecdsa_signature_parse_der_obj, usecp256k1_ecdsa_signature_parse_der);

// serialize der ecdsa signature
STATIC mp_obj_t usecp256k1_ecdsa_signature_serialize_der(const mp_obj_t arg){
    maybe_init_ctx();
    mp_buffer_info_t buf;
    mp_get_buffer_raise(arg, &buf, MP_BUFFER_READ);
    if(buf.len != 64){
        mp_raise_ValueError(MP_ERROR_TEXT("Signature should be 64 bytes long"));
        return mp_const_none;
    }
    secp256k1_ecdsa_signature sig;
    memcpy(sig.data, buf.buf, 64);
    byte out[78];
    size_t len = 78;
    int res = secp256k1_ecdsa_signature_serialize_der(ctx, out, &len, &sig);
    if(!res){
        mp_raise_ValueError(MP_ERROR_TEXT("Failed serializing der signature"));
        return mp_const_none;
    }
    vstr_t vstr;
    vstr_init_len(&vstr, len);
    memcpy((byte*)vstr.buf, out, len);

    return mp_obj_new_str_from_vstr(&mp_type_bytes, &vstr);
}

STATIC MP_DEFINE_CONST_FUN_OBJ_1(usecp256k1_ecdsa_signature_serialize_der_obj, usecp256k1_ecdsa_signature_serialize_der);

// serialize compact ecdsa signature
STATIC mp_obj_t usecp256k1_ecdsa_signature_serialize_compact(const mp_obj_t arg){
    maybe_init_ctx();
    mp_buffer_info_t buf;
    mp_get_buffer_raise(arg, &buf, MP_BUFFER_READ);
    if(buf.len != 64){
        mp_raise_ValueError(MP_ERROR_TEXT("Signature should be 64 bytes long"));
        return mp_const_none;
    }
    secp256k1_ecdsa_signature sig;
    memcpy(sig.data, buf.buf, 64);
    vstr_t vstr;
    vstr_init_len(&vstr, 64);
    secp256k1_ecdsa_signature_serialize_compact(ctx, (byte*)vstr.buf, &sig);
    return mp_obj_new_str_from_vstr(&mp_type_bytes, &vstr);
}

STATIC MP_DEFINE_CONST_FUN_OBJ_1(usecp256k1_ecdsa_signature_serialize_compact_obj, usecp256k1_ecdsa_signature_serialize_compact);

// verify ecdsa signature
STATIC mp_obj_t usecp256k1_ecdsa_verify(const mp_obj_t sigarg, const mp_obj_t msgarg, const mp_obj_t pubkeyarg){
    maybe_init_ctx();
    mp_buffer_info_t buf;
    mp_get_buffer_raise(sigarg, &buf, MP_BUFFER_READ);
    if(buf.len != 64){
        mp_raise_ValueError(MP_ERROR_TEXT("Signature should be 64 bytes long"));
        return mp_const_none;
    }
    secp256k1_ecdsa_signature sig;
    memcpy(sig.data, buf.buf, 64);

    mp_get_buffer_raise(msgarg, &buf, MP_BUFFER_READ);
    if(buf.len != 32){
        mp_raise_ValueError(MP_ERROR_TEXT("Message should be 32 bytes long"));
        return mp_const_none;
    }
    byte msg[32];
    memcpy(msg, buf.buf, 32);

    mp_get_buffer_raise(pubkeyarg, &buf, MP_BUFFER_READ);
    if(buf.len != 64){
        mp_raise_ValueError(MP_ERROR_TEXT("Public key should be 64 bytes long"));
        return mp_const_none;
    }
    secp256k1_pubkey pub;
    memcpy(pub.data, buf.buf, 64);

    int res = secp256k1_ecdsa_verify(ctx, &sig, msg, &pub);
    if(res){
        return mp_const_true;
    }
    return mp_const_false;
}

STATIC MP_DEFINE_CONST_FUN_OBJ_3(usecp256k1_ecdsa_verify_obj, usecp256k1_ecdsa_verify);

// normalize ecdsa signature
STATIC mp_obj_t usecp256k1_ecdsa_signature_normalize(const mp_obj_t arg){
    maybe_init_ctx();
    mp_buffer_info_t buf;
    mp_get_buffer_raise(arg, &buf, MP_BUFFER_READ);
    if(buf.len != 64){
        mp_raise_ValueError(MP_ERROR_TEXT("Signature should be 64 bytes long"));
        return mp_const_none;
    }
    secp256k1_ecdsa_signature sig;
    secp256k1_ecdsa_signature sig2;
    memcpy(sig.data, buf.buf, 64);
    vstr_t vstr;
    vstr_init_len(&vstr, 64);
    secp256k1_ecdsa_signature_normalize(ctx, &sig2, &sig);
    memcpy(vstr.buf, sig2.data, 64);
    return mp_obj_new_str_from_vstr(&mp_type_bytes, &vstr);
}

STATIC MP_DEFINE_CONST_FUN_OBJ_1(usecp256k1_ecdsa_signature_normalize_obj, usecp256k1_ecdsa_signature_normalize);

// same as secp256k1_nonce_function_rfc6979
STATIC mp_obj_t usecp256k1_nonce_function_default(mp_uint_t n_args, const mp_obj_t *args){
    mp_buffer_info_t msgbuf;
    mp_get_buffer_raise(args[0], &msgbuf, MP_BUFFER_READ);
    if(msgbuf.len != 32){
        mp_raise_ValueError(MP_ERROR_TEXT("Message should be 32 bytes long"));
        return mp_const_none;
    }
    mp_buffer_info_t secbuf;
    mp_get_buffer_raise(args[1], &secbuf, MP_BUFFER_READ);
    if(secbuf.len != 32){
        mp_raise_ValueError(MP_ERROR_TEXT("Secret should be 32 bytes long"));
        return mp_const_none;
    }
    unsigned char *algo16 = NULL;
    void *data = NULL;
    int attempt = 0;
    // result
    vstr_t nonce;
    vstr_init_len(&nonce, 32);
    if(n_args > 2){
        if(args[2] != mp_const_none){
            mp_buffer_info_t algbuf;
            mp_get_buffer_raise(args[0], &algbuf, MP_BUFFER_READ);
            algo16 = algbuf.buf;
        }
        if(n_args > 3 && args[3]!=mp_const_none){
            mp_buffer_info_t databuf;
            if (!mp_get_buffer(args[3], &databuf, MP_BUFFER_READ)) {
                data = (void*) args[3];
            }else{
                data = (void*) databuf.buf;
            }
        }
        if(n_args > 4){
            attempt = mp_obj_get_int(args[4]);
        }
    }
    int res = secp256k1_nonce_function_default((unsigned char*)nonce.buf, msgbuf.buf, secbuf.buf, algo16, data, attempt);
    if(!res){
        mp_raise_ValueError(MP_ERROR_TEXT("Failed to calculate nonce"));
        return mp_const_none;
    }
    return mp_obj_new_str_from_vstr(&mp_type_bytes, &nonce);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR(usecp256k1_nonce_function_default_obj, 2, usecp256k1_nonce_function_default);

STATIC mp_obj_t mp_nonce_callback = NULL;
STATIC mp_obj_t mp_nonce_data = NULL;

STATIC int usecp256k1_nonce_function(
    unsigned char *nonce32,
    const unsigned char *msg32,
    const unsigned char *key32,
    const unsigned char *algo16,
    void *data,
    unsigned int attempt
    ){

    return secp256k1_nonce_function_default(nonce32, msg32, key32, algo16, data, attempt);
    // TODO: make nonce function compatible with ctypes
    // if(!mp_obj_is_callable(mp_nonce_callback)){
    //     mp_raise_ValueError(MP_ERROR_TEXT("Nonce callback should be callable..."));
    //     return mp_const_none;
    // }

    // if(attempt > 100){
    //     mp_raise_ValueError(MP_ERROR_TEXT("Too many attempts... Invalid function?"));
    //     // not sure it will ever get here, but just in case
    //     return secp256k1_nonce_function_default(nonce32, msg32, key32, algo16, data, attempt);
    // }
    // mp_obj_t mp_args[5];
    // mp_args[0] = mp_obj_new_bytes(msg32, 32);
    // mp_args[1] = mp_obj_new_bytes(key32, 32);
    // if(algo16!=NULL){
    //     mp_args[2] = mp_obj_new_bytes(key32, 16);
    // }else{
    //     mp_args[2] = mp_const_none;
    // }
    // if(mp_nonce_data!=NULL){
    //     mp_args[3] = mp_nonce_data;
    // }else{
    //     mp_args[3] = mp_const_none;
    // }
    // mp_args[4] = mp_obj_new_int_from_uint(attempt);

    // mp_obj_t mp_res = mp_call_function_n_kw(mp_nonce_callback , 5, 0, mp_args);
    // if(mp_res == mp_const_none){
    //     return 0;
    // }
    // mp_buffer_info_t buffer_info;
    // if (!mp_get_buffer(mp_res, &buffer_info, MP_BUFFER_READ)) {
    //     return 0;
    // }
    // if(buffer_info.len < 32){
    //     mp_raise_ValueError(MP_ERROR_TEXT("Returned nonce is less than 32 bytes"));
    //     return 0;
    // }
    // memcpy(nonce32, (byte*)buffer_info.buf, 32);
    // return 1;
}

// msg, secret, [callback, data]
STATIC mp_obj_t usecp256k1_ecdsa_sign(mp_uint_t n_args, const mp_obj_t *args){
    maybe_init_ctx();
    mp_nonce_data = NULL;
    if(n_args < 2){
        mp_raise_ValueError(MP_ERROR_TEXT("Function requires at least two arguments: message and private key"));
        return mp_const_none;
    }
    mp_buffer_info_t msgbuf;
    mp_get_buffer_raise(args[0], &msgbuf, MP_BUFFER_READ);
    if(msgbuf.len != 32){
        mp_raise_ValueError(MP_ERROR_TEXT("Message should be 32 bytes long"));
        return mp_const_none;
    }

    mp_buffer_info_t secbuf;
    mp_get_buffer_raise(args[1], &secbuf, MP_BUFFER_READ);
    if(secbuf.len != 32){
        mp_raise_ValueError(MP_ERROR_TEXT("Secret key should be 32 bytes long"));
        return mp_const_none;
    }
    secp256k1_ecdsa_signature sig;

    mp_buffer_info_t databuf;
    void * data = NULL;

    int res=0;
    if(n_args == 2){
        res = secp256k1_ecdsa_sign(ctx, &sig, msgbuf.buf, secbuf.buf, NULL, NULL);
    }else if(n_args >= 3){
        mp_nonce_callback = args[2];
        if(n_args > 3){
            mp_get_buffer_raise(args[3], &databuf, MP_BUFFER_READ);
            if(databuf.len != 32){
                mp_raise_ValueError(MP_ERROR_TEXT("Data should be 32 bytes long"));
                return mp_const_none;
            }
            data = databuf.buf;
        }
        res = secp256k1_ecdsa_sign(ctx, &sig, msgbuf.buf, secbuf.buf, usecp256k1_nonce_function, data);
    }
    if(!res){
        mp_raise_ValueError(MP_ERROR_TEXT("Failed to sign"));
        return mp_const_none;
    }

    vstr_t vstr;
    vstr_init_len(&vstr, 64);
    memcpy((byte*)vstr.buf, sig.data, 64);

    return mp_obj_new_str_from_vstr(&mp_type_bytes, &vstr);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR(usecp256k1_ecdsa_sign_obj, 2, usecp256k1_ecdsa_sign);

// verify secret key
STATIC mp_obj_t usecp256k1_ec_seckey_verify(const mp_obj_t arg){
    maybe_init_ctx();
    mp_buffer_info_t buf;
    mp_get_buffer_raise(arg, &buf, MP_BUFFER_READ);
    if(buf.len != 32){
        mp_raise_ValueError(MP_ERROR_TEXT("Private key should be 32 bytes long"));
        return mp_const_none;
    }

    int res = secp256k1_ec_seckey_verify(ctx, buf.buf);
    if(res){
        return mp_const_true;
    }
    return mp_const_false;
}

STATIC MP_DEFINE_CONST_FUN_OBJ_1(usecp256k1_ec_seckey_verify_obj, usecp256k1_ec_seckey_verify);

// return N - secret key
STATIC mp_obj_t usecp256k1_ec_privkey_negate(mp_obj_t arg){
    maybe_init_ctx();
    mp_buffer_info_t buf;
    mp_get_buffer_raise(arg, &buf, MP_BUFFER_READ);
    if(buf.len != 32){
        mp_raise_ValueError(MP_ERROR_TEXT("Private key should be 32 bytes long"));
        return mp_const_none;
    }

    vstr_t vstr;
    vstr_init_len(&vstr, 32);
    memcpy((byte*)vstr.buf, buf.buf, 32);

    int res = secp256k1_ec_privkey_negate(ctx, (unsigned char *)vstr.buf);
    if(!res){ // never happens according to the API
        mp_raise_ValueError(MP_ERROR_TEXT("Failed to negate the private key"));
        return mp_const_none;
    }
    return mp_obj_new_str_from_vstr(&mp_type_bytes, &vstr);
}

STATIC MP_DEFINE_CONST_FUN_OBJ_1(usecp256k1_ec_privkey_negate_obj, usecp256k1_ec_privkey_negate);

// return neg of pubkey
STATIC mp_obj_t usecp256k1_ec_pubkey_negate(mp_obj_t arg){
    maybe_init_ctx();
    mp_buffer_info_t buf;
    mp_get_buffer_raise(arg, &buf, MP_BUFFER_READ);
    if(buf.len != 64){
        mp_raise_ValueError(MP_ERROR_TEXT("Publick key should be 64 bytes long"));
        return mp_const_none;
    }

    vstr_t vstr;
    vstr_init_len(&vstr, 64);
    memcpy((byte*)vstr.buf, buf.buf, 64);

    int res = secp256k1_ec_pubkey_negate(ctx, (secp256k1_pubkey *)vstr.buf);
    if(!res){ // never happens according to the API
        mp_raise_ValueError(MP_ERROR_TEXT("Failed to negate the public key"));
        return mp_const_none;
    }
    return mp_obj_new_str_from_vstr(&mp_type_bytes, &vstr);
}

STATIC MP_DEFINE_CONST_FUN_OBJ_1(usecp256k1_ec_pubkey_negate_obj, usecp256k1_ec_pubkey_negate);

// tweak private key in place
STATIC mp_obj_t usecp256k1_ec_privkey_tweak_add(mp_obj_t privarg, const mp_obj_t tweakarg){
    maybe_init_ctx();
    mp_buffer_info_t privbuf;
    mp_get_buffer_raise(privarg, &privbuf, MP_BUFFER_READ);
    if(privbuf.len != 32){
        mp_raise_ValueError(MP_ERROR_TEXT("Private key should be 32 bytes long"));
        return mp_const_none;
    }

    mp_buffer_info_t tweakbuf;
    mp_get_buffer_raise(tweakarg, &tweakbuf, MP_BUFFER_READ);
    if(tweakbuf.len != 32){
        mp_raise_ValueError(MP_ERROR_TEXT("Tweak should be 32 bytes long"));
        return mp_const_none;
    }

    int res = secp256k1_ec_privkey_tweak_add(ctx, privbuf.buf, tweakbuf.buf);
    if(!res){ // never happens according to the API
        mp_raise_ValueError(MP_ERROR_TEXT("Failed to tweak the private key"));
        return mp_const_none;
    }
    return mp_const_none;
}

STATIC MP_DEFINE_CONST_FUN_OBJ_2(usecp256k1_ec_privkey_tweak_add_obj, usecp256k1_ec_privkey_tweak_add);

// add private key
STATIC mp_obj_t usecp256k1_ec_privkey_add(mp_obj_t privarg, const mp_obj_t tweakarg){
    maybe_init_ctx();
    mp_buffer_info_t privbuf;
    mp_get_buffer_raise(privarg, &privbuf, MP_BUFFER_READ);
    if(privbuf.len != 32){
        mp_raise_ValueError("Private key should be 32 bytes long");
        return mp_const_none;
    }

    mp_buffer_info_t tweakbuf;
    mp_get_buffer_raise(tweakarg, &tweakbuf, MP_BUFFER_READ);
    if(tweakbuf.len != 32){
        mp_raise_ValueError("Tweak should be 32 bytes long");
        return mp_const_none;
    }

    vstr_t priv2;
    vstr_init_len(&priv2, 32);
    memcpy((byte*)priv2.buf, privbuf.buf, 32);

    int res = secp256k1_ec_privkey_tweak_add(ctx, priv2.buf, tweakbuf.buf);
    if(!res){ // never happens according to the API
        mp_raise_ValueError("Failed to tweak the private key");
        return mp_const_none;
    }
    return mp_obj_new_str_from_vstr(&mp_type_bytes, &priv2);
}

STATIC MP_DEFINE_CONST_FUN_OBJ_2(usecp256k1_ec_privkey_add_obj, usecp256k1_ec_privkey_add);

// tweak public key in place (add tweak * Generator)
STATIC mp_obj_t usecp256k1_ec_pubkey_tweak_add(mp_obj_t pubarg, const mp_obj_t tweakarg){
    maybe_init_ctx();
    mp_buffer_info_t pubbuf;
    mp_get_buffer_raise(pubarg, &pubbuf, MP_BUFFER_READ);
    if(pubbuf.len != 64){
        mp_raise_ValueError(MP_ERROR_TEXT("Public key should be 64 bytes long"));
        return mp_const_none;
    }
    secp256k1_pubkey pub;
    memcpy(pub.data, pubbuf.buf, 64);

    mp_buffer_info_t tweakbuf;
    mp_get_buffer_raise(tweakarg, &tweakbuf, MP_BUFFER_READ);
    if(tweakbuf.len != 32){
        mp_raise_ValueError(MP_ERROR_TEXT("Tweak should be 32 bytes long"));
        return mp_const_none;
    }

    int res = secp256k1_ec_pubkey_tweak_add(ctx, &pub, tweakbuf.buf);
    if(!res){ // never happens according to the API
        mp_raise_ValueError(MP_ERROR_TEXT("Failed to tweak the public key"));
        return mp_const_none;
    }
    memcpy(pubbuf.buf, pub.data, 64);
    return mp_const_none;
}

STATIC MP_DEFINE_CONST_FUN_OBJ_2(usecp256k1_ec_pubkey_tweak_add_obj, usecp256k1_ec_pubkey_tweak_add);

// add tweak * Generator
STATIC mp_obj_t usecp256k1_ec_pubkey_add(mp_obj_t pubarg, const mp_obj_t tweakarg){
    maybe_init_ctx();
    mp_buffer_info_t pubbuf;
    mp_get_buffer_raise(pubarg, &pubbuf, MP_BUFFER_READ);
    if(pubbuf.len != 64){
        mp_raise_ValueError("Public key should be 64 bytes long");
        return mp_const_none;
    }
    secp256k1_pubkey pub;
    memcpy(pub.data, pubbuf.buf, 64);

    mp_buffer_info_t tweakbuf;
    mp_get_buffer_raise(tweakarg, &tweakbuf, MP_BUFFER_READ);
    if(tweakbuf.len != 32){
        mp_raise_ValueError("Tweak should be 32 bytes long");
        return mp_const_none;
    }

    int res = secp256k1_ec_pubkey_tweak_add(ctx, &pub, tweakbuf.buf);
    if(!res){ // never happens according to the API
        mp_raise_ValueError("Failed to tweak the public key");
        return mp_const_none;
    }

    vstr_t pubbuf2;
    vstr_init_len(&pubbuf2, 64);
    memcpy((byte*)pubbuf2.buf, pub.data, 64);
    return mp_obj_new_str_from_vstr(&mp_type_bytes, &pubbuf2);
}

STATIC MP_DEFINE_CONST_FUN_OBJ_2(usecp256k1_ec_pubkey_add_obj, usecp256k1_ec_pubkey_add);

// tweak private key in place (multiply by tweak)
STATIC mp_obj_t usecp256k1_ec_privkey_tweak_mul(mp_obj_t privarg, const mp_obj_t tweakarg){
    maybe_init_ctx();
    mp_buffer_info_t privbuf;
    mp_get_buffer_raise(privarg, &privbuf, MP_BUFFER_READ);
    if(privbuf.len != 32){
        mp_raise_ValueError(MP_ERROR_TEXT("Private key should be 32 bytes long"));
        return mp_const_none;
    }

    mp_buffer_info_t tweakbuf;
    mp_get_buffer_raise(tweakarg, &tweakbuf, MP_BUFFER_READ);
    if(tweakbuf.len != 32){
        mp_raise_ValueError(MP_ERROR_TEXT("Tweak should be 32 bytes long"));
        return mp_const_none;
    }

    int res = secp256k1_ec_privkey_tweak_mul(ctx, privbuf.buf, tweakbuf.buf);
    if(!res){ // never happens according to the API
        mp_raise_ValueError(MP_ERROR_TEXT("Failed to tweak the public key"));
        return mp_const_none;
    }
    return mp_const_none;
}

STATIC MP_DEFINE_CONST_FUN_OBJ_2(usecp256k1_ec_privkey_tweak_mul_obj, usecp256k1_ec_privkey_tweak_mul);

// tweak public key in place (multiply by tweak)
STATIC mp_obj_t usecp256k1_ec_pubkey_tweak_mul(mp_obj_t pubarg, const mp_obj_t tweakarg){
    maybe_init_ctx();
    mp_buffer_info_t pubbuf;
    mp_get_buffer_raise(pubarg, &pubbuf, MP_BUFFER_READ);
    if(pubbuf.len != 64){
        mp_raise_ValueError(MP_ERROR_TEXT("Public key should be 64 bytes long"));
        return mp_const_none;
    }
    secp256k1_pubkey pub;
    memcpy(pub.data, pubbuf.buf, 64);

    mp_buffer_info_t tweakbuf;
    mp_get_buffer_raise(tweakarg, &tweakbuf, MP_BUFFER_READ);
    if(tweakbuf.len != 32){
        mp_raise_ValueError(MP_ERROR_TEXT("Tweak should be 32 bytes long"));
        return mp_const_none;
    }

    int res = secp256k1_ec_pubkey_tweak_mul(ctx, &pub, tweakbuf.buf);
    if(!res){ // never happens according to the API
        mp_raise_ValueError(MP_ERROR_TEXT("Failed to tweak the public key"));
        return mp_const_none;
    }
    memcpy(pubbuf.buf, pub.data, 64);
    return mp_const_none;
}

STATIC MP_DEFINE_CONST_FUN_OBJ_2(usecp256k1_ec_pubkey_tweak_mul_obj, usecp256k1_ec_pubkey_tweak_mul);

// adds public keys
STATIC mp_obj_t usecp256k1_ec_pubkey_combine(mp_uint_t n_args, const mp_obj_t *args){
    maybe_init_ctx();
    secp256k1_pubkey pubkey;
    secp256k1_pubkey ** pubkeys;
    pubkeys = (secp256k1_pubkey **)malloc(sizeof(secp256k1_pubkey*)*n_args);
    mp_buffer_info_t pubbuf;
    for(unsigned int i=0; i<n_args; i++){ // TODO: can be refactored to avoid allocation
        mp_get_buffer_raise(args[i], &pubbuf, MP_BUFFER_READ);
        if(pubbuf.len != 64){
            for(unsigned int j=0; j<i; j++){
                free(pubkeys[j]);
            }
            free(pubkeys);
            mp_raise_ValueError(MP_ERROR_TEXT("All pubkeys should be 64 bytes long"));
            return mp_const_none;
        }
        pubkeys[i] = (secp256k1_pubkey *)malloc(64);
        memcpy(pubkeys[i]->data, pubbuf.buf, 64);
    }
    int res = secp256k1_ec_pubkey_combine(ctx, &pubkey, (const secp256k1_pubkey *const *)pubkeys, n_args);
    if(!res){
        mp_raise_ValueError(MP_ERROR_TEXT("Failed combining public keys"));
        return mp_const_none;
    }
    vstr_t vstr;
    vstr_init_len(&vstr, 64);
    memcpy((byte*)vstr.buf, pubkey.data, 64);
    for(unsigned int i=0; i<n_args; i++){
        free(pubkeys[i]);
    }
    free(pubkeys);
    return mp_obj_new_str_from_vstr(&mp_type_bytes, &vstr);
}

STATIC MP_DEFINE_CONST_FUN_OBJ_VAR(usecp256k1_ec_pubkey_combine_obj, 2, usecp256k1_ec_pubkey_combine);

/**************************** schnorrsig ****************************/

STATIC mp_obj_t usecp256k1_xonly_pubkey_from_pubkey(mp_obj_t arg){
    maybe_init_ctx();
    mp_buffer_info_t buf;
    mp_get_buffer_raise(arg, &buf, MP_BUFFER_READ);
    if(buf.len != 64){
        mp_raise_ValueError(MP_ERROR_TEXT("Public key should be 64 bytes long"));
        return mp_const_none;
    }

    vstr_t vstr;
    vstr_init_len(&vstr, 64);
    int parity = 0;

    int res = secp256k1_xonly_pubkey_from_pubkey(ctx, (secp256k1_xonly_pubkey *)vstr.buf, &parity, buf.buf);
    if(!res){
        mp_raise_ValueError(MP_ERROR_TEXT("Failed to convert the public key"));
        return mp_const_none;
    }

    mp_obj_t items[2];
    items[0] = mp_obj_new_str_from_vstr(&mp_type_bytes, &vstr);
    items[1] = mp_obj_new_int(parity);
    return mp_obj_new_tuple(2, items);
}

STATIC MP_DEFINE_CONST_FUN_OBJ_1(usecp256k1_xonly_pubkey_from_pubkey_obj, usecp256k1_xonly_pubkey_from_pubkey);


STATIC mp_obj_t usecp256k1_schnorrsig_verify(const mp_obj_t sigarg, const mp_obj_t msgarg, const mp_obj_t pubkeyarg){
    maybe_init_ctx();
    mp_buffer_info_t buf;
    mp_get_buffer_raise(sigarg, &buf, MP_BUFFER_READ);
    if(buf.len != 64){
        mp_raise_ValueError(MP_ERROR_TEXT("Signature should be 64 bytes long"));
        return mp_const_none;
    }
    byte sig[64];
    memcpy(sig, buf.buf, 64);

    mp_get_buffer_raise(msgarg, &buf, MP_BUFFER_READ);
    if(buf.len != 32){
        mp_raise_ValueError(MP_ERROR_TEXT("Message should be 32 bytes long"));
        return mp_const_none;
    }
    byte msg[32];
    memcpy(msg, buf.buf, 32);

    mp_get_buffer_raise(pubkeyarg, &buf, MP_BUFFER_READ);
    if(buf.len != 64){
        mp_raise_ValueError(MP_ERROR_TEXT("Public key should be 64 bytes long"));
        return mp_const_none;
    }
    secp256k1_xonly_pubkey pub;
    memcpy(pub.data, buf.buf, 64);

    int res = secp256k1_schnorrsig_verify(ctx, sig, msg, 32, &pub);
    if(res){
        return mp_const_true;
    }
    return mp_const_false;
}

STATIC MP_DEFINE_CONST_FUN_OBJ_3(usecp256k1_schnorrsig_verify_obj, usecp256k1_schnorrsig_verify);


STATIC mp_obj_t usecp256k1_keypair_create(mp_obj_t arg){
    maybe_init_ctx();
    mp_buffer_info_t buf;
    mp_get_buffer_raise(arg, &buf, MP_BUFFER_READ);
    if(buf.len != 32){
        mp_raise_ValueError(MP_ERROR_TEXT("Secret should be 32 bytes long"));
        return mp_const_none;
    }

    vstr_t vstr;
    vstr_init_len(&vstr, 96);

    int res = secp256k1_keypair_create(ctx, (secp256k1_keypair *)vstr.buf, buf.buf);
    if(!res){
        mp_raise_ValueError(MP_ERROR_TEXT("Failed to create keypair"));
        return mp_const_none;
    }

    return mp_obj_new_str_from_vstr(&mp_type_bytes, &vstr);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(usecp256k1_keypair_create_obj, usecp256k1_keypair_create);


// msg, secret, [callback, data]
STATIC mp_obj_t usecp256k1_schnorrsig_sign(mp_uint_t n_args, const mp_obj_t *args){
    maybe_init_ctx();
    mp_nonce_data = NULL;
    if(n_args < 2){
        mp_raise_ValueError(MP_ERROR_TEXT("Function requires at least two arguments: message and private key"));
        return mp_const_none;
    }
    mp_buffer_info_t msgbuf;
    mp_get_buffer_raise(args[0], &msgbuf, MP_BUFFER_READ);
    if(msgbuf.len != 32){
        mp_raise_ValueError(MP_ERROR_TEXT("Message should be 32 bytes long"));
        return mp_const_none;
    }

    mp_buffer_info_t secbuf;
    mp_get_buffer_raise(args[1], &secbuf, MP_BUFFER_READ);
    if(secbuf.len != 32 && secbuf.len != 96){
        mp_raise_ValueError(MP_ERROR_TEXT("Secret key should be 32 bytes long or 96 bytes long (keypair)"));
        return mp_const_none;
    }
    byte keypair[96];
    if(secbuf.len == 32){
        int res = secp256k1_keypair_create(ctx, (secp256k1_keypair *)keypair, secbuf.buf);
        if(!res){
            mp_raise_ValueError(MP_ERROR_TEXT("Failed to create keypair"));
            return mp_const_none;
        }
    }else{
        memcpy(keypair, secbuf.buf, 96);
    }
    byte sig[64];

    mp_buffer_info_t databuf;
    void * data = NULL;

    int res=0;
    if(n_args == 2){
        res = secp256k1_schnorrsig_sign(ctx, sig, msgbuf.buf, (secp256k1_keypair *)keypair, NULL);
    }else if(n_args >= 3){
        mp_nonce_callback = args[2];
        if(n_args > 3){
            mp_get_buffer_raise(args[3], &databuf, MP_BUFFER_READ);
            if(databuf.len != 32){
                mp_raise_ValueError(MP_ERROR_TEXT("Data should be 32 bytes long"));
                return mp_const_none;
            }
            data = databuf.buf;
        }
        res = secp256k1_schnorrsig_sign(ctx, sig, msgbuf.buf, (secp256k1_keypair *)keypair, data);
    }
    if(!res){
        mp_raise_ValueError(MP_ERROR_TEXT("Failed to sign"));
        return mp_const_none;
    }

    vstr_t vstr;
    vstr_init_len(&vstr, 64);
    memcpy((byte*)vstr.buf, sig, 64);

    return mp_obj_new_str_from_vstr(&mp_type_bytes, &vstr);
}

STATIC MP_DEFINE_CONST_FUN_OBJ_VAR(usecp256k1_schnorrsig_sign_obj, 2, usecp256k1_schnorrsig_sign);

/**************************** recoverable ***************************/

// msg, secret, [callback, data]
STATIC mp_obj_t usecp256k1_ecdsa_sign_recoverable(mp_uint_t n_args, const mp_obj_t *args){
    maybe_init_ctx();
    mp_nonce_data = NULL;
    if(n_args < 2){
        mp_raise_ValueError(MP_ERROR_TEXT("Function requires at least two arguments: message and private key"));
        return mp_const_none;
    }
    mp_buffer_info_t msgbuf;
    mp_get_buffer_raise(args[0], &msgbuf, MP_BUFFER_READ);
    if(msgbuf.len != 32){
        mp_raise_ValueError(MP_ERROR_TEXT("Message should be 32 bytes long"));
        return mp_const_none;
    }

    mp_buffer_info_t secbuf;
    mp_get_buffer_raise(args[1], &secbuf, MP_BUFFER_READ);
    if(secbuf.len != 32){
        mp_raise_ValueError(MP_ERROR_TEXT("Secret key should be 32 bytes long"));
        return mp_const_none;
    }
    secp256k1_ecdsa_recoverable_signature sig;
    int res=0;

    mp_buffer_info_t databuf;
    void * data = NULL;

    if(n_args == 2){
        res = secp256k1_ecdsa_sign_recoverable(ctx, &sig, msgbuf.buf, secbuf.buf, NULL, NULL);
    }else if(n_args >= 3){
        mp_nonce_callback = args[2];
        if(n_args > 3){
            mp_get_buffer_raise(args[3], &databuf, MP_BUFFER_READ);
            if(databuf.len != 32){
                mp_raise_ValueError(MP_ERROR_TEXT("Data should be 32 bytes long"));
                return mp_const_none;
            }
            data = databuf.buf;
        }
        res = secp256k1_ecdsa_sign_recoverable(ctx, &sig, msgbuf.buf, secbuf.buf, usecp256k1_nonce_function, data);
    }
    if(!res){
        mp_raise_ValueError(MP_ERROR_TEXT("Failed to sign"));
        return mp_const_none;
    }

    vstr_t vstr;
    vstr_init_len(&vstr, 65);
    memcpy((byte*)vstr.buf, sig.data, 65);

    return mp_obj_new_str_from_vstr(&mp_type_bytes, &vstr);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_VAR(usecp256k1_ecdsa_sign_recoverable_obj, 2, usecp256k1_ecdsa_sign_recoverable);

/****************************** MODULE ******************************/

STATIC const mp_rom_map_elem_t secp256k1_module_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_secp256k1) },
    { MP_ROM_QSTR(MP_QSTR_context_randomize), MP_ROM_PTR(&usecp256k1_context_randomize_obj) },
    { MP_ROM_QSTR(MP_QSTR_ec_pubkey_create), MP_ROM_PTR(&usecp256k1_ec_pubkey_create_obj) },
    { MP_ROM_QSTR(MP_QSTR_ec_pubkey_parse), MP_ROM_PTR(&usecp256k1_ec_pubkey_parse_obj) },
    { MP_ROM_QSTR(MP_QSTR_ec_pubkey_serialize), MP_ROM_PTR(&usecp256k1_ec_pubkey_serialize_obj) },
    { MP_ROM_QSTR(MP_QSTR_ecdsa_signature_parse_compact), MP_ROM_PTR(&usecp256k1_ecdsa_signature_parse_compact_obj) },
    { MP_ROM_QSTR(MP_QSTR_ecdsa_signature_parse_der), MP_ROM_PTR(&usecp256k1_ecdsa_signature_parse_der_obj) },
    { MP_ROM_QSTR(MP_QSTR_ecdsa_signature_serialize_der), MP_ROM_PTR(&usecp256k1_ecdsa_signature_serialize_der_obj) },
    { MP_ROM_QSTR(MP_QSTR_ecdsa_signature_serialize_compact), MP_ROM_PTR(&usecp256k1_ecdsa_signature_serialize_compact_obj) },
    { MP_ROM_QSTR(MP_QSTR_ecdsa_signature_normalize), MP_ROM_PTR(&usecp256k1_ecdsa_signature_normalize_obj) },
    { MP_ROM_QSTR(MP_QSTR_ecdsa_verify), MP_ROM_PTR(&usecp256k1_ecdsa_verify_obj) },
    { MP_ROM_QSTR(MP_QSTR_ecdsa_sign), MP_ROM_PTR(&usecp256k1_ecdsa_sign_obj) },
   // schnorrsig
    { MP_ROM_QSTR(MP_QSTR_xonly_pubkey_from_pubkey), MP_ROM_PTR(&usecp256k1_xonly_pubkey_from_pubkey_obj) },
    { MP_ROM_QSTR(MP_QSTR_schnorrsig_verify), MP_ROM_PTR(&usecp256k1_schnorrsig_verify_obj) },
    { MP_ROM_QSTR(MP_QSTR_keypair_create), MP_ROM_PTR(&usecp256k1_keypair_create_obj) },
    { MP_ROM_QSTR(MP_QSTR_schnorrsig_sign), MP_ROM_PTR(&usecp256k1_schnorrsig_sign_obj) },

    { MP_ROM_QSTR(MP_QSTR_ecdsa_sign_recoverable), MP_ROM_PTR(&usecp256k1_ecdsa_sign_recoverable_obj) },

    { MP_ROM_QSTR(MP_QSTR_nonce_function_default), MP_ROM_PTR(&usecp256k1_nonce_function_default_obj) },
    { MP_ROM_QSTR(MP_QSTR_nonce_function_rfc6979), MP_ROM_PTR(&usecp256k1_nonce_function_default_obj) },

    { MP_ROM_QSTR(MP_QSTR_ec_seckey_verify), MP_ROM_PTR(&usecp256k1_ec_seckey_verify_obj) },
    { MP_ROM_QSTR(MP_QSTR_ec_privkey_negate), MP_ROM_PTR(&usecp256k1_ec_privkey_negate_obj) },
    { MP_ROM_QSTR(MP_QSTR_ec_pubkey_negate), MP_ROM_PTR(&usecp256k1_ec_pubkey_negate_obj) },
    { MP_ROM_QSTR(MP_QSTR_ec_privkey_tweak_add), MP_ROM_PTR(&usecp256k1_ec_privkey_tweak_add_obj) },
    { MP_ROM_QSTR(MP_QSTR_ec_privkey_add), MP_ROM_PTR(&usecp256k1_ec_privkey_add_obj) },
    { MP_ROM_QSTR(MP_QSTR_ec_pubkey_tweak_add), MP_ROM_PTR(&usecp256k1_ec_pubkey_tweak_add_obj) },
    { MP_ROM_QSTR(MP_QSTR_ec_pubkey_add), MP_ROM_PTR(&usecp256k1_ec_pubkey_add_obj) },
    { MP_ROM_QSTR(MP_QSTR_ec_privkey_tweak_mul), MP_ROM_PTR(&usecp256k1_ec_privkey_tweak_mul_obj) },
    { MP_ROM_QSTR(MP_QSTR_ec_pubkey_tweak_mul), MP_ROM_PTR(&usecp256k1_ec_pubkey_tweak_mul_obj) },
    { MP_ROM_QSTR(MP_QSTR_ec_pubkey_combine), MP_ROM_PTR(&usecp256k1_ec_pubkey_combine_obj) },
    { MP_ROM_QSTR(MP_QSTR_EC_COMPRESSED), MP_ROM_INT(SECP256K1_EC_COMPRESSED) },
    { MP_ROM_QSTR(MP_QSTR_EC_UNCOMPRESSED), MP_ROM_INT(SECP256K1_EC_UNCOMPRESSED) },
};
STATIC MP_DEFINE_CONST_DICT(secp256k1_module_globals, secp256k1_module_globals_table);

// Define module object.
const mp_obj_module_t secp256k1_user_cmodule = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t*)&secp256k1_module_globals,
};

// Register the module to make it available in Python
MP_REGISTER_MODULE(MP_QSTR_secp256k1, secp256k1_user_cmodule, MODULE_SECP256K1_ENABLED);
