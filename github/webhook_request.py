#!/usr/bin/env python3

import sys
import json
import hmac
import hashlib
import requests
import argparse
from os import environ
from uuid import uuid4

HELP_DESCRIPTION='This a utility for adding accounts to private GitHub repos.'
HELP_EXAMPLE='Example: ./add_to_private.py -o "waku-org" -u "status-im-auto"'

# This is just an example payload.
PAYLOAD={
  'ref': 'refs/heads/deploy-develop',
  'before': '2ef2124e7e739d8fe8a14d7c1660c0fb29db247c',
  'after': '750c8bd47aaf0d6d619c64c67b7ec2e4044f11a7',
}

def parse_args():
    parser = argparse.ArgumentParser(
        description=HELP_DESCRIPTION,
        epilog=HELP_EXAMPLE,
    )
    parser.add_argument('-u', '--url',
                        help='Webhook URL.')
    parser.add_argument('-e', '--event', default='push',
                        help='Webhook GitHub event.')
    parser.add_argument('-s', '--secret', default=environ.get('WEBHOOK_SECRET'),
                        help='Webhook Secret.')
    parser.add_argument('-p', '--payload', default=PAYLOAD,
                        help='Webhook Secret.')
    parser.add_argument('-t', '--timeout', default=5,
                        help='Webhook request timeout.')

    args = parser.parse_args()

    return args


def main():
    args = parse_args()

    secret = args.secret.encode('utf-8')
    data = json.dumps(args.payload).encode('utf-8')

    digest = lambda algo: hmac.new(secret, data, algo).hexdigest()

    headers = {
        'Content-Type':        'application/json',
        'X-Hub-Signature':     'sha1=%s'   % digest(hashlib.sha1),
        'X-Hub-Signature-256': 'sha256=%s' % digest(hashlib.sha256),
        'X-GitHub-Event':      args.event,
        'X-GitHub-Delivery':   str(uuid4()),
    }

    try:
        rval = requests.post(
            args.url,
            data=data,
            headers=headers,
            timeout=args.timeout,
        )
    except requests.exceptions.ConnectionError as ex:
        print(ex)
        sys.exit(1)

    print(rval.status_code, rval.reason)
    print(rval.headers)
    print(rval.text)

if __name__ == '__main__':
    main()
