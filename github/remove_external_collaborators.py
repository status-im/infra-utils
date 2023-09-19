#!/usr/bin/env python3

import os
import re
from github import Github
from optparse import OptionParser

HELP_DESCRIPTION='Utility for listing external collaboraeors in GitHub repos.'
HELP_EXAMPLE='Example: ./external_collaborators.py -o "waku-org"'

def parse_opts():
    parser = OptionParser(description=HELP_DESCRIPTION, epilog=HELP_EXAMPLE)
    parser.add_option('-o', '--org', default='status-im',
                      help='GitHub organization to search for private repos.')
    parser.add_option('-r', '--regex', default=None,
                      help='Regex to limit which collaborators get removed.')
    parser.add_option('-t', '--token', default=os.environ['GH_TOKEN'],
                      help='GitHub API token to query for repos.')
    parser.add_option('-p', '--private', default=False, action='store_true',
                      help='Check only private repositories.')
    parser.add_option('-d', '--dry-run', default=False, action='store_true',
                      help='Dry run. Only listing repos.')

    return parser.parse_args()

def main():
    (opts, args) = parse_opts()

    gh = Github(opts.token)

    org = gh.get_organization(opts.org)

    for repo in org.get_repos():
        skip = any([
          repo.fork,
          repo.archived,
          repo.name in ['process-models', 'infra-spiff-workflow', 'nim-raft', 'nim-eth-verkle'],
          '-ghsa-' in repo.name,
        ])
        if skip:
            continue
        if opts.private and not repo.private:
            continue

        for collaborator in repo.get_collaborators('outside'):
            if opts.regex and not re.search(opts.regex, collaborator.login):
                continue

            print('%30s - %s' % (repo.name, collaborator.login))

            if opts.dry_run:
                continue

            repo.remove_from_collaborators(collaborator)

if __name__ == '__main__':
    main()
