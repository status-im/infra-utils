#!/usr/bin/env python3
import os
import json
import CloudFlare

email = 'jakub@status.im'
token = os.environ['CF_TOKEN']

cf = CloudFlare.CloudFlare(email, token)

#zones = cf.zones.get(params = {'per_page':100})
#zone_id = zones[0]['id']
#zone_name = zones[0]['id']
#print('Zones:', [z['name'] for z in zones])

logs = cf.organizations.audit_logs.get('113ef908d19933ef327f079a3def53fc',
    params={
        'since': '2018-01-01',
        'per_page': 5000,
        'order': 'when',
        'direction': 'asc',
        'zone.name': 'status.im'
    }
)
for log in logs:
    if log['action']['type'] not in ['add', 'delete']:
        continue
    print('{:30} {:20} {:12} {:>10} {:>7} {:30} {}'.format(
        log['when'],
        log['actor'].get('email', log['metadata'].get('acted_on_behalf_of')),
        log['metadata'].get('zone_name'),
        log['action'].get('type'),
        log['metadata'].get('type') or '',
        log['metadata'].get('name') or '',
        log['metadata'].get('content') or ''
    ))
