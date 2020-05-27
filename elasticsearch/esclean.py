#!/usr/bin/env python3
import os
from retry import retry
from optparse import OptionParser
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConflictError

HELP_DESCRIPTION='This is a simple utility for cleaning ElasticSearch indices.'
HELP_EXAMPLE='Example: ./esclean.py -i "logstash-2019.11.*" -p beacon -d'

def parse_opts():
    parser = OptionParser(description=HELP_DESCRIPTION, epilog=HELP_EXAMPLE)
    parser.add_option('-H', '--host', dest='es_host', default='localhost',
                      help='ElasticSearch host.')
    parser.add_option('-P', '--port', dest='es_port', default=9200,
                      help='ElasticSearch port.')
    parser.add_option('-i', '--index-pattern', default='logstash-*',
                      help='Patter for matching indices.')
    parser.add_option('-t', '--tag',
                      help='Had given tag.')
    parser.add_option('-p', '--program',
                      help='Program to query for.')
    parser.add_option('-m', '--message',
                      help='Message to query for.')
    parser.add_option('-f', '--fleet',
                      help='Fleet to query for.')
    parser.add_option('-s', '--severity',
                      help='Log severity/level.')
    parser.add_option('-I', '--logsource-ip',
                      help='IP of log source.')
    parser.add_option('-o', '--older-than',
                      help='How old the logs should be, in days.')
    parser.add_option('-d', '--delete', action='store_true',
                      help='Delete matching documents.')
    parser.add_option('-q', '--query', type='str',
                      help='Query matching documents.')
    
    return parser.parse_args()

def print_logs(docs):
    for doc in docs:
        log = doc['_source']
        print('{:26} {:21} {:38} {}'.format(
            log['@timestamp'], log.get('program', 'unknown'),
            log.get('logsource', 'unknown'), log['message'][:2000]
        ))

@retry(ConflictError, tries=5, delay=120, backoff=2)
def delete_retry(es, index, body):
    return es.delete_by_query(index=index, body=body)

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
    
    queries = []
    if opts.tag:
        queries.append({'match': {'tags': opts.tag}})
    if opts.program:
        queries.append({'term': {'program': opts.program}})
    if opts.fleet:
        queries.append({'term': {'fleet': opts.fleet}})
    if opts.severity:
        queries.append({'term': {'severity_name': opts.severity}})
    if opts.logsource_ip:
        queries.append({'term': {'logsource_ip': opts.logsource_ip}})
    if opts.message:
        queries.append({'match_phrase':{'message': opts.message}})
    if opts.query:
        queries.append({'query_string':{'query': opts.query}})
    if opts.older_than:
        queries.append({'range':{ '@timestamp': {
            'lt': 'now-{}d'.format(opts.older_than),
            'format': 'basic_date_time',
        }}})

    body = None
    if len(queries) > 0:
        body = {'query': {'bool': {'must': queries}}}

    for index in indices:
        resp = es.count(index=index, body=body)
        count = resp.get('count')
        print('{:22} count: {:6}'.format(index, count))

        if opts.delete and count > 0:
            rval = delete_retry(es, index, body)
            rval2 = es.indices.forcemerge(
                index=index,
                params={'only_expunge_deletes':'true'}
            )
            print('{:22} Deleted: {:10} Failed: {}'.format(index, rval['deleted'], rval2['_shards']['failed']))
        #else:
        #    resp = es.search(index=index, body=body)
        #    print_logs(resp['hits']['hits'])

if __name__ == '__main__':
    main()
