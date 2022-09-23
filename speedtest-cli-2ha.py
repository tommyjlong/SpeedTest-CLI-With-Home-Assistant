# -*- coding: utf-8 -*-

import requests
import subprocess
import json
import logging
import logging.handlers #Needed for Syslog
import sys


##################################
# Instructions:
# AUTHKEY -  Create a permanent key in HA and use here it
# HASERVER - URL (http:port or https:port of your Home Assistant. Leave quotes as is.
# SPEEDTEST_SERVERID - the speedtest server ID of your desired server, 
#   or leave as is and speedtest will find one.
# SPEEDTEST_PATH - The full filename/path to the speedtest.bin file. LEAVE AS IS.
# 
# Use your existing speedtest integration from HA, but set 
#   manual: true 
# and use an automation to run this.
# Alternatively, this code will autocreate the same sensors
# but they will not live after a reboot.
# 
# This will update the following sensors:
#   sensor.speedtest_download
#   sensor.speedtest_ping
#   sensor.speedtest_upload
# 
##################################

# Configuration
HASERVER = "" #Home assistant server (no backslash at the end).
SPEEDTEST_SERVERID = ''
SPEEDTEST_PATH = sys.argv[1] + '/' + 'speedtest.bin'

# Your HA's long lived token for this:
AUTHKEY = "YOUR_HA_AUTH_TOKEN_HERE_IN_QUOTES"

# Setup Logger 
DEBUG   = 0 #set to 1 to get debug information.
CONSOLE = 0 #set to 1 to send output to stdout, 0 to local syslog

_LOGGER = logging.getLogger(__name__)
if CONSOLE:
    formatter = \
        logging.Formatter('%(message)s')
    handler1 = logging.StreamHandler(sys.stdout)
    handler1.setFormatter(formatter)
    handler1.setLevel(logging.NOTSET)
    _LOGGER.addHandler(handler1)
else:
    formatter2 = \
        logging.Formatter('%(levelname)s %(asctime)s %(filename)s - %(message)s')
    handler2 = logging.handlers.SysLogHandler(address = '/dev/log')
    handler2.setFormatter(formatter2)
    handler2.setLevel(logging.NOTSET)
    _LOGGER.addHandler(handler2)

if DEBUG:
  _LOGGER.setLevel(logging.DEBUG)
else:
  _LOGGER.setLevel(logging.NOTSET)

def HAPost(sensorname,state,unitmeasure,friendlyname,icon):
    """Method handling sending POST to home assistant api"""
    url = HASERVER + '/api/states/sensor.' + 'speedtest_' + sensorname
    headers = {'Authorization': 'Bearer ' + AUTHKEY,
               'content-type': 'application/json'}
    attributes = {"unit_of_measurement":unitmeasure,
                  "friendly_name":friendlyname,
                  "icon":icon}
    data = {'state':state, 'attributes':attributes}

    try:
        _LOGGER.debug('Try posting to HA')
        _LOGGER.debug('URL: %s',url)
        _LOGGER.debug('Headers: %s',headers)
        _LOGGER.debug('Attributes: %s',attributes)
        _LOGGER.debug('JSON Data: %s',data)

        response = requests.post(url, headers=headers, json=data, timeout=2)

        http_code = response.status_code
        response.raise_for_status() #For HTTPError
        _LOGGER.debug('Response:  %s',response)
        _LOGGER.debug('Response Status Code: %s',response.status_code) 
        _LOGGER.debug('Response Headers %s', response.headers)

        if str(response) == '<Response [200]>':
            #If Home Assistant uses the POST to update an existing 
            # speedtest entity, you get this return code.
            return 1
        if str(response) == '<Response [201]>':
            #If Home Assistant is creating this 
            #If Home Assistant uses the POST to create a new 
            # speedtest entity, you get this return code.
            return 1
    except(requests.exceptions.Timeout):
        #Something is too slow.
        _LOGGER.error('requests.exceptions.Timeout')
        return -1
    except(requests.exceptions.ConnectionError):
        #Either the URL is incorrect, or HA is off-line.
        _LOGGER.error('ConnectionError')
        _LOGGER.error('requests.exceptions.ConnectionError')
        return -1
    except requests.exceptions.HTTPError as err:
        _LOGGER.error('HTTPError')
        if http_code == 401:
            _LOGGER.debug("Auth Token may be bad")
        else:
            _LOGGER.debug("HTTPError return code : %s", http_code)
        return -1


# Run Speedtest
_LOGGER.debug('Running Speedtest')
if SPEEDTEST_SERVERID == '':
  speed_test_server_id=''
else:
  speed_test_server_id = '--server-id=' + SPEEDTEST_SERVERID

process = subprocess.Popen([SPEEDTEST_PATH,
                     '--format=json',
                     '--precision=4',
                     '--accept-license',
                     '--accept-gdpr',
                     speed_test_server_id],
                     stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE,
                     universal_newlines=True)
stdout, stderr = process.communicate()
_LOGGER.debug('Stdout: %s', stdout)
_LOGGER.debug('Stderr: %s', stderr)

# Speed Test Results - (from returned JSON string)
st_results = json.loads(stdout)
down_load_speed = round(st_results["download"]["bandwidth"]*8/1000000, 2)
up_load_speed = round(st_results["upload"]["bandwidth"]*8/1000000, 2)
ping_latency = st_results["ping"]["latency"]
isp = st_results["isp"]
server_name = st_results["server"]["name"]
url_result = st_results["result"]["url"]

_LOGGER.info('Downstream BW: %s',down_load_speed)
_LOGGER.info('Upstram BW: %s',up_load_speed)
_LOGGER.info('Ping Latency: %s', ping_latency)
_LOGGER.info('ISP: %s', isp)
_LOGGER.info('Server name: %s',server_name)
_LOGGER.info('URL results: %s',url_result)
_LOGGER.info('---------------------------------')

_LOGGER.debug('Posting to HA SpeedTest Sensors')
ret1 = HAPost("download",down_load_speed,"Mbit/s","Speedtest Download","mdi:speedometer")
ret2 = HAPost("upload",up_load_speed,"Mbit/s","Speedtest Upload","mdi:speedometer")
ret3 = HAPost("ping",ping_latency,"ms","Speedtest Ping","mdi:speedometer")
_LOGGER.debug('Return code from POST Method calls %s %s %s', ret1, ret2, ret3)

