BITCOIN_MOD_DIR := $(USERMOD_DIR)

# Add all C files to SRC_USERMOD.
SRC_USERMOD += $(BITCOIN_MOD_DIR)/crypto/ripemd160.c
SRC_USERMOD += $(BITCOIN_MOD_DIR)/crypto/sha2.c
SRC_USERMOD += $(BITCOIN_MOD_DIR)/crypto/hmac.c
SRC_USERMOD += $(BITCOIN_MOD_DIR)/crypto/pbkdf2.c
SRC_USERMOD += $(BITCOIN_MOD_DIR)/crypto/memzero.c
SRC_USERMOD += $(BITCOIN_MOD_DIR)/hashlib.c
SRC_USERMOD += $(BITCOIN_MOD_DIR)/uhmac.c

# We can add our module folder to include paths if needed
CFLAGS_USERMOD += -I$(BITCOIN_MOD_DIR)/crypto