#!/usr/bin/env python3
import os
import json
import CloudFlare

#email = 'jakub@status.im'
#token = os.environ['CF_TOKEN']
#
#cf = CloudFlare.CloudFlare(email, token)
#
#zones = cf.zones.get(params = {'per_page':100})
#zone_id = zones[0]['id']
#zone_name = zones[0]['id']
#print('Zones:', [z['name'] for z in zones])
#
# BROKEN: https://github.com/cloudflare/python-cloudflare/issues/50
## https://api.cloudflare.com/#audit-logs-list-user-audit-logs
#user_id = cf.user.get()['id']
#logs = cf._base.call_with_auth('GET', 
#logs = cf.user.audit_logs.get('status.im',
#    params={
#        'actor.email': 'jakub@status.im',
#        'since': '2018-06-01',
#        'per_page': 500,
#        'order': 'when',
#        'direction': 'desc',
#    }
#)
with open('/tmp/audit_logs.json') as f:
    logs = json.load(f)['result']

print('Found:', len(logs))
for l in logs:                                                         
    if l['action']['type'] in ['logout', 'login']:
        continue
    if l['metadata'].get('zone_name') != 'status.im':
        continue
    if l['resource'].get('type') != 'DNS_record':
        continue
    print(l['when'], l['action']['info'])
