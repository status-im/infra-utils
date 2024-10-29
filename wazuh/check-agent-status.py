#!/usr/bin/env python
import json
import logging
import argparse
import requests
from requests.auth import HTTPBasicAuth

DESCRIPTION = '''
This script is to check the Agent Syncing status.
It required a direct access to Wazuh Manager API, and the credential.
'''
WAZUH_API_HOST = 'localhost'
WAZUH_API_PORT = '55000'
QUERY_TYPE = ['sync', 'groups']

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def parse_opts():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('-H', '--host', default=WAZUH_API_HOST, help='Wazuh host')
    parser.add_argument('-p', '--port', default=WAZUH_API_PORT, help='Wazuh Port')
    parser.add_argument('-u', '--username', help='Wazuh API Username')
    parser.add_argument('-P', '--password', help='Wazuh API Password')
    parser.add_argument('-q', '--queries', default=QUERY_TYPE, help='List of queries to execute, default is all query available')
    parser.add_argument('-c', '--certificate', default=False, help='Path to Wazuh Root CA, optional')
    return parser.parse_args()

class Wazuh:

    def __init__(self, hostname, port, verify):
        self.hostname = hostname
        self.port = port
        self.verify = verify

    def login(self, username, password):
        req=requests.post(f"https://{self.hostname}:{self.port}/security/user/authenticate",
                auth=HTTPBasicAuth(username, password), verify=self.verify)
        self.headers ={"Authorization": f"Bearer {req.json().get('data').get('token')}"}

    def get_agents_status(self):
        req = requests.get(f"https://{ self.hostname }:{ self.port }/agents",
                verify=self.verify, headers=self.headers)
        self.print_agents_status(req.json().get('data').get('affected_items'))

    def print_agents_status(self, agents):
        logger.info("| Agent Id | Name | Group | OS | Status | Sync Status | ConfigSum | MergedSum |")
        for agent in agents:
            logger.info("| %s | %s | %s | %s | %s | %s | %s | %s |",
                agent.get('id'), agent.get('node_name'), agent.get('group'), agent.get('os').get('name'),
                        agent.get('status'), agent.get('group_config_status'), agent.get('configSum'), agent.get('mergedSum'))


    def get_groups(self):
        req = requests.get(f"https://{ self.hostname }:{ self.port }/groups",
                verify=self.verify, headers=self.headers)
        self.print_groups(req.json().get('data').get('affected_items'))

    def print_groups(self, groups):
        logger.info("| Group Name | Number of Agent | Config Sum | Merged Sum |")
        for group in groups:
            if group.get('name') != '.git':
                logger.info("| %s | %s | %s | %s |",
                    group.get('name'), group.get('count'), group.get('configSum'), group.get('mergedSum'))



def main():
    opts = parse_opts()
    conn = Wazuh(opts.host, opts.port, opts.certificate)
    logger.info("Getting Bearer token")
    conn.login(opts.username, opts.password)
    if 'sync' in opts.queries:
        logger.info("Getting Agents Status")
        conn.get_agents_status()
    if 'groups' in opts.queries:
        logger.info("Getting Groups info")
        conn.get_groups()
main()


