#include "mbed.h"
 
#include "secp256k1.h"
#include "secp256k1_preallocated.h"
 
RawSerial pc(SERIAL_TX, SERIAL_RX, 115200);
 
// small helper functions that prints 
// data in hex to the serial port
void print_hex(const uint8_t * data, size_t data_len){
    for(int i=0; i<data_len; i++){
        printf("%02x", data[i]);
    }
}
// just adds a new line to the end of the data
void println_hex(const uint8_t * data, size_t data_len){
    print_hex(data, data_len);
    printf("\r\n");
}
// prints error and hangs forever
void err(const char * message, void * data = NULL){
    printf("ERROR: %s\r\n", message);
    while(1){
        wait(1);
    }
}
 
void secp_example(){
    // secp256k1 context
    secp256k1_context *ctx = NULL;
 
    int res;    // to store results of function calls
    size_t len; // to store serialization lengths
 
    printf("=== secp256k1 context ===\r\n");
 
    // first we need to create the context
    // this is the size of memory to be allocated
    size_t context_size = secp256k1_context_preallocated_size(SECP256K1_CONTEXT_VERIFY | SECP256K1_CONTEXT_SIGN);
    printf("Context size: %u bytes\r\n", context_size);
 
    // creating the context
    ctx = secp256k1_context_create(SECP256K1_CONTEXT_VERIFY | SECP256K1_CONTEXT_SIGN);
    printf("Context created\r\n");
 
    printf("=== Secret key ===\r\n");
    // some random secret key
    uint8_t secret[] = {
        0xbd, 0xb5, 0x1a, 0x16, 0xeb, 0x64, 0x60, 0xec, 
        0x16, 0xf8, 0x4d, 0x7b, 0x6f, 0x19, 0xe2, 0x0d, 
        0x9b, 0x9a, 0xb5, 0x58, 0xfa, 0x0e, 0x9a, 0xe4, 
        0xbb, 0x49, 0x3e, 0xf7, 0x79, 0xf1, 0x40, 0x55
    };
    printf("Secret key: ");
    println_hex(secret, sizeof(secret));
 
    // Makes sense to check if secret key is valid.
    // It will be ok in most cases, only if secret > N it will be invalid
    res = secp256k1_ec_seckey_verify(ctx, secret);
    if(!res){ err("Secret key is invalid"); }
 
    /**************** Public key ******************/
 
    printf("=== Public key ===\r\n");
    // computing corresponding pubkey
    secp256k1_pubkey pubkey;
    res = secp256k1_ec_pubkey_create(ctx, &pubkey, secret);
    if(!res){ err("Pubkey computation failed"); }
 
    // serialize the pubkey in compressed format
    uint8_t pub[33];
    len = sizeof(pub);
    secp256k1_ec_pubkey_serialize(ctx, pub, &len, &pubkey, SECP256K1_EC_COMPRESSED);
    printf("Public key: ");
    println_hex(pub, len);
 
    // this is how you parse the pubkey
    res = secp256k1_ec_pubkey_parse(ctx, &pubkey, pub, 33);
    if(res){
        printf("Key is valid\r\n");
    }else{
        printf("Invalid key\r\n");
    }
 
    /**************** Signature stuff ******************/
 
    printf("=== Signature generation ===\r\n");
 
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
    if(!res){ err("Can't sign"); }
 
    // serialization
    uint8_t der[72];
    len = sizeof(der);
    res = secp256k1_ecdsa_signature_serialize_der(ctx, der, &len, &sig);
    if(!res){ err("Can't serialize the signature"); }
    printf("Signature: ");
    println_hex(der, len);
 
    // verification
    printf("=== Signature verification ===\r\n");
    res = secp256k1_ecdsa_verify(ctx, &sig, hash, &pubkey);
    if(res){
        printf("Signature is valid\r\n");
    }else{
        printf("Invalid signature\r\n");
    }
 
    secp256k1_context_destroy(ctx);
}
 
int main(){
    printf("Press any key to continue\r\n");
    pc.getc();
    printf("Ready to go!\r\n");
 
    printf("=== Running example for secp256k1 ===\r\n");
    secp_example();
 
 
    printf("\r\n=== Done ===\r\n");
 
}