#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
----------------------------------------------------------------------
Created Date: 2nd November 2022
Author: Ed Moore
License: Cisco Sample Code License, Version 1.1
----------------------------------------------------------------------

Copyright (c) 2022 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the 'License'). You may obtain a copy of the
License at
               'https://developer.cisco.com/docs/licenses'
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an 'AS IS'
BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.

----------------------------------------------------------------------
"""

import requests
import pandas as pd
from requests.auth import HTTPBasicAuth
from dotenv import dotenv_values

# Disable SSL warnings. Not needed in production
# environments with valid certificates
import urllib3
urllib3.disable_warnings()

# Import env variables from dotenv

config = dotenv_values(".env")

BASE_URL = config.get("BASE_URL")
USERNAME = config.get("USERNAME")
PASSWORD = config.get("PASSWORD")

# STATIC URLs
AUTH_URL = '/dna/system/api/v1/auth/token'
DEVICES_URL = '/dna/intent/api/v1/network-device'
IMAGE_URL = '/dna/intent/api/v1/image/importation?isTaggedGolden=TRUE'


def get_auth_token():
    """Authenticate and receivev x-auth token
       Returns: token: string
    """
    response = requests.post(BASE_URL + AUTH_URL,
                             auth=HTTPBasicAuth(USERNAME, PASSWORD),
                             verify=False,
                             timeout=10)
    token = response.json()['Token']
    return token

def get_devices_list(headers, query_string_params):
    """Get list of devices
       Returns: response : json
    """
    response = requests.get(BASE_URL + DEVICES_URL,
                            headers = headers,
                            params = query_string_params,
                            verify=False,
                            timeout=10)
    return response.json()['response']

def get_image_list(headers):
    """Get list of images
       Returns: response : json
    """
    response = requests.get(BASE_URL + IMAGE_URL,
                            headers = headers,
                            verify=False,
                            timeout=10)
    return response.json()['response']

def create_image_device_mapping(images):
    """Create a dict mapping device_family to golden image version
       Returns: image_mapping : dict
    """
    image_mapping = {}
    for image in images:
        for device_family in image['applicableDevicesForImage']:
            image_mapping[device_family['productName']] = image['displayVersion']
    return image_mapping

def create_device_table(devices):
    """Create subset of device info from devices response and output list of dicts
       Returns - device_table : list
    """
    device_table = []
    for device in devices:
        device_table.append({'Hostname': device['hostname'],
                            'Platform ID': device['platformId'],
                            'Device Family': device['series'],
                            'Software Type': device['softwareType'],
                            'Software Version': device['softwareVersion'],
                            'Software Compliant': ''})
    return device_table

def check_image_compliant(devices,images):
    """Checks to see whether device matches Golden Image
    Returns - devices : list of dicts"""
    for device in devices:
        version = images.get(device['Device Family'])
        if version is None:
            device['Software Compliant'] = 'Golden Image Not specified'
        elif version == device['Software Version']:
            device['Software Compliant'] = True
        else:
            device['Software Compliant'] = False
    return devices

def create_device_report(devices):
    """Generate dataframe from devices list
       Returns - devices_df : dataframe """
    devices_df = pd.DataFrame.from_dict(devices)
    return devices_df

def create_pie_chart(devices):
    plot = devices["Software Compliant"].value_counts(normalize=True).plot.pie(autopct='%.1f %%', ylabel='', labeldistance=None, legend=True)
    plot.figure.savefig('compliance.png')

def main():
    """Creates a mini-report of the Software Compliance Info"""

    # obtain the Cisco DNA Center Auth Token
    token = get_auth_token()
    headers = {'X-Auth-Token': token, 'Content-Type': 'application/json'}
    # Create mapping of image to device family
    print('\nPrinting Image Info ...')
    response = get_image_list(headers)
    image_family = create_image_device_mapping(response)
    # Create table of device info
    response = get_devices_list(headers, {})
    devices = create_device_table(response)
    report_table = check_image_compliant(devices,image_family)
    device_df = create_device_report(report_table)
    print(device_df)
    create_pie_chart(device_df)



if __name__ == "__main__":
    main()
