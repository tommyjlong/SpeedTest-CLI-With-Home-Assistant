# -*- coding: utf-8 -*-

import requests
import subprocess
import json
import logging
import logging.handlers
import sys
import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

##################################
# Configuration from environment variables
HASERVER = os.getenv('HA_SERVER', 'http://localhost:8123')
AUTHKEY = os.getenv('HA_AUTH_KEY', '')
SPEEDTEST_SERVERID = os.getenv('SPEEDTEST_SERVER_ID', '')
INCLUDE_LTS = int(os.getenv('INCLUDE_LTS', '1'))

# Sensor names configuration
SENSOR_DOWNLOAD = os.getenv('SENSOR_DOWNLOAD', 'download')
SENSOR_UPLOAD = os.getenv('SENSOR_UPLOAD', 'upload')
SENSOR_PING = os.getenv('SENSOR_PING', 'ping')

# Friendly names configuration
SENSOR_DOWNLOAD_NAME = os.getenv('SENSOR_DOWNLOAD_NAME', f'SpeedTest {SENSOR_DOWNLOAD.capitalize()}')
SENSOR_UPLOAD_NAME = os.getenv('SENSOR_UPLOAD_NAME', f'SpeedTest {SENSOR_UPLOAD.capitalize()}')
SENSOR_PING_NAME = os.getenv('SENSOR_PING_NAME', f'SpeedTest {SENSOR_PING.capitalize()}')

# Speedtest binary path - in Docker this will be just 'speedtest'
SPEEDTEST_PATH = os.getenv('SPEEDTEST_PATH', '/usr/bin/speedtest')

# Debug configuration
DEBUG = int(os.getenv('DEBUG', '0'))
CONSOLE = int(os.getenv('CONSOLE', '1'))

# Setup Logger 
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

def HAPost(sensorname, state, attributes):
    """Method handling sending POST to home assistant api"""
    url = HASERVER + '/api/states/sensor.' + 'speedtest_' + sensorname
    headers = {'Authorization': 'Bearer ' + AUTHKEY,
               'content-type': 'application/json'}
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
down_load_bytes_received = st_results["download"]["bytes"]
up_load_speed = round(st_results["upload"]["bandwidth"]*8/1000000, 2)
up_load_bytes_sent = st_results["upload"]["bytes"]
ping_latency = st_results["ping"]["latency"]
isp = st_results["isp"]
server_name = st_results["server"]["name"]
server_country = st_results["server"]["country"]
server_id = st_results["server"]["id"]
url_result = st_results["result"]["url"]

_LOGGER.info('Downstream BW: %s',down_load_speed)
_LOGGER.info('Upstram BW: %s',up_load_speed)
_LOGGER.info('Ping Latency: %s', ping_latency)
_LOGGER.info('ISP: %s', isp)
_LOGGER.info('Server name: %s',server_name)
_LOGGER.info('Server country: %s',server_country)
_LOGGER.info('Server id: %s',server_id)
_LOGGER.info('URL results: %s',url_result)
_LOGGER.info('---------------------------------')

_LOGGER.debug('Posting to HA SpeedTest Sensors')

#Setup Download Attributes, then POST to HA
download_attribs = {
                 "attribution": "Data retrieved from Speedtest.net by Ookla",
                 "unit_of_measurement": "Mbit/s",
                 "device_class": "data_rate",
                 "friendly_name": SENSOR_DOWNLOAD_NAME,
                 "server_name": server_name,
                 "server_country": server_country,
                 "server_id": server_id,
                 "bytes_received": down_load_bytes_received}
if INCLUDE_LTS:
    download_attribs["state_class"] = "measurement"
ret1 = HAPost(SENSOR_DOWNLOAD, down_load_speed, download_attribs)

#Setup Upload Attributes, then POST to HA
upload_attribs = {
               "attribution": "Data retrieved from Speedtest.net by Ookla",
               "unit_of_measurement": "Mbit/s",
               "device_class": "data_rate",
               "friendly_name": SENSOR_UPLOAD_NAME,
               "server_name": server_name,
               "server_country": server_country,
               "server_id": server_id,
               "bytes_sent": up_load_bytes_sent }
if INCLUDE_LTS:
    upload_attribs["state_class"] = "measurement"
ret2 = HAPost(SENSOR_UPLOAD, up_load_speed, upload_attribs)

#Setup Ping Attributes
ping_attribs = {
             "attribution": "Data retrieved from Speedtest.net by Ookla",
             "unit_of_measurement": "ms",
             "device_class": "duration",
             "friendly_name": SENSOR_PING_NAME,
             "server_name": server_name,
             "server_country": server_country,
             "server_id": server_id}
if INCLUDE_LTS:
    ping_attribs["state_class"] = "measurement"
ret3 = HAPost(SENSOR_PING, ping_latency, ping_attribs)
_LOGGER.debug('Return code from POST Method calls %s %s %s', ret1, ret2, ret3)

