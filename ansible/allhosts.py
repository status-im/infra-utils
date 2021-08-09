#!/usr/bin/env python
import sys
import json
import requests
from optparse import OptionParser

HELP_DESCRIPTION = '''
This queries Consul for all available hosts and outputs them in the Ansible
inventory format, which is JSON with specific keys.
Assumes existence of Ansible certificate files.
https://docs.ansible.com/ansible/latest/dev_guide/developing_inventory.html
'''.strip()
HELP_EXAMPLE = '''
Example: ./allhosts.py -l debug -u https://consul.example.org:8400
'''


def parse_opts():
    parser = OptionParser(description=HELP_DESCRIPTION, epilog=HELP_EXAMPLE)
    # WARNING: The --list flag is mandatory for use with Ansible. We ignore it.
    parser.add_option('-l', '--list', action='store_true',
                      help='Mandatory flag for Ansible. Ignored.')
    parser.add_option('-d', '--hosts-domain', default='statusim.net',
                      help='Domain to append to hostnames.')
    parser.add_option('-u', '--consul-url', default='https://consul.statusim.net:8400',
                      help='Name of virtual network interface.')
    parser.add_option('-c', '--cert-chain', default='ansible/files/consul-ca.crt',
                      help='Path to Consul certificate CA chain.')
    parser.add_option('-p', '--cert-path', default='ansible/files/consul-client.crt',
                      help='Path to Consul certificate file')
    parser.add_option('-k', '--cert-key', default='ansible/files/consul-client.key',
                      help='Path to Consul certificate key file')

    return parser.parse_args()

def main():
    (opts, args) = parse_opts()

    data_centers = requests.get(
        '%s/v1/catalog/datacenters' % opts.consul_url,
        cert=(opts.cert_path, opts.cert_key),
        verify=opts.cert_chain,
    ).json()

    nodes = []
    for dc in data_centers:
        nodes.extend(requests.get(
            '%s/v1/catalog/nodes?dc=%s' % (opts.consul_url,dc),
            cert=(opts.cert_path, opts.cert_key),
            verify=opts.cert_chain,
        ).json())

    # JSON for Ansible
    out = {'_meta':{'hostvars':{}}}
    for node in nodes:
        out['_meta']['hostvars'][node['Node']] = {
            "dns_entry":    '%s.%s' % (node['Node'], opts.hosts_domain),
            "hostname":     node['Node'],
            "ansible_host": node['Address'],
            "data_center":  node['Datacenter'],
            "env":          node['Meta']['env'],
            "stage":        node['Meta']['stage'],
        }

        dc_group = out.setdefault(
            node['Datacenter'],
            {'children': [], 'hosts': [], 'vars': {} },
        )
        dc_group['hosts'].append(node['Node'])

        fleet_group = out.setdefault(
            '%s.%s' % (node['Meta']['env'],node['Meta']['stage']),
            {'children': [], 'hosts': [], 'vars': {} },
        )
        fleet_group['hosts'].append(node['Node'])

    out['all'] = { 'hosts': [node['Node'] for node in nodes] }

    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
