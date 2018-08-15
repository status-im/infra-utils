#!/usr/bin/env python3
import os
import CloudFlare

email = 'jakub@status.im'
token = os.environ['CF_TOKEN']

cf = CloudFlare.CloudFlare(email, token)

zones = cf.zones.get(params = {'per_page':100})
zone_id = zones[0]['id']
zone_name = zones[0]['id']
print('Zones:', [z['name'] for z in zones])

# https://api.cloudflare.com/#audit-logs-list-user-audit-logs
user_id = cf.user.get()['id']
logs = cf.user.audit_logs.get('status.im',
    params={
        'actor.email': 'jakub@status.im',
        'since': '2018-06-01',
        'per_page': 500,
        'order': 'when',
        'direction': 'desc',
    }
)
print('Found:', len(logs))
for l in logs:                                                         
    if l['action']['type'] in ['logout', 'login']:
        continue
    print(l['when'], l['action'], l['metadata'])
