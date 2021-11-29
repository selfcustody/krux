SECP256K1_MODULE_DIR := $(USERMOD_DIR)

# Add all C files to SRC_USERMOD.
SRC_USERMOD += $(SECP256K1_MODULE_DIR)/secp256k1/src/secp256k1.c
SRC_USERMOD += $(SECP256K1_MODULE_DIR)/mpy/config/ext_callbacks.c
SRC_USERMOD += $(SECP256K1_MODULE_DIR)/mpy/libsecp256k1.c

# We can add our module folder to include paths if needed
CFLAGS_USERMOD += -I$(SECP256K1_MODULE_DIR)/secp256k1 -I$(SECP256K1_MODULE_DIR)/secp256k1/src -I$(SECP256K1_MODULE_DIR)/mpy/config -DHAVE_CONFIG_H -Wno-unused-function