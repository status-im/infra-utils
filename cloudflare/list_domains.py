#!/usr/bin/env python3
import os
import CloudFlare

email = 'jakub@status.im'
token = os.environ['CF_TOKEN']

cf = CloudFlare.CloudFlare(email, token)
zones = cf.zones.get(params = {'per_page':100})

for z in zones:
    zone_id = z['id']
    zone_name = z['name']

    settings_ssl = cf.zones.settings.ssl.get(zone_id)
    ssl_status = settings_ssl['value']

    settings_ipv6 = cf.zones.settings.ipv6.get(zone_id)
    ipv6_status = settings_ipv6['value']

    #print(zone_id, zone_name, ssl_status, ipv6_status)

    records = cf.zones.dns_records.get(zone_id, params={'per_page': 1000})

    for r in records:
        print('{};{};{};{}'.format(
            r['type'],
            r['name'],
            r['content'],
            r['zone_name'],
        ))
