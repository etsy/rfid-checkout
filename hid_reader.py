#!/usr/bin/env python
# Python reads GPIO on RasPi too slow for good tag data
# We will now take the read from a C app
#   Hardware Lines - green/data0 is BCM pin 17 
#   Hardware Lines - white/data1 is BCM pin 18

import time
import subprocess
import select
import hashlib
import logging
from tag_handler import TagHandler
import constants

logger = logging.getLogger('rfid_application')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(constants.LOG_FILE)
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

tag_handler = TagHandler()

f = None
p = None
bits = ''

print "Ready. Please Present Card..."
try:
    while 1:
        f = subprocess.Popen([constants.READER_APP],\
                stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        p = select.poll()
        p.register(f.stdout)
        logger.debug('GPIO Process Started')

        while 1:
            if p.poll(1):
                line = f.stdout.readline()
                if (len(line) > 1):
                    print line
                    line = line.rstrip()
                    # Next line depends on what we have in our C program for the GPIO data
                    # You will likely need to update this in the future if that app changes
                    bits = line[12:]

                    # Convert the string of bits to an int (removes leading zeros)
                    card_int = int(str(bits),2)

                    logger.debug('New Tag: ' + str(bits))
                    print "--NEW TAG--"
                    print time.asctime(time.localtime(time.time())) 
                    print "Binary:",bits

                    if (card_int > constants.HUMAN_TAG_RANGE_LOW) and (card_int < constants.HUMAN_TAG_RANGE_HIGH):
                        human_tag = hashlib.sha256(constants.HASH_STRING+str(card_int)).hexdigest()
                        print "Human Tag:", human_tag
                        logger.info('HumanTag=' + human_tag)
                        tag_handler.dispatch(human_tag)
                    elif (card_int > constants.DEVICE_TAG_RANGE_LOW) and (card_int < constants.DEVICE_TAG_RANGE_HIGH):
                        print "Device Tag:", str(card_int)
                        logger.info('DeviceTag=' + str(card_int))
                        tag_handler.dispatch(card_int)
                    else:
                        print "BAD READ"
                        logger.error('BadRead=' + str(card_int))
                        tag_handler.bad_read(card_int)
                        break

                    bits = '0'

            time.sleep(0.1)

        p.unregister(f.stdout)
        f.terminate()
        logger.debug('GPIO Process Terminated')
        time.sleep(2)

except KeyboardInterrupt:
    print "Clean Exit By user"
    logger.debug('Clean Exit By user')
    p.unregister(f.stdout)
    f.terminate()

