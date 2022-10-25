#!/usr/bin/env python3
import os
import sys
import time
import json
import requests
from optparse import OptionParser

HELP_DESCRIPTION='This is a simple utility for querying CloudFlare for DNS entries.'
HELP_EXAMPLE='Example: ./fqdns.py -d status.im -t CNAME'

class BeaconChainAPI:

    def __init__(self, token, url='https://prater.beaconcha.in/api/'):
        self.token = token
        self.url = url

    def _req(self, method, path):
        try:
            rval = requests.request(method, self.url+path, headers={'apikey':self.token})
            rval.raise_for_status()
        except Exception as ex:
            print(rval.text)
            raise ex
        return rval

    def _get(self, path):
        return self._req('GET', path)

    def health(self):
        return self._get('healthz').text

    def validator(self, index):
        return self._get('v1/validator/%s' % index).json()

def parse_opts():
    parser = OptionParser(description=HELP_DESCRIPTION, epilog=HELP_EXAMPLE)
    parser.add_option('-u', '--url', default='https://prater.beaconcha.in/api/',
                      help='format records as a csv file.')
    parser.add_option('-t', '--token', default=os.environ['BEACON_CHAIN_TOKEN'],
                      help='Beaconcha.in API token, sourced from BEACON_CHAIN_TOKEN env var.')
    
    return parser.parse_args()

def main():
    (opts, args) = parse_opts()

    api = BeaconChainAPI(opts.token, opts.url)

    for line in sys.stdin:
        val_id = line.rstrip()
        rval = api.validator(val_id)
        print(json.dumps({
            'id': val_id,
            'status': rval['data']['status'],
            'slashed': rval['data']['slashed'],
            'balance': rval['data']['balance'],
        }))
        time.sleep(6)

if __name__ == '__main__':
    main()
