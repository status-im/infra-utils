#!/usr/bin/env python3
import os
import json
import CloudFlare
from optparse import OptionParser

HELP_DESCRIPTION='This is a simple utility for querying CloudFlare for DNS entries.'
HELP_EXAMPLE='Example: ./fqdns.py -d status.im -t CNAME'

def format_csv(record):
    return '{};{};{};{}'.format(
        record['type'],
        record['name'],
        record['content'],
        record['proxied'],
    )

def format_table(record):
    return '{:>20} {:1} {:>6} {:30} {}'.format(
        record['id'],
        ('P' if record['proxied'] else ''),
        record['type'],
        record['name'],
        record['content'],
    )

def format_json(record):
    return json.dumps(
        {k: record[k] for k in (
            'id', 'proxied', 'type', 'name', 'content'
        )}
    )

def parse_opts():
    parser = OptionParser(description=HELP_DESCRIPTION, epilog=HELP_EXAMPLE)
    parser.add_option('-M', '--mail', dest='cf_email', default='jakub@status.im',
                      help='CloudFlare Account email for auth. (default: %default)')
    parser.add_option('-T', '--token', dest='cf_token', default=os.environ['CF_TOKEN'],
                      help='CloudFlare API token for auth (env CF_TOKEN used). (default: %default)')
    parser.add_option('-d', '--domain', dest='cf_domain', default='status.im',
                      help='Specify which domain to query for. (default: %default)')
    parser.add_option('-t', '--type', type=str,
                      help='Type of DNS records to query for.')
    parser.add_option('-c', '--csv', action='store_true',
                      help='Format records as a CSV file.')
    parser.add_option('-j', '--json', action='store_true',
                      help='Format records as a CSV file.')
    
    opts, args = parser.parse_args()

    if opts.csv and opts.json:
        parser.error('Options ---csv and --json are mutually exclusive.')
    
    return opts, args

def main():
    (opts, args) = parse_opts()
    
    cf = CloudFlare.CloudFlare(opts.cf_email, opts.cf_token)

    zones = cf.zones.get(params={'per_page':100})
    zone = next(z for z in zones if z['name'] == opts.cf_domain)
    records = cf.zones.dns_records.get(zone['id'], params={'per_page': 1000})

    formatter = format_table
    if opts.csv:
        formatter = format_csv
    elif opts.json:
        formatter = format_json

    for r in records:
        if opts.type and r['type'] != opts.type:
            continue
        print(formatter(r))

if __name__ == '__main__':
    main()
