#
# Makefile:
#   App for reading HID RFID cards from the GPIO pins
#
#   _Requires_
#	wiringPi - Wiring Compatable library for the Raspberry Pi
#	https://projects.drogon.net/wiring-pi
#

DEBUG	= -O3
CC	= gcc
INCLUDE	= -I/usr/local/include
CFLAGS	= $(DEBUG) -Wall $(INCLUDE) -Winline -pipe

LDFLAGS	= -L/usr/local/lib
LDLIBS    = -lwiringPi -lwiringPiDev -lpthread -lm

SRC	=	hid_reader.c

OBJ	=	$(SRC:.c=.o)

BINS	=	$(SRC:.c=)

hid_gpio_reader:	hid_reader.o
	@echo [link]
	@$(CC) -o $@ hid_reader.o $(LDFLAGS) $(LDLIBS)

.c.o:
	@echo [CC] $<
	@$(CC) -c $(CFLAGS) $< -o $@

clean:
	@echo "[Clean]"
	@rm -f $(OBJ) *~ core tags $(BINS)

depend:
	makedepend -Y $(SRC)

