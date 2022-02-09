#!/usr/bin/env python
import sys
import json
from requests import get
from optparse import OptionParser

HELP_DESCRIPTION = '''
Simple script to output counts of hosts in all fleets and all DCs.
'''.strip()
HELP_EXAMPLE = '''
Example: ./stats.py -u http://consul.example.org:8400
'''


def parse_opts():
    parser = OptionParser(description=HELP_DESCRIPTION, epilog=HELP_EXAMPLE)
    parser.add_option('-u', '--consul-url', default='http://localhost:8500',
                      help='Name of virtual network interface.')

    return parser.parse_args()

def main():
    (opts, args) = parse_opts()

    nodes = []
    envs = {}
    fleets = {}
    dcs = {}

    data_centers = get('%s/v1/catalog/datacenters' % opts.consul_url)
    for dc in data_centers.json():
        node = get('%s/v1/catalog/nodes?dc=%s' % (opts.consul_url,dc))
        nodes.extend(node.json())

    for node in nodes:
        meta = node['Meta']
        fleet_name = '%s.%s' % (meta['env'], meta['stage'])


        # Fix for inconsistency in fleet naming
        if meta['stage'] in ['hq', 'misc', 'office', 'bi', 'ci']:
            env = envs.setdefault(meta['stage'], [])
        else:
            env = envs.setdefault(meta['env'], [])
        dc = dcs.setdefault(node['Datacenter'], [])
        fleet = fleets.setdefault(fleet_name, [])

        dc.append(node['Node'])
        fleet.append(node['Node'])
        env.append(node['Node'])

    out = {
        'total': len(nodes),
        'dcs': {dc: len(hosts) for dc, hosts in dcs.items()},
        'envs': {env: len(hosts) for env, hosts in envs.items()},
        #'fleets': {fleet: len(hosts) for fleet, hosts in fleets.items()},
    }

    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
