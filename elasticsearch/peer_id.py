#!/usr/bin/env python3
import os
import json
from optparse import OptionParser
from elasticsearch import Elasticsearch

HELP_DESCRIPTION='This is a simple utility extracting a peer_id field for existing logs.'
HELP_EXAMPLE='Example: ./peer_id.py -s 2018-10-01 -a delete'

PAINLESS_SCRIPT = """
if (ctx._source.peer_id == null) {
  def match = /peerID=(\w+)/.matcher(ctx._source.message);
  if (match.find()) {
    ctx._source.peer_id = match.group(1);
  }
}
"""

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
    parser.add_option('-u', '--update', action='store_true',
                      help='Update matching documents.')
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
        timeout=1200,
        retry_on_timeout=True
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
      elif opts.update:
        # add the script for extracting peer_id
        body['script'] = { 'lang': 'painless', 'inline': PAINLESS_SCRIPT }
        try:
            rval = es.update_by_query(index=index, body=body)
        except Exception as ex:
            print(json.dumps(ex.info, indent=2))
        print('{:22} Updated: {:10} Failed: {}'.format(index, rval['updated'], rval.get('failed', 0)))

if __name__ == '__main__':
    main()
