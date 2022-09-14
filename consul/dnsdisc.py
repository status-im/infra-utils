#!/usr/bin/env python3
import os
import sys
import time
import json
import consul
import logging
import requests
import CloudFlare
from optparse import OptionParser
from subprocess import Popen, PIPE
from contextlib import contextmanager

HOME=os.path.expanduser('~')
HELP_DESCRIPTION='This a utility for generating DNS Discovery records'
HELP_EXAMPLE='Example: ./dnsdisc.py -p 123abc -d nodes.example.org'

# Setup logging.
log_format = '[%(levelname)s] %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format)
LOG = logging.getLogger(__name__)

def parse_opts():
    parser = OptionParser(description=HELP_DESCRIPTION, epilog=HELP_EXAMPLE)
    parser.add_option('-m', '--cf-email', default='jakub@status.im',
                      help='CloudFlare Account email. (default: %default)')
    parser.add_option('-t', '--cf-token', default=os.environ.get('CF_TOKEN'),
                      help='CloudFlare API token (env: CF_TOKEN). (default: %default)')
    parser.add_option('-D', '--cf-domain', default='status.im',
                      help='CloudFlare zone domain. (default: %default)')
    parser.add_option('-r', '--rpc-host', default='127.0.0.1',
                      help='RPC listen host.')
    parser.add_option('-c', '--rpc-port', default=8545,
                      help='RPC listen port.')
    parser.add_option('-H', '--consul-host', default='127.0.0.1',
                      help='Consul host.')
    parser.add_option('-P', '--consul-port', default=8500,
                      help='Consul port.')
    parser.add_option('-T', '--consul-token', default=os.environ.get('CONSUL_HTTP_TOKEN'),
                      help='Consul API token.')
    parser.add_option('-n', '--query-service', default='nim-waku-v2-enr',
                      help='Name of Consul service to query.')
    parser.add_option('-e', '--query-env', default='wakuv2',
                      help='Name of Consul service to query.')
    parser.add_option('-s', '--query-stage', default='test',
                      help='Name of Consul service to query.')
    parser.add_option('-d', '--domain', type='string',
                      help='Fully qualified domain name for the tree root entry.')
    parser.add_option('-C', '--tree-creator', default=HOME+'/work/nim-dnsdisc/build/tree_creator',
                      help='Path to tree_creator binary from nim-dnsdisc.')
    parser.add_option('-p', '--private-key', default=os.environ.get('PRIVATE_KEY'),
                      help='Tree creator private key as 64 char hex string.')
    parser.add_option('-l', '--log-level', default='info',
                      help='Change default logging level.')
    parser.add_option('-x', '--dry-run', action='store_true',
                      help='Do not delete or create DNS records.')
    
    return parser.parse_args()

class ConsulCatalog:
    def __init__(self, host='localhost', port=8500, token=None):
        self.client = consul.Consul(host=host, port=port, token=token)

    def dcs(self):
        return self.client.catalog.datacenters()

    def services(self, service, dc, meta={}):
        return self.client.catalog.service(service, dc=dc, node_meta=meta)

    def all_services(self, service, meta={}):
        rval = []
        for dc in self.dcs():
            rval.extend(self.services(service, dc, meta)[1])
        return rval


class DNSDiscovery:
    def __init__(self, path, host, port, private_key):
        self.path = path
        self.host = host
        self.port = port
        self.private_key = private_key
        self.url = 'http://%s:%d' % (self.host, self.port)

    @contextmanager
    def start(self, domain, enrs):
        try:
            args = [
                self.path,
                "--private-key=%s" % self.private_key,
                "--rpc-address=%s" % self.host,
                "--rpc-port=%s" % self.port,
                "--domain=%s" % domain,
            ] + [
                '--enr-record=' + enr for enr in enrs
            ]
            LOG.debug('Starting node: %s', ' '.join(args))
            self.process = Popen(args, stdout=PIPE)
            # Not pretty, but the process needs time to start.
            time.sleep(1)
            yield self.process
        finally:
            self.process.kill()

    def _rpc(self, method, params=[]):
        payload = {
            "method": method,
            "params": params,
            "jsonrpc": "2.0",
            "id": 0,
        }
        rval = requests.request(
            'POST',
            self.url,
            headers={'Content-Type': 'application/json'},
            data=json.dumps(payload)
        )
        return rval.json()

    def records(self):
        return self._rpc('get_txt_records')['result']

    def generate(self, domain, enrs):
        with self.start(domain, enrs):
            return self.records()


class CFManager:
    def __init__(self, email, token, domain):
        self.client = CloudFlare.CloudFlare(email, token)
        zones = self.client.zones.get(params={'per_page':100})
        self.zone = next(z for z in zones if z['name'] == domain)

    def txt_records(self, suffix):
        # Get currently existing records
        records = self.client.zones.dns_records.get(
            self.zone['id'], params={'type':'txt', 'per_page':1000}
        )
        # Match records only under selected domain.
        return list(filter(
            lambda r: r['name'].endswith(suffix), records
        ))

    def delete(self, record_id):
        return self.client.zones.dns_records.delete(
            self.zone['id'], record_id
        )

    def create(self, name, content):
        self.client.zones.dns_records.post(
            self.zone['id'],
            data={'name': name, 'content': content, 'type': 'TXT'}
        )


def main():
    (opts, args) = parse_opts()

    LOG.setLevel(opts.log_level.upper())

    LOG.debug('Connecting to Consul: %s:%d',
             opts.consul_host, opts.consul_port)
    catalog = ConsulCatalog(
        host=opts.consul_host,
        port=opts.consul_port,
        token=opts.consul_token,
    )

    LOG.debug('Querying service: %s (%s.%s)',
             opts.query_service, opts.query_env, opts.query_stage)
    services = catalog.all_services(
        opts.query_service,
        meta={
          'env': opts.query_env,
          'stage': opts.query_stage
        }
    )

    if len(services) == 0:
        LOG.error('No services found!')
        sys.exit(1)

    for service in services:
        LOG.info('Service found: %s:%s', service['Node'], service['ServiceID'])
        LOG.debug('Service ENR: %s', service['ServiceMeta']['node_enode'])

    service_enrs = [s['ServiceMeta']['node_enode'] for s in services]

    LOG.debug('Using DNS tree creator: %s', opts.tree_creator)
    dns = DNSDiscovery(
        opts.tree_creator,
        opts.rpc_host,
        opts.rpc_port,
        opts.private_key
    )
    LOG.debug('Generating DNS records...')
    new_records = dns.generate(opts.domain, service_enrs)

    for record, value in sorted(new_records.items()):
        LOG.debug('New DNS Record: %s -> %s', record, value)

    LOG.debug('Connecting to CloudFlare: %s', opts.cf_email)
    cf = CFManager(opts.cf_email, opts.cf_token, opts.cf_domain)

    LOG.debug('Querying TXT DNS records: %s', opts.domain)
    raw_old_records = cf.txt_records(opts.domain)

    old_records_ids = {r['name']: r['id'] for r in raw_old_records}
    old_records = set((r['name'], r['content']) for r in raw_old_records)
    new_records = set((k.lower(), v) for k,v in new_records.items())

    # Delete records which changed or are gone.
    for name, value in sorted(old_records - new_records):
        LOG.info('Deleting record: %s', name)
        if not opts.dry_run:
            cf.delete(old_records_ids[name])

    # Create new records or update old ones.
    for name, value in sorted(new_records - old_records):
        LOG.info('Creating record: %s', name)
        if not opts.dry_run:
            cf.create(name, value)

    if opts.dry_run:
        LOG.warning('Dry-run mode! No changes made.')

if __name__ == '__main__':
    main()
