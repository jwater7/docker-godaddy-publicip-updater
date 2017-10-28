#!/usr/bin/env python3

import os
import sys
import traceback
import time
import pif
import godaddypy
import ipaddress

import argparse
import logging

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

# Required ENV
godaddy_api_key = os.environ['GODADDY_API_KEY']
godaddy_api_secret = os.environ['GODADDY_API_SECRET']
godaddy_domains = os.environ['GODADDY_DOMAINS'].split(',')

# Optional ENV
godaddy_a_names = os.environ.get('GODADDY_A_NAMES', '@').split(',')
get_ip_wait_sec = os.environ.get('GET_IP_WAIT_SEC', 10) # default 10 sec
update_interval_sec = os.environ.get('UPDATE_INTERVAL_SEC', 900) # default 15 min

# Create the godaddypy client using the provided keys
g_client = godaddypy.Client(godaddypy.Account(api_key=godaddy_api_key, api_secret=godaddy_api_secret))

def update_godaddy_records(ip):

    successful = True
    for domain in godaddy_domains:
        for a_name in godaddy_a_names:

            logging.debug('Getting A records with {} for {}'.format(a_name, domain))
            records = g_client.get_records(domain, name=a_name, record_type='A')
            if not records:
                logging.warning('No record {} for {} found'.format(a_name, domain))
                successful = False
                # TODO add the record if configured to do so
                continue

            for record in records:
                if ip == record['data']:
                    logging.debug('Record {} for {} is still {}, no update required'.format(a_name, domain, ip))
                    continue

                result = g_client.update_record_ip(ip, domain, name=a_name, record_type='A')
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
                pub_ip = pif.get_public_ip()
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

