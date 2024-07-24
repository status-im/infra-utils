#!/usr/bin/env python3
import os
import logging
import warnings
from retry.api import retry_call
from optparse import OptionParser
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConflictError
from elasticsearch.exceptions import ElasticsearchWarning

# Ignore warnings about disabled security features.
warnings.simplefilter('ignore', ElasticsearchWarning)

# Setup logging.
log_format = '[%(levelname)s] %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format)
logging.getLogger('elastic_transport.transport').setLevel(logging.WARNING)
LOG = logging.getLogger(__name__)

HELP_DESCRIPTION='This is a simple utility for cleaning ElasticSearch indices.'
HELP_EXAMPLE='Example: ./esclean.py -i "logstash-2019.11.*" -p beacon -d'

def parse_opts():
    parser = OptionParser(description=HELP_DESCRIPTION, epilog=HELP_EXAMPLE)
    parser.add_option('-H', '--host', dest='es_host', default='localhost',
                      help='ElasticSearch host.')
    parser.add_option('-P', '--port', dest='es_port', default=9200,
                      help='ElasticSearch port.')
    parser.add_option('-T', '--timeout', dest='es_timeout', default=3000,
                      help='ElasticSearch timeout.')
    parser.add_option('-R', '--retries', dest='es_retries', default=5,
                      help='ElasticSearch retries.')
    parser.add_option('-D', '--delay', dest='es_delay', default=120,
                      help='ElasticSearch retry delay.')
    parser.add_option('-B', '--backoff', dest='es_backoff', default=2,
                      help='ElasticSearch retry backoff.')
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
    parser.add_option('-L', '--logsource',
                      help='Hostname of log source.')
    parser.add_option('-I', '--logsource-ip',
                      help='IP of log source.')
    parser.add_option('-o', '--older-than',
                      help='How old the logs should be, in days.')
    parser.add_option('-d', '--delete', action='store_true',
                      help='Delete matching documents.')
    parser.add_option('-q', '--query', type='str',
                      help='Query matching documents.')
    parser.add_option('-l', '--log-level', default='info',
                      help='Change default logging level.')

    return parser.parse_args()

def print_logs(docs):
    for doc in docs:
        log = doc['_source']
        LOG.info('{:26} {:21} {:38} {}'.format(
            log['@timestamp'], log.get('program', 'unknown'),
            log.get('logsource', 'unknown'), log['message'][:2000]
        ))

def delete_retry(es, index, body, tries=5, delay=120, backoff=2):
    return retry_call(
        es.delete_by_query,
        fkwargs={'index': index, 'body': body},
        tries=tries,
        delay=delay,
        backoff=backoff
    )

def main():
    (opts, args) = parse_opts()

    LOG.setLevel(opts.log_level.upper())

    es = Elasticsearch(
        hosts=[{ 'host': opts.es_host, 'port': opts.es_port, 'scheme': 'http'}],
        request_timeout=opts.es_timeout,
        retry_on_timeout=True
    )

    LOG.info('Cluster: {}'.format(es.info().get('cluster_name')))

    indices = es.indices.get(index=opts.index_pattern).keys()

    queries = []
    if opts.tag:
        queries.append({'match': {'tags': opts.tag}})
    if opts.program and '*' in opts.program:
        queries.append({'wildcard': {'program': opts.program}})
    elif opts.program:
        queries.append({'term': {'program': opts.program}})
    if opts.fleet:
        queries.append({'match': {'fleet': opts.fleet}})
    if opts.severity:
        queries.append({'term': {'severity_name': opts.severity}})
    if opts.logsource:
        queries.append({'match': {'logsource': opts.logsource}})
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
        resp = es.count(index=index, **body)
        count = resp.get('count')
        LOG.info('{:22} count: {:8}'.format(index, count))

        if opts.delete and count > 0:
            rval = delete_retry(
                es, index, body,
                tries=opts.es_retries,
                delay=opts.es_delay,
                backoff=opts.es_backoff
            )
            rval2 = es.indices.forcemerge(
                index=index,
                only_expunge_deletes=True,
            )
            LOG.info('{:22} Deleted: {:10} Failed: {}'.format(index, rval['deleted'], rval2['_shards']['failed']))

if __name__ == '__main__':
    main()
