#!/usr/bin/env python3

import os
import sys
import traceback
import time
import pif
import godaddypy
import ipaddress
import json

import argparse
import logging

import urllib
import string

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(name)s - %(message)s', level=logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument('-v', '--verbose', action="store_true", default=False, help="Verbose logging")
args = parser.parse_args()
if args.verbose:
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logging.debug('Debug Logging Enabled')

# Disable Unverified HTTPS request warning from pif
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# For developemnt test purpose.
# os.environ.setdefault('UPDATER_CONFIG_FILE', "./config.json")

# Read default config file which env will override
json_config = None
try:
    config_file = os.environ.get('UPDATER_CONFIG_FILE', None) # no default
    if config_file:
      with open(config_file) as config_file_data:
        json_config = json.load(config_file_data)
except:
    logging.error('No default config found, continuing.', exc_info=True)

def get_config_value(key, default_value=None):
    v = default_value
    # Get from json config as default
    if json_config:
        v = json_config.get(key, v)

    # if no default then it is required and return env var
    if not v:
        return os.environ[key]

    # otherwise try to override with env var
    return os.environ.get(key, v)

# Required ENV
godaddy_api_key = get_config_value('GODADDY_API_KEY')
godaddy_api_secret = get_config_value('GODADDY_API_SECRET')
godaddy_domains = get_config_value('GODADDY_DOMAINS').split(',')

# Optional ENV
godaddy_a_names = get_config_value('GODADDY_A_NAMES', '@').split(',')
get_ip_wait_sec = get_config_value('GET_IP_WAIT_SEC', 10) # default 10 sec
update_interval_sec = get_config_value('UPDATE_INTERVAL_SEC', 900) # default 15 min
ipv6_get_api = get_config_value('IPV6_GET_API', 'https://api6.ipify.org') # default https://api6.ipify.org
record_type = get_config_value('RECORD_TYPE', 'A') # default 'A'

# Create the godaddypy client using the provided keys
g_client = godaddypy.Client(godaddypy.Account(api_key=godaddy_api_key, api_secret=godaddy_api_secret))


def url_postget(url):
    response = urllib.request.urlopen(url)
    str = response.read()
    return str


def update_godaddy_records(ip):

    successful = True
    for domain in godaddy_domains:
        for a_name in godaddy_a_names:

            logging.debug('Getting A records with {} for {}'.format(a_name, domain))
            records = g_client.get_records(domain, name=a_name, record_type=record_type)
            if not records:
                logging.warning('No record {} for {} found'.format(a_name, domain))
                successful = False
                # TODO add the record if configured to do so
                continue

            for record in records:
                if ip == record['data']:
                    logging.debug('Record {} for {} is still {}, no update required'.format(a_name, domain, ip))
                    continue

                result = g_client.update_record_ip(ip, domain, name=a_name, record_type=record_type)
                if result is not True:
                    logging.error('Failed to update {} for {} to {}'.format(a_name, domain, ip))
                    successful = False
                    continue

                logging.info('Updated {} for {} to {}'.format(a_name, domain, ip))

    return successful

def loop_forever():

    public_ip_cache = False

    # Loop forever
    while True:

        # Go get our current public IP address
        new_ip = False
        while not new_ip:
            try:
                if record_type == 'A':
                    pub_ip = pif.get_public_ip()
                elif record_type == 'AAAA':
                    pub_ip = bytes.decode(url_postget(ip_get_url))
                else:
                    logging.error("record type must be 'A' or 'AAAA' .")
                    break
                
                # Check for valid ip
                try:
                    ipaddress.ip_address(pub_ip)
                    new_ip = pub_ip
                except:
                    logging.error('Got an invalid ip address')
                    logging.debug('ip address {}'.format(pub_ip), exc_info=True)
            except:
                logging.exception('Got exception getting public IP')

            # Done if we got one
            if new_ip:
                break

            time.sleep(get_ip_wait_sec)

        # If we got the same IP address, we will try again later
        if public_ip_cache != new_ip:
            # Update the records at godaddy
            try:
                worked = update_godaddy_records(new_ip)
                if worked:
                    #cache so we dont try again if everything went good
                    logging.info('new-ip: {}, old-ip: {}'.format(new_ip, public_ip_cache))
                    public_ip_cache = new_ip
            except:
                logging.exception('Got exception updating godaddy records')

        time.sleep(update_interval_sec)

loop_forever()

