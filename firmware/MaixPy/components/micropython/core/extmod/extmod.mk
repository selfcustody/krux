# This makefile fragment provides rules to build 3rd-party components for extmod modules

# this sets the config file for FatFs
CFLAGS_MOD += -DFFCONF_H=\"lib/oofatfs/ffconf.h\"

################################################################################
# btree

ifeq ($(MICROPY_PY_BTREE),1)
BTREE_DIR = lib/berkeley-db-1.xx
BTREE_DEFS = -D__DBINTERFACE_PRIVATE=1 -Dmpool_error=printf -Dabort=abort_ "-Dvirt_fd_t=void*" $(BTREE_DEFS_EXTRA)
INC += -I$(TOP)/$(BTREE_DIR)/PORT/include
SRC_MOD += extmod/modbtree.c
SRC_MOD += $(addprefix $(BTREE_DIR)/,\
	btree/bt_close.c \
	btree/bt_conv.c \
	btree/bt_debug.c \
	btree/bt_delete.c \
	btree/bt_get.c \
	btree/bt_open.c \
	btree/bt_overflow.c \
	btree/bt_page.c \
	btree/bt_put.c \
	btree/bt_search.c \
	btree/bt_seq.c \
	btree/bt_split.c \
	btree/bt_utils.c \
	mpool/mpool.c \
	)
CFLAGS_MOD += -DMICROPY_PY_BTREE=1
# we need to suppress certain warnings to get berkeley-db to compile cleanly
# and we have separate BTREE_DEFS so the definitions don't interfere with other source code
$(BUILD)/$(BTREE_DIR)/%.o: CFLAGS += -Wno-old-style-definition -Wno-sign-compare -Wno-unused-parameter $(BTREE_DEFS)
$(BUILD)/extmod/modbtree.o: CFLAGS += $(BTREE_DEFS)
endif

