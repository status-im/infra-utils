#!/usr/bin/env python3
import os
import logging
from github import Github
from optparse import OptionParser

HELP_DESCRIPTION='Utility for listing repos in multiple GitHub orgs.'
HELP_EXAMPLE='Example: ./list_repos.py -o status-im -o logos-co'

# Setup logging.
log_format = '[%(levelname)s] %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format)
LOG = logging.getLogger(__name__)

GH_TOKEN = os.environ['GH_TOKEN']
DEFAULT_GH_ORGS = ['Develp-GmbH', 'status-im', 'vacp2p', 'waku-org', 'logos-co', 'acid-info', 'keycard-tech']

def parse_opts():
    parser = OptionParser(description=HELP_DESCRIPTION, epilog=HELP_EXAMPLE)
    parser.add_option('-o', '--github-orgs', type='string', action='append', default=DEFAULT_GH_ORGS,
                      help='Names of organizations to scan.')
    parser.add_option('-f', '--forks', default=False, action='store_true',
                      help='Include forked repos in listing.')
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

    for org in opts.github_orgs:
        for repo in gh.get_user(org).get_repos('private'):
            # Don't print the urls for repos that are forks.
            if not opts.forks and repo.fork:
                continue

            print('{}/{}'.format(repo.owner.login, repo.name))

if __name__ == '__main__':
    main()
