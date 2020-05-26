#!/usr/bin/env python3
import os
import json
from optparse import OptionParser
from elasticsearch import Elasticsearch

HELP_DESCRIPTION='This a utility for deleting fields from documents.'
HELP_EXAMPLE='Example: ./delete_field.py -i 2018-10-01 --delete'

def parse_opts():
    parser = OptionParser(description=HELP_DESCRIPTION, epilog=HELP_EXAMPLE)
    parser.add_option('-H', '--host', dest='es_host', default='localhost',
                      help='ElasticSearch host.')
    parser.add_option('-P', '--port', dest='es_port', default=9200,
                      help='ElasticSearch port.')
    parser.add_option('-i', '--index-pattern', default='logstash-*',
                      help='Patter for matching indices.')
    parser.add_option('-f', '--field', type='str',
                      help='Name of field to remove from documents.')
    parser.add_option('-d', '--delete', action='store_true',
                      help='Delete field from matching documents.')
    (opts, args) = parser.parse_args()
    
    if not opts.field:
        parser.error('Field not specified!')
    
    return (opts, args)

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
        'query':{'bool':{'must':{'exists':{'field':opts.field}}}}
    }

    for index in indices:
      resp = es.count(index=index, body=body)
      count = resp.get('count')
      print('{:22} count: {:6}'.format(index, count))

      if opts.delete and count > 0:
        body['script'] = 'ctx._source.remove("peer_id")'
        try:
            rval = es.update_by_query(index=index, body=body)
        except Exception as ex:
            print(json.dumps(ex.info, indent=2))
        print('{:22} Updated: {:10} Failed: {}'.format(index, rval['updated'], rval.get('failed', 0)))

if __name__ == '__main__':
    main()
