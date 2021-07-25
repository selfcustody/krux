UEMBIT_MOD_DIR := $(USERMOD_DIR)

# Add all C files to SRC_USERMOD.
SRC_USERMOD += $(UEMBIT_MOD_DIR)/uembit.c
SRC_USERMOD += $(UEMBIT_MOD_DIR)/src/wordlist_bip39.c
SRC_USERMOD += $(UEMBIT_MOD_DIR)/src/wordlist_slip39.c

# We can add our module folder to include paths if needed
# disable for now, more optimizations required for faster word lookups
CFLAGS_USERMOD += -I$(UEMBIT_MOD_DIR)/include -DMODULE_UEMBIT_ENABLED=0