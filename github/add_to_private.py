#!/usr/bin/env python3

import os
from github import Github
from optparse import OptionParser

HELP_DESCRIPTION='This a utility for adding accounts to private GitHub repos.'
HELP_EXAMPLE='Example: ./add_to_private.py -o "waku-org" -u "status-im-auto"'

def parse_opts():
    parser = OptionParser(description=HELP_DESCRIPTION, epilog=HELP_EXAMPLE)
    parser.add_option('-o', '--org', default='status-im',
                      help='GitHub organization to search for private repos.')
    parser.add_option('-u', '--user', default='status-im-bot',
                      help='GitHub user to grant access to private repos found.')
    parser.add_option('-p', '--perm', default='pull',
                      help='Permission to give to GitHub user to private repo.')
    parser.add_option('-t', '--token', default=os.environ['GH_TOKEN'],
                      help='GitHub API token to query for repos.')

    return parser.parse_args()

def main():
    (opts, args) = parse_opts()

    gh = Github(opts.token)

    org = gh.get_organization(opts.org)

    for repo in org.get_repos():
        skip = any([
          repo.fork,
          repo.archived,
          not repo.private,
          repo.name.endswith('-pass'),
          repo.name.contains('-ghsa-'),
        ])
        if skip:
            continue

        print(' - %s' % repo.name)
        repo.add_to_collaborators(opts.user, permission=opts.perm)

if __name__ == '__main__':
    main()
