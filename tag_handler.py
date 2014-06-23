#/usr/bin/python
from os import system
import os
import time
import json
import urllib,urllib2
import pprint
import thread
from display import Display
import constants


class TagHandler:
    # scan_interval_time out can be used to set the maximum time allowed between 
    # two taps to be considered a check in/out request
    def __init__(self, verbose = False, scan_interval_timeout = constants.SCAN_INTERVAL_TIMEOUT):
        self.scan_interval_timeout = scan_interval_timeout
        self.last_tag = None
        self.last_tag_type = None
        self.current_tag_type = None
        self.last_read_tstamp = -1
        self.display = Display()

    # This may need to be changed depending which tags you associate to staff versus devices
    def is_human_tag(self, tag):
        if len(str(tag)) > 10:
            return True
        return False 

    def query_api(self, url, postdata = None):
        headers = {}
        if postdata:
            postdata = urllib.urlencode(postdata)
        req = urllib2.Request(url, postdata, headers)

        response = None
        code = None
        f = None
       
        try:
            f = urllib2.urlopen(req)
            code = f.getcode()
            resp = f.read()
            response = json.loads(resp)
        except urllib2.URLError as e:
            if hasattr(e, 'reason'):
                response = e.reason
                code = -1
            elif hasattr(e, 'code'):
                response = e.msg
                code = e.code
        except ValueError:  
            response = 'Decoding JSON has failed'
            code = 500
            print resp
        finally:
            if f:
                f.close()
        return response, code

    def _process_checkinout(self, tag_a, tag_b):
        #A Human must be sent to the API call for checkout
        if(self.last_tag_type == "human"):
            data = {"tag_human" : tag_a, "tag_thing" : tag_b}
        elif(self.current_tag_type == "human"):
            data =  {"tag_human" : tag_b, "tag_thing" : tag_a}
        else:
            print "Who are you?"
            return

        url = constants.CHECKINOUT_ENDPOINT % (data['tag_human'], data['tag_thing'])
        resp, code = self.query_api(url)
        if code != 200:
            self._handle_api_exception(resp, code, data)
        else:
            self.display.print_checkout_info(resp)
            ## THis should clear the last tag scanned
            self.last_read_tstamp = (time.time() - self.scan_interval_timeout) 

    def _process_read(self, tag):
        url = constants.WHATIS_ENDPOINT % tag
        resp, code = self.query_api(url)
        if code == 200:
            if not resp.get("error"):
                self.current_tag_type = resp.get("type")
                self.display.print_whatis_info(resp)
            else:
                # We're only going to allow human tags to be updated from client
                user_input = self.display.tag_not_found(tag, self.is_human_tag(tag))
                if user_input is not None:
                    self.associate_human_to_tag(user_input, tag)
            return
        self._handle_api_exception(resp, code, {"tag" : tag})

    def dispatch(self, tag):
        now = time.time()
        self.display.display_on()

        #Find out if this is a human, device, book or other tag
        self._process_read(tag)

        #If we have both a human and thing, lets check in/out
        if (now - self.last_read_tstamp) < self.scan_interval_timeout and self.current_tag_type != self.last_tag_type:
            self._process_checkinout(self.last_tag, tag)
        else:
            #Set last tag data so we have this for next read
            self.last_read_tstamp = now
            self.last_tag = tag
            self.last_tag_type = self.current_tag_type 

    def associate_human_to_tag(self, username, tag):
        url = constants.ADDHUMAN_ENDPOINT % (username, tag)
        resp, code = self.query_api(url)

        print resp

        if code == 200:
            if not resp.get("error"):
                # Resend tag since it should now be in the system
                # could this loop? YOLO.
                self.dispatch(tag)
            else:
                self.display.print_associate_human_error(resp.get("error"))
            return

    def bad_read(self, tag):
        self.display.display_on()
        self.display.print_bad_read()

    def _handle_api_exception(self, resp, code, data):
        print "[%s] - %s (data : %s)" % (code, resp,  pprint.pformat(data))
        self.display.print_api_error()


