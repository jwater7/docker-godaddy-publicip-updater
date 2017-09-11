#!/usr/bin/env python3

import os
import sys
import traceback
import time
import pif
import godaddypy

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

    for domain in godaddy_domains:
        for a_name in godaddy_a_names:

            print('Getting A records with {} for {}'.format(a_name, domain))
            records = g_client.get_records(domain, name=a_name, record_type='A')
            if not records:
                print('No record {} for {} found'.format(a_name, domain))
                # TODO add the record if configured to do so
                continue

            for record in records:
                if ip == record['data']:
                    print('Record {} for {} is still {}, no update required'.format(a_name, domain, ip))
                    continue

                result = g_client.update_record_ip(ip, domain, name=a_name, record_type='A')
                if result is True:
                    print('Updated {} for {} to {}'.format(a_name, domain, ip))

def loop_forever():

    public_ip = False

    # Loop forever
    while True:

        # Go get our current public IP address
        new_ip = False
        while not new_ip:
            new_ip = pif.get_public_ip()
            # Done if we got one
            if new_ip:
                break

            time.sleep(get_ip_wait_sec)

        # If we got the same IP address, we will try again later
        if public_ip != new_ip:
            print('new-ip: {}, old-ip: {}'.format(new_ip, public_ip))
            public_ip = new_ip

            # Update the records at godaddy
            try:
                update_godaddy_records(public_ip)
            except:
                print('Unable to update godaddy records')
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_exception(exc_type, exc_value, exc_traceback)

        time.sleep(update_interval_sec)

loop_forever()

