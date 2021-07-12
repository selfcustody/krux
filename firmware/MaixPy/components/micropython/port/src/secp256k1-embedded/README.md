# secp256k1 for embedded systems: Arduino, Mbed and MicroPython

# About this repository

[secp256k1](https://github.com/bitcoin-core/secp256k1/) is an elliptic curve library developed and maintained by Bitcoin Core community.

**This repository** makes it easy to use the library with Arduino IDE, ARM Mbed and MicroPython. 

For Arduino and Mbed it introduces a few hacks to get around their recursive build system. For MicroPython it defines [bindings](./mpy/libsecp256k1.c) that makes the library accessible from MicroPython.

Tested on ESP32 (M5Stack, TTGO) and STM32F469I-Discovery, but should work on any 32-bit MCU.

# Installation

## MicroPython

Clone with `--recursive` flag to the folder where you store user modules.

Compile MicroPython for your board with user modules and `CFLAGS_EXTRA=-DMODULE_SECP256K1_ENABLED=1` flag. For example:

```sh
make BOARD=STM32F469DISC USER_C_MODULES=../../../usermods CFLAGS_EXTRA=-DMODULE_SECP256K1_ENABLED=1
```

Here replace `STM32F469DISC` to your board name, `../../../usermods` to your path to usermods folder.

Here is a usage example for MicroPython: [`examples/secp256k1.py`](examples/secp256k1.py)

## Arduino IDE

Clone this repo with `--recursive` flag to the `Arduino/libraries/` folder (or download zip file and select `Sketch->Include Library->Add .ZIP Library`. 

Check out the [example](examples/basic_example/basic_example.ino) for Arduino to see it in action.

## ARM Mbed

Clone this repo with `--recursive` flag to the project folder, or whatever folder you store libraries in. In the online IDE do `Import Library` and put there a link to this repository.

Check out the [example](examples/mbed/main.cpp). You can also import [this project](https://os.mbed.com/users/diybitcoinhardware/code/secp256k1_example/) and start from there.

**Important!** Library mostly uses stack, and mbed has pretty small default limitat for the stack size. You can increase the stack size in `mbed_app.json` file:

```json
{
    "target_overrides": {
        "*": {
            "rtos.main-thread-stack-size": "8192"
        }
    }
}
```

Or you can use bare-metal mbed version:

```json
{
	"requires": ["bare-metal"]
}
```

## Usage

A very basic example in C/C++:

```cpp
// secp256k1 context
secp256k1_context *ctx = NULL;

int res;    // to store results of function calls
size_t len; // to store serialization lengths

// first we need to create the context
// this is the size of memory to be allocated
size_t context_size = secp256k1_context_preallocated_size(SECP256K1_CONTEXT_VERIFY | SECP256K1_CONTEXT_SIGN);

// creating the context
ctx = secp256k1_context_create(SECP256K1_CONTEXT_VERIFY | SECP256K1_CONTEXT_SIGN);

// some random secret key
uint8_t secret[] = {
	0xbd, 0xb5, 0x1a, 0x16, 0xeb, 0x64, 0x60, 0xec, 
	0x16, 0xf8, 0x4d, 0x7b, 0x6f, 0x19, 0xe2, 0x0d, 
	0x9b, 0x9a, 0xb5, 0x58, 0xfa, 0x0e, 0x9a, 0xe4, 
	0xbb, 0x49, 0x3e, 0xf7, 0x79, 0xf1, 0x40, 0x55
};

// Makes sense to check if secret key is valid.
// It will be ok in most cases, only if secret > N it will be invalid
res = secp256k1_ec_seckey_verify(ctx, secret);
if(!res){ return; /* handle error here */ }

/**************** Public key ******************/

// computing corresponding pubkey
secp256k1_pubkey pubkey;
res = secp256k1_ec_pubkey_create(ctx, &pubkey, secret);
if(!res){ return; /* handle error here */ }

// serialize the pubkey in compressed format
uint8_t pub[33];
len = sizeof(pub);
secp256k1_ec_pubkey_serialize(ctx, pub, &len, &pubkey, SECP256K1_EC_COMPRESSED);

// this is how you parse the pubkey
res = secp256k1_ec_pubkey_parse(ctx, &pubkey, pub, 33);
if(res){
	// Key is valid
}else{
	// Invalid pubkey
}

/**************** Signature stuff ******************/

// hash of the string "hello"
uint8_t hash[32] = { 
	0x2c, 0xf2, 0x4d, 0xba, 0x5f, 0xb0, 0xa3, 0x0e, 
	0x26, 0xe8, 0x3b, 0x2a, 0xc5, 0xb9, 0xe2, 0x9e, 
	0x1b, 0x16, 0x1e, 0x5c, 0x1f, 0xa7, 0x42, 0x5e, 
	0x73, 0x04, 0x33, 0x62, 0x93, 0x8b, 0x98, 0x24 
};
// signing
secp256k1_ecdsa_signature sig;
res = secp256k1_ecdsa_sign(ctx, &sig, hash, secret, NULL, NULL);
if(!res){ return; /* handle error here */ }

// serialization
uint8_t der[72];
len = sizeof(der);
res = secp256k1_ecdsa_signature_serialize_der(ctx, der, &len, &sig);
if(!res){ return; /* handle error here */ }

// verification
res = secp256k1_ecdsa_verify(ctx, &sig, hash, &pubkey);
if(res){
	// Signature is valid
}else{
	// Invalid signature
}

secp256k1_context_destroy(ctx);
```