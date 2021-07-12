#include "secp256k1.h"
#include "secp256k1_preallocated.h"

// forward declaration
void print_err(const char * message, void * data = NULL);

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  Serial.println("Press any key to continue.");
  while(!Serial.available()){
    delay(100);
  }
  Serial.println("\nOk, let's rock!");
  secp_example();
  Serial.println("=== Done ===");
}

void loop() {
  delay(1000);
}

void secp_example(){
  // secp256k1 context
  secp256k1_context *ctx = NULL;

  int res;    // to store results of function calls
  size_t len; // to store serialization lengths

  Serial.print("=== secp256k1 context ===\r\n");

  // first we need to create the context
  // this is the size of memory to be allocated
  size_t context_size = secp256k1_context_preallocated_size(SECP256K1_CONTEXT_VERIFY | SECP256K1_CONTEXT_SIGN);
  Serial.print("Context size: ");
  Serial.print(context_size);
  Serial.println(" bytes");

  // creating the context
  // you can also preallocate it yourself and
  // pass to secp256k1_context_preallocated_create
  ctx = secp256k1_context_create(SECP256K1_CONTEXT_VERIFY | SECP256K1_CONTEXT_SIGN);
  Serial.print("Context created\r\n");

  // if you have true random number generator
  // it makes sense to randomize context from time to time
  // to avoid sidechannel attacks:
  // secp256k1_context_randomize(ctx, byte[32] random_buf);

  Serial.print("=== Secret key ===\r\n");
  // some random secret key
  uint8_t secret[] = {
    0xbd, 0xb5, 0x1a, 0x16, 0xeb, 0x64, 0x60, 0xec, 
    0x16, 0xf8, 0x4d, 0x7b, 0x6f, 0x19, 0xe2, 0x0d, 
    0x9b, 0x9a, 0xb5, 0x58, 0xfa, 0x0e, 0x9a, 0xe4, 
    0xbb, 0x49, 0x3e, 0xf7, 0x79, 0xf1, 0x40, 0x55
  };
  Serial.print("Secret key: ");
  println_hex(secret, sizeof(secret));

  // Makes sense to check if secret key is valid.
  // It will be ok in most cases, only if secret > N it will be invalid
  res = secp256k1_ec_seckey_verify(ctx, secret);
  if(!res){ print_err("Secret key is invalid"); }

  /**************** Public key ******************/

  Serial.print("=== Public key ===\r\n");
  // computing corresponding pubkey
  secp256k1_pubkey pubkey;
  res = secp256k1_ec_pubkey_create(ctx, &pubkey, secret);
  if(!res){ print_err("Pubkey computation failed"); }

  // serialize the pubkey in compressed format
  uint8_t pub[33];
  len = sizeof(pub);
  secp256k1_ec_pubkey_serialize(ctx, pub, &len, &pubkey, SECP256K1_EC_COMPRESSED);
  Serial.print("Public key: ");
  println_hex(pub, len);

  // this is how you parse the pubkey
  res = secp256k1_ec_pubkey_parse(ctx, &pubkey, pub, 33);
  if(res){
    Serial.print("Key is valid\r\n");
  }else{
    Serial.print("Invalid key\r\n");
  }

  /**************** Signature stuff ******************/

  Serial.print("=== Signature generation ===\r\n");

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
  if(!res){ print_err("Can't sign"); }

  // serialization
  uint8_t der[72];
  len = sizeof(der);
  res = secp256k1_ecdsa_signature_serialize_der(ctx, der, &len, &sig);
  if(!res){ print_err("Can't serialize the signature"); }
  Serial.print("Signature: ");
  println_hex(der, len);

  // signature verification
  Serial.print("=== Signature verification ===\r\n");
  res = secp256k1_ecdsa_verify(ctx, &sig, hash, &pubkey);
  if(res){
    Serial.print("Signature is valid\r\n");
  }else{
    Serial.print("Invalid signature\r\n");
  }

  // clean up when context is not needed any more
  secp256k1_context_destroy(ctx);
}

void print_hex(const uint8_t * data, size_t data_len){
  char arr[3];
  for(int i=0; i<data_len; i++){
    if(data[i]<0x10){ Serial.print("0"); }
    Serial.print(data[i], HEX);
  }
}
// just adds a new line to the end of the data
void println_hex(const uint8_t * data, size_t data_len){
  print_hex(data, data_len);
  Serial.println();
}

// prints error and hangs forever
void print_err(const char * message, void * data){
  Serial.print("ERROR: ");
  Serial.println(message);
  while(1){
    delay(1000);
  }
}
