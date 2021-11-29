#ifndef SECP256K1_CONFIG_H
#define SECP256K1_CONFIG_H

#undef USE_ASM_X86_64
#undef USE_ECMULT_STATIC_PRECOMPUTATION
#undef USE_ENDOMORPHISM
#undef USE_EXTERNAL_ASM
#undef USE_EXTERNAL_DEFAULT_CALLBACKS
#undef USE_FIELD_10X26
#undef USE_FIELD_5X52
#undef USE_FIELD_INV_BUILTIN
#undef USE_FIELD_INV_NUM
#undef USE_NUM_GMP
#undef USE_NUM_NONE
#undef USE_SCALAR_4X64
#undef USE_SCALAR_8X32
#undef USE_SCALAR_INV_BUILTIN
#undef USE_SCALAR_INV_NUM
#undef ECMULT_WINDOW_SIZE

#define ENABLE_MODULE_ECDH 1
#define ENABLE_MODULE_RECOVERY 1
#define ENABLE_MODULE_EXTRAKEYS 1
#define ENABLE_MODULE_SCHNORRSIG 1

#define USE_NUM_NONE 1
#define USE_FIELD_INV_BUILTIN 1
#define USE_SCALAR_INV_BUILTIN 1
#define USE_FIELD_10X26 1
#define USE_SCALAR_8X32 1

#define USE_ECMULT_STATIC_PRECOMPUTATION 1
#define ECMULT_GEN_PREC_BITS 4
#define ECMULT_WINDOW_SIZE 4

#define HAVE_STDINT_H 1
#define HAVE_STDLIB_H 1
#define HAVE_STRING_H 1

#define USE_EXTERNAL_DEFAULT_CALLBACKS

// malloc and free in micropython
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "py/mpconfig.h"
#include "py/misc.h"
#include "py/mpstate.h"

#if MICROPY_ENABLE_GC
#include "py/gc.h"

// We redirect standard alloc functions to GC heap - just for the rest of
// this module. In the rest of MicroPython source, system malloc can be
// freely accessed - for interfacing with system and 3rd-party libs for
// example. On the other hand, some (e.g. bare-metal) ports may use GC
// heap as system heap, so, to avoid warnings, we do undef's first.
#undef malloc
#undef free
#undef realloc
#define malloc(b) gc_alloc((b), false)
#define malloc_with_finaliser(b) gc_alloc((b), true)
#define free gc_free
#define realloc(ptr, n) gc_realloc(ptr, n, true)
#define realloc_ext(ptr, n, mv) gc_realloc(ptr, n, mv)
#endif

#endif /* SECP256K1_CONFIG_H */
