#!/usr/bin/env python

import json
import requests
from argparse import ArgumentParser, RawTextHelpFormatter

HELP_DEFINITION='''
Script to call the Superset API, authenticate and configure all the Headers correctly
'''
HELP_EXAMPLE='''
Example: 
    \n\t./superset_api_auth.py -e dashboard -t get -n username -p NotARealPassword
    \n\t./superset_api_auth.py -e chart -t post -d '{"some": "json data"}' -n username -p NotARealPassword
'''

DEFAULT_URL='https://superset.bi.status.im'


headers={
    'Content-Type': 'application/json',
    'accept': 'application/json',
}

auth_data={
    "provider": "db",
    "refresh": True,
}

def parse_args():
    parser = ArgumentParser(description=HELP_DEFINITION, epilog=HELP_EXAMPLE, formatter_class=RawTextHelpFormatter)
    parser.add_argument('-u', '--url',      required=False,     help='URL of the Superset instance',            default=DEFAULT_URL)
    parser.add_argument('-e', '--endpoint', required=True,      help='Endpoint to call')
    parser.add_argument('-t', '--type',     required=True,      help='Type of HTTP call to make',               choices=['get','post'])
    parser.add_argument('-d', '--data',     required=False,     help='Data in json format to pass in the call', default={})
    parser.add_argument('-n', '--username', required=True,      help='Username to connect with')
    parser.add_argument('-p', '--password', required=True,      help='Password to connect with')
    return parser.parse_args()


def main():
    args = parse_args()

    s = requests.Session()
    auth_data['username'] = args.username
    auth_data['password'] = args.password
    print(f'{args.url}')
    auth_req = s.post(f'{args.url}/api/v1/security/login', headers=headers, json=auth_data)
    print(f'{auth_req.json()}')
    access_token=auth_req.json()["access_token"]
    headers['Referer'] = f'{args.url}/api/v1/security/login'
    # Call to get CSRF token 
    headers['Authorization']= f'Bearer {access_token}'
    csrf_req = s.get('%s/api/v1/security/csrf_token/' % args.url, headers=headers)
    headers['X-CSRFToken'] = csrf_req.json()['result']

    if args.type == 'get':
        req = s.get(f'{args.url}/api/v1/{args.endpoint}', headers=headers)
        print(f'{req.json()}\n')
    elif args.type == 'post':
        req = s.post(f'{args.url}/api/v1/{args.endpoint}', headers=headers, json=args.data)
        print(f'{req.json()}\n')

if __name__ == '__main__':
    main()
