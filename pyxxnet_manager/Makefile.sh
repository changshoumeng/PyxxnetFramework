###################################################
#Teach Wisedom to My Machine
#       Please Call me Devil
#

VERSION = 1
ARNAME 	= libnetlog.a
SONAME 	= libnetlog.so

ROOT_DIR     := $(shell pwd)
SRC_DIR      := $(ROOT_DIR)/src
INC_DIR      := $(ROOT_DIR)/include
INC_DIR      += $(ROOT_DIR)/common
INSTALL_PATH := $(ROOT_DIR)/lib/
LIB_DIR      := $(ROOT_DIR)/lib/

CC 	= g++
AR	= ar -cru
CFLAGS 	= -Wall -D_REENTRANT -D_GNU_SOURCE -g -fPIC  -O3 -fpermissive -fno-strict-aliasing -DTRACE_LOG -D__SERVER
#CFLAGS 	= -Wall -D_REENTRANT -D_GNU_SOURCE -g -fPIC -m32 -O3 -fpermissive -fno-strict-aliasing -DTRACE_LOG -D__SERVER
SOFLAGS = -shared
#SOFLAGS = -shared  -m32 -melf_i386
LFLAGS 	= -lstdc++ -lpthread

LD_LIBS    :=

CFLAGS	+= -I$(SRC_DIR) $(addprefix -I,$(INC_DIR))
LFLAGS 	+= -L$(LIB_DIR) $(addprefix -l,$(LD_LIBS))

#------------------------------------------------

#OBJS =  $(SRC_DIR)/DebugTraceThread.o $(SRC_DIR)/System.o $(SRC_DIR)/BaseConfig.o  $(SRC_DIR)/IniEx.o
#OBJS = $(SRC_DIR)/BaseConfig.o  $(SRC_DIR)/DebugTraceThread.o $(SRC_DIR)/System.o  $(SRC_DIR)/IniEx.o

SOURCE =  $(wildcard  $(SRC_DIR)/*.cpp)
OBJS = $(patsubst %.cpp,%.o,$(SOURCE))


install : all
	cp -f $(SONAME).$(VERSION) ../../update/$(SONAME)
	cp -f $(SONAME).$(VERSION) $(INSTALL_PATH)$(SONAME)
	cp -f $(ARNAME).$(VERSION) $(INSTALL_PATH)$(ARNAME)

all : $(SONAME).$(VERSION) $(ARNAME).$(VERSION)

$(SONAME).$(VERSION) : $(OBJS)
	$(CC) $(SOFLAGS) $(LFLAGS) $^ -o $@
	ln -s $@ $(SONAME)
#	$(warning  $(OBJS))
$(ARNAME).$(VERSION) : $(OBJS)
	$(AR) $@ $^
	ln -s $@ $(ARNAME)

clean :
	@echo "clean--------------"
	@echo $(SOURCE)
	rm -rf $(OBJS)


	rm -rf $(SONAME)
	rm -rf $(SONAME).$(VERSION)

	rm -rf $(ARNAME)
	rm -rf $(ARNAME).$(VERSION)

distclean :
	rm -rf $(OBJS)

	rm -rf $(SONAME)
	rm -rf $(SONAME).$(VERSION)

	rm -rf $(ARNAME)
	rm -rf $(ARNAME).$(VERSION)

	rm -rf $(INSTALL_PATH)$(SONAME)
	rm -rf $(INSTALL_PATH)$(ARNAME)



#------------------------------------------------

%.o : %.c
	$(CC) $(CFLAGS) -c $^ -o $@

%.o : %.cpp
	$(CC) $(CFLAGS) -c $^ -o $@
