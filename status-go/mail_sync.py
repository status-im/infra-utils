#!/usr/bin/env python

import json
import time
import requests
from optparse import OptionParser
from datetime import datetime, timedelta

FLEETS_URL = "https://fleets.status.im/"

HELP_DESCRIPTION='Utility for syncing Mailservers archived envelopes.'
HELP_EXAMPLE='./sync.py --server mail-01.do-ams3.eth.prod'

def parse_opts():
    parser = OptionParser(description=HELP_DESCRIPTION, epilog=HELP_EXAMPLE)
    parser.add_option('-s', '--server',
                      help='Name of mailserver to sync.')
    parser.add_option('-H', '--host', default='localhost',
                      help='status-go JSON RPC host.')
    parser.add_option('-P', '--port', type='int', default=8545,
                      help='status-go JSON RPC port.')
    parser.add_option('-d', '--days', type='int', default=30,
                      help='How many days in the past to sync.')
    parser.add_option('-S', '--sleep', type='int', default=10,
                      help='Seconds to wait before checking if peer was added.')
    (opts, args) = parser.parse_args()

    if opts.server is None:
        parser.error("The --server is required!")
    return (opts, args)

def get_enode(server):
    fleets = requests.get(FLEETS_URL).json()

    for fleet in fleets["fleets"].values():
        if fleet["mail"].get(server) is not None:
            return fleet["mail"].get(server)
    return None

def get_unix_ts(d):
    return int(time.mktime(d.timetuple()))

def contains_peer_id(peers, enode):
    node_id = enode.lstrip('enode://').split('@')[0]
    for peer in peers:
        if node_id in peer:
            return True
    return False

class RPCClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def _enode(self):
        return "http://{}:{}".format(self.host, self.port)

    def call(self, method, params=[]):
        headers = {"Content-Type": "application/json"}
        data = {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}
        # make the RPC call
        resp = requests.post(
            self._enode(),
            headers=headers,
            data=json.dumps(data)
        )
        # status code is always 200, even with error
        error = resp.json().get("error") 
        if error is not None:
            raise Exception(error)
        return resp.json().get("result")

def main():
    (opts, args) = parse_opts()
    
    enode = get_enode(opts.server)

    rpc = RPCClient(opts.host, opts.port)

    print("Syncing: {}".format(opts.server))
    print("Enode: {}".format(enode))

    # The addPeer call is async and takes time to work.
    # Also devp2p is fucking reatarded and has conn. timeouts.
    while True:
        rpc.call("admin_addPeer", [enode])
        peers = rpc.call("admin_peers")
        if contains_peer_id(peers, enode):
            break
        else:
            print('Failed to addPeer, sleeping...')
            time.sleep(opts.sleep)
       
    rpc.call("shh_markTrustedPeer", [enode])
    rpc.call("shhext_syncMessages", [{
        "mailServerPeer": enode,
        "to": get_unix_ts(datetime.now()),
        "from": get_unix_ts(datetime.now()-timedelta(days=opts.days)),
        "limit": 1000,
        "followCursor": True
    }])

    print('SUCCESS!')

if __name__ == '__main__':
    main()
