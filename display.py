#/usr/bin/python
import serial
import time
import logging
import sys, tty, termios
import constants


running_pid = '/var/run/rfid_application_lastrun.pid'
logger = logging.getLogger('rfid_application')

class Display:
    def __init__(self):
        self.ser = None
        self.connect_lcd()
        self.display_on()
        self.show("Lab is Open.")

    def __del__(self):
        self._display_off()
  
    def display_on(self):
        self.touch(running_pid)
        self.ser.write(constants.SCREEN_ON)

    def _display_off(self):
        self.ser.write(constants.SCREEN_OFF)

    def connect_lcd(self):
        ### USB LCD Screen will either be on ttyUSB0 or ttyUSB1
        ### If using GPIO pins (BCM 14), port will be '/dev/ttyAMA0'
        try:
            self.ser = serial.Serial(
                port=constants.SERIAL_PORT,
                baudrate=9600,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS
            )
            self.ser.open()
        except serial.SerialException as e:
            print "Error connecting LCD display: ", e
               
    def tag_not_found(self, tag, is_human):
        self.print_unknown_tag(tag)
        if self.ser.isOpen():
            if is_human:
                self.show("_Unknown Badge_ Type User Name:")
                logger.info("Display_Unknown=human")
                new_name = self._type_new_tag_name()
                self.ser.write(constants.CLS)
                if len(new_name) > 2:
                    self.show("Thank you.      Sending...")
                    return new_name
                else:
                    self.ser.write("Bad Input.      Tap Tag Again")                               
            else:
                self.show("Device must be  added to DB")
                logger.info("Display_Unknown=device")
                time.sleep(5)
                self.show("New Device Tag. " + str(tag))
                

    def print_checkout_info(self, resp):
        print resp.get("response")
        logger.info("Display_Checking_Data=" + str(resp.get("response")))
        if resp.get("response") == None:
            self.show("  _Web Error_   Try Again")
            return

        ### Shorter reply on 16 char display
        if "checked in" in resp.get("response"):
            self.show("  _Checked In_  Device Returned")
        elif "checked out" in resp.get("response"):
            self.show(" _Checked Out_    It's Yours!")
        else:
            self.show(" Status Unknown ")


    def print_whatis_info(self, resp):
        print resp.get("name")
        logger.info("Display_WhatIs=" + str(resp.get("name"))) 
        self.show(str(resp.get('name')))

    def print_unknown_tag(self, tag):
        sorry_text = "Tag not associated. Sorry sucka, I don't know you. "
        print sorry_text + "\nTagID = %s" % (tag)

    def print_api_error(self):
        self.show("API Error       Check Logs")
        logger.error("Display_API_ERROR=true")

    def print_bad_read(self):
        time.sleep(0.25)        #Fix for LCD screen locking up
        self.show("Bad Tag Read    Please Tap Again")
        logger.error("Display_Bad_Read=True")

    def print_associate_human_error(self, msg):
        print "ERROR - Associate Human: " + msg
        self.show("Error: " + str(msg)[0:24])

    def _type_new_tag_name(self):
        user_string = ""
        last_char = ""
        while True:
            last_char = self._read_char_from_input()
            
            if last_char == "\r":
                break
            if len(user_string) == 0:
                self.ser.write(constants.CLS)
            if len(user_string) > 256:
                break
            if last_char == '\x08' or last_char == '\x7f':
                user_string = user_string[:-1]
                self.show(user_string)
                continue

            user_string = user_string + last_char
            self.ser.write(last_char)
        return user_string

    def _read_char_from_input(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    def touch(self, fname):
        open(fname, 'w').close()

    def show(self, text):
        if (len(text) > 0):
            self.ser.write(constants.CLS)
            self.ser.write(str(text)[0:16])
            self.ser.write(constants.LINE_TWO)
            self.ser.write(str(text)[16:32])
