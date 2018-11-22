#!/usr/bin/env python3
import os
import json
import CloudFlare
from optparse import OptionParser

HELP_DESCRIPTION='This is a simple utility for querying CloudFlare for audit logs.'
HELP_EXAMPLE='Example: ./get_log.py -s 2018-10-01 -a delete'

def format_log(log):
    return '{:30} {:20} {:12} {:>10} {:>7} {:30} {}'.format(
        log['when'],
        log['actor'].get('email', log['metadata'].get('acted_on_behalf_of')),
        log['metadata'].get('zone_name'),
        log['action'].get('type'),
        log['metadata'].get('type') or '',
        log['metadata'].get('name') or '',
        log['metadata'].get('content') or ''
    )

def parse_opts():
    parser = OptionParser(description=HELP_DESCRIPTION, epilog=HELP_EXAMPLE)
    parser.add_option('-M', '--mail', dest='cf_email', default='jakub@status.im',
                      help='CloudFlare Account email for auth. (default: %default)')
    parser.add_option('-T', '--token', dest='cf_token', default=os.environ['CF_TOKEN'],
                      help='CloudFlare API token for auth (env CF_TOKEN used). (default: %default)')
    parser.add_option('-o', '--organiation', dest='cf_org_id', default='113ef908d19933ef327f079a3def53fc',
                      help='Specify which CloudFlare organization to query. (default: %default)')
    parser.add_option('-d', '--domain', dest='cf_domain', default='status.im',
                      help='Specify which domain to query for. (default: %default)')
    parser.add_option('-a', '--actions', action='append', default=['add'],
                      help='Specify which CloudFlare actions to list. (default: %default)')
    parser.add_option('-b', '--before',
                      help='Query logs before this date. (ex: "2018-12-30")')
    parser.add_option('-s', '--since',
                      help='Query logs since this date. (ex: "2018-01-01")')
    
    return parser.parse_args()

def main():
    (opts, args) = parse_opts()

    cf = CloudFlare.CloudFlare(opts.cf_email, opts.cf_token)

    params = {
        'per_page': 5000,
        'order': 'when',
        'direction': 'asc',
        'zone.name': opts.cf_domain,
    }
    if opts.before:
        params['before'] = opts.before
    if opts.since:
        params['since'] = opts.since
    
    logs = cf.organizations.audit_logs.get(opts.cf_org_id, params=params)

    for log in logs:
        if log['action']['type'] not in opts.actions:
            continue
        print(format_log(log))

if __name__ == '__main__':
    main()
