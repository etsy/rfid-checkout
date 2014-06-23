#/usr/bin/python
# Paths and settings for this checkout system

# Server side end points
# You will need to implement these on your server (see Readme)
CHECKINOUT_ENDPOINT = "https://YOURSERVER.COM/checkinout.php?staff_rfid_tag=%s&asset_rfid_tag=%s"
WHATIS_ENDPOINT     = "https://YOURSERVER.COM/whatis.php?rfid=%s"
ADDHUMAN_ENDPOINT   = "https://YOURSERVER.COM/associate.php?who=%s&tag=%s"

# Bounds Checks for card nubmers
# This helps to detect if we've gotten a read error and determine if the card
# was associated to a human or a device. Change these to fit your site ids.
HUMAN_TAG_RANGE_HIGH  = 8000000
HUMAN_TAG_RANGE_LOW   = 90000
DEVICE_TAG_RANGE_HIGH = 9990000
DEVICE_TAG_RANGE_LOW  = 8000000

# Optional: Hash human tag values before they are sent to the server
HASH_STRING = ""

# Path to the compiled C code for card reading (should be in same directory if you ran "make")
READER_APP = './hid_gpio_reader'

# Cause we all love logs
LOG_FILE = '/var/log/rfid.log'

# If using GPIO pins, the port should be '/dev/ttyAMA0'
# otherwise usb serial should be '/dev/ttyUSB0' or '/dev/ttyUSB1'
SERIAL_PORT = '/dev/ttyAMA0'

# We've used two types of serial 16x2 LCD screens which have different built in commands 

# NKC_LCD commands
CLS = "\xfe\x51"
LINE_TWO = "\xfe\x45\x40"
SCREEN_ON = "\x7e\x41"
SCREEN_OFF = "\x7e\x42"

# Sparkfun serial LCD commands
#CLS = "\xfe\x01"
#LINE_TWO = "" 
#SCREEN_ON = "\x7c\x9D"
#SCREEN_OFF = "\x7c\x80"

# Max number of seconds between two scans which will be used for a check in/out
SCAN_INTERVAL_TIMEOUT = 60
