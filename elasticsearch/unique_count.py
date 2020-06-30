#!/usr/bin/env python3
import os
import csv
import hashlib
from optparse import OptionParser
from elasticsearch import Elasticsearch

HELP_DESCRIPTION='This generates a CSV with buckets of peer_ids for every day.'
HELP_EXAMPLE='Example: ./unique_count.py -i "logstash-2019.11.*" -f peer_id'

def parse_opts():
    parser = OptionParser(description=HELP_DESCRIPTION, epilog=HELP_EXAMPLE)
    parser.add_option('-H', '--host', dest='es_host', default='localhost',
                      help='ElasticSearch host.')
    parser.add_option('-P', '--port', dest='es_port', default=9200,
                      help='ElasticSearch port.')
    parser.add_option('-i', '--index-pattern', default='logstash-*',
                      help='Patter for matching indices.')
    parser.add_option('-f', '--field', type='str', default='peer_id',
                      help='Name of the field to count.')
    parser.add_option('-o', '--out-file', type='str', default='out.csv',
                      help='Filename of CSV to write to.')
    parser.add_option('-m', '--max-size', default=10000,
                      help='Max number of counts to find.')
    (opts, args) = parser.parse_args()

    if not opts.field:
        parser.error('No field name specified!')
    
    return (opts, args)

def remove_prefix(text, prefix):
    return text[text.startswith(prefix) and len(prefix):]

def hash_string(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def main():
    (opts, args) = parse_opts()

    es = Elasticsearch(
        [{ 'host': opts.es_host,
           'port': opts.es_port }],
        timeout=1200,
        retry_on_timeout=True
    )
    
    print('Cluster: {}'.format(es.info().get('cluster_name')))
    
    indices = es.indices.get(index=opts.index_pattern).keys()
    
    body = {
        'size': 0,
        'aggs': { 'peers': {
            'terms': {
                'field': opts.field,
                'size': 10000,
            },
        }, },
    }

    csv_field_names = ['date', 'peer', 'count']

    with open(opts.out_file, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=csv_field_names)
        writer.writeheader()

        for index in indices:
            resp = es.search(index=index, body=body)
            aggs = resp.get('aggregations')
            print('{:22} count: {:6}'.format(index, len(aggs['peers']['buckets'])))

            for bucket in aggs['peers']['buckets']:
                writer.writerow({
                    'date': remove_prefix(index, 'logstash-'),
                    'peer': hash_string(bucket['key']),
                    'count': bucket['doc_count'],
                })

if __name__ == '__main__':
    main()
