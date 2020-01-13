#!/usr/bin/env python3

import re
import json
import requests
import content_hash # https://pypi.org/project/content-hash
import ipfscluster  # https://pypi.org/project/ipfscluster
from multiaddr import Multiaddr

IPFS_CLUSTER_ADDR = 'http://localhost:9094'
STICKER_PACKS_META_URLS = [
  "https://cloudflare-ipfs.com/ipfs/QmWVVLwVKCwkVNjYJrRzQWREVvEk917PhbHYAUhA1gECTM",
  "https://cloudflare-ipfs.com/ipfs/QmWpG2Q5NB472KLgFysdCjB8D1Qf9hxR2KNJvtCJQJufDj",
]

# https://github.com/ethereum/EIPs/blob/master/EIPS/eip-1577.md
content_hash_rgx = r'e30101701220\w+'

content_hashes = []

for url in STICKER_PACKS_META_URLS:
    resp = requests.get(url)
    resp.raise_for_status()
    matches = re.findall(content_hash_rgx, resp.text)
    content_hashes.extend(matches)

# IPFS can't handle EIP-1577 content hashes
decoded_hashes = [content_hash.decode(ch) for ch in content_hashes]

class IpfsPinner:

    def __init__(self, addr=ipfscluster.DEFAULT_ADDR):
        self.client = ipfscluster.connect(addr)

    def is_pinned(self, chash):
        resp = self.client.pins.ls(chash)
        statuses = [peer['status'] for peer in resp['peer_map'].values()]
        return all(s == 'pinned' for s in statuses), statuses

    def pin(self, chash):
        return self.client.pins.add(chash)

ip = IpfsPinner()

for chash in decoded_hashes:
    pinned, statuses = ip.is_pinned(chash)
    print('{} - {}'.format(chash, statuses))

    if pinned:
        continue

    ip.pin(chash)
    print('{} - PINNED'.format(chash))
