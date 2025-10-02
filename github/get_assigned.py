#!/usr/bin/env python3
import os
import sys
import csv
import json
import logging
from datetime import datetime, timedelta
from optparse import OptionParser
from github import Github, GithubException

HELP_DESCRIPTION='Utility getting assigned issues and pull requests for user.'
HELP_EXAMPLE='Example: ./get_assigned.py -o status-im -o logos-co -u jakubgs'

# Setup logging.
log_format = '[%(levelname)s] %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format)
LOG = logging.getLogger(__name__)

DEFAULT_GH_ORGS = ['Develp-GmbH', 'status-im', 'vacp2p', 'waku-org', 'logos-co', 'acid-info', 'keycard-tech']

def parse_opts():
    parser = OptionParser(description=HELP_DESCRIPTION, epilog=HELP_EXAMPLE)
    parser.add_option('-o', '--github-orgs', type='string', action='append', default=DEFAULT_GH_ORGS,
                      help='Names of organizations to scan.')
    parser.add_option('-s', '--state', type='string', default='open',
                      help='Issue state to query for.')
    parser.add_option('-t', '--type', type='string', default='issue',
                      help='Names of user to query for.')
    parser.add_option('-U', '--updated', type='string', default=(datetime.now() - timedelta(days=30)).date(),
                      help='Time since which issue has been updated.')
    parser.add_option('-u', '--user', type='string',
                      help='Names of user to query for.')
    parser.add_option('-T', '--github-token', default=os.environ.get('GH_TOKEN', None),
                      help='GitHub API token.')
    parser.add_option('-l', '--log-level', default='info',
                      help='Change default logging level.')

    (opts, args) = parser.parse_args()

    assert opts.github_orgs,  parser.error('No GH orgs provided!')
    assert opts.github_token, parser.error('No GH token provided!')

    return opts, args

def main():
    (opts, args) = parse_opts()

    LOG.setLevel(opts.log_level.upper())

    gh = Github(opts.github_token)

    issues = []
    for org in opts.github_orgs:
        query = f'is:{opts.type} org:{org} assignee:{opts.user} state:{opts.state} updated:>={opts.updated}'
        LOG.debug(f'Query: {query}')
        issues.extend(
            {
                'url':      issue.html_url,
                'number':   issue.number,
                'title':    issue.title,
                'assignee': issue.assignee.login,
                'state':    issue.state,
                'updated':  str(issue.updated_at.date()),
            }
            for issue
            in gh.search_issues(query, sort='updated', order='desc')
        )

    print(json.dumps(issues, indent=2))


if __name__ == '__main__':
    main()
