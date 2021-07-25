QR_MOD_DIR := $(USERMOD_DIR)

# Add all C files to SRC_USERMOD.
SRC_USERMOD += $(QR_MOD_DIR)/qrcodegen/qrcodegen.c
SRC_USERMOD += $(QR_MOD_DIR)/qrcode.c

# We can add our module folder to include paths if needed
CFLAGS_USERMOD += -I$(QR_MOD_DIR)/qrcodegen