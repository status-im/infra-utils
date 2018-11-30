#!/usr/bin/env python3
import os
from optparse import OptionParser
from elasticsearch import Elasticsearch

HELP_DESCRIPTION='This is a simple utility for querying CloudFlare for audit logs.'
HELP_EXAMPLE='Example: ./get_log.py -s 2018-10-01 -a delete'

def parse_opts():
    parser = OptionParser(description=HELP_DESCRIPTION, epilog=HELP_EXAMPLE)
    parser.add_option('-H', '--host', dest='es_host', default='localhost',
                      help='ElasticSearch host.')
    parser.add_option('-P', '--port', dest='es_port', default=9200,
                      help='ElasticSearch port.')
    parser.add_option('-i', '--index-pattern', default='logstash-*',
                      help='Patter for matching indices.')
    parser.add_option('-p', '--program',
                      help='Program to query for.')
    parser.add_option('-m', '--message',
                      help='Message to query for.')
    parser.add_option('-f', '--fleet',
                      help='Fleet to query for.')
    parser.add_option('-d', '--delete', action='store_true',
                      help='Delete matching documents.')
    parser.add_option('-q', '--query', type='int', default=0,
                      help='Query matching documents.')
    
    return parser.parse_args()

def print_logs(docs):
    for doc in docs:
        log = doc['_source']
        print('{:26} {:21} {:38} {}'.format(
            log['@timestamp'], log['program'],
            log['logsource'], log['message'][:90]
        ))

def main():
    (opts, args) = parse_opts()

    es = Elasticsearch(
        [{ 'host': opts.es_host,
           'port': opts.es_port }],
        timeout=600
    )
    
    print('Cluster: {}'.format(es.info().get('cluster_name')))
    
    indices = es.indices.get(index=opts.index_pattern).keys()
    
    queries = []
    if opts.program:
        queries.append({'term': {'program': opts.program}})
    if opts.fleet:
        queries.append({'term': {'fleet': opts.fleet}})
    if opts.message:
        queries.append({'match_phrase':{'message': opts.message}})

    body = None
    if len(queries) > 0:
        body = {'query': {'bool': {'must': queries}}}

    for index in indices:
      resp = es.count(index=index, body=body)
      count = resp.get('count')
      print('{:22} count: {:6}'.format(index, count))

      if opts.query > 0:
        resp = es.search(index=index, body=body)
        print_logs(resp['hits']['hits'])
      elif opts.delete:
        rval = es.delete_by_query(index=index, body=body)
        rval2 = es.indices.forcemerge(
            index=index,
            params={'only_expunge_deletes':'true'}
        )
        print('{:22} Deleted: {:10} Failed: {}'.format(index, rval['deleted'], rval2['_shards']['failed']))

if __name__ == '__main__':
    main()
