#!/usr/bin/env nix-shell
#! nix-shell -i python3 -p "python3.withPackages (ps: [ ps.cloudflare ])"
import os
import json
from cloudflare import Cloudflare
from optparse import OptionParser

HELP_DESCRIPTION='This is a simple utility for querying CloudFlare for DNS entries.'
HELP_EXAMPLE='Example: ./fqdns.py -d status.im -t CNAME'

def format_csv(record):
    return '{};{};{};{}'.format(
        record.type,
        record.name,
        record.content,
        record.proxied,
    )

def format_table(record):
    return '{:>20} {:1} {:>6} {:30} {}'.format(
        record.id,
        ('P' if record.proxied else ''),
        record.type,
        record.name,
        record.content,
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
    parser.add_option('-K', '--api-key', dest='cf_key', default=os.environ['CF_KEY'],
                      help='CloudFlare API key for auth (env CF_KEY used). (default: %default)')
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

    cf = Cloudflare(api_email=opts.cf_email, api_key=opts.cf_key)

    zones = cf.zones.list(per_page=100)
    zone = next(z for z in zones if z.name == opts.cf_domain)
    records = cf.dns.records.list(zone_id=zone.id, per_page=100)

    formatter = format_table
    if opts.csv:
        formatter = format_csv
    elif opts.json:
        formatter = format_json

    for r in records:
        if opts.type and r.type != opts.type:
            continue
        print(formatter(r))

if __name__ == '__main__':
    main()
