#!/usr/bin/env python3

import os
import sys
import github
from github import Github
from optparse import OptionParser

HELP_DESCRIPTION='This a utility for adding a team to all GitHub repos of an org.'
HELP_EXAMPLE='Example: ./add_to_private.py -o "waku-org" -u "devops"'

def parse_opts():
    parser = OptionParser(description=HELP_DESCRIPTION, epilog=HELP_EXAMPLE)
    parser.add_option('-o', '--org', default='status-im',
                      help='GitHub organization to search for repos to update.')
    parser.add_option('-t', '--team', default='devops',
                      help='GitHub team to grant access to all repos in given org.')
    parser.add_option('-p', '--perm', default='pull',
                      help='Permission to give: pull, triage, push, maintain, admin')
    parser.add_option('-T', '--token', default=os.environ['GH_TOKEN'],
                      help='GitHub API token to query for repos.')
    parser.add_option('-d', '--debug', default=False, action='store_true', 
                      help='Print debug messages for GitHub calls.')

    return parser.parse_args()

def main():
    (opts, args) = parse_opts()

    if opts.debug:
        github.enable_console_debug_logging()

    gh = Github(opts.token)

    org = gh.get_organization(opts.org)
    team = org.get_team_by_slug(opts.team)

    for repo in org.get_repos():
        skip_conditions = [
          repo.fork,
          repo.archived,
          '-ghsa-' in repo.name,
        ]

        if any(skip_conditions):
            continue

        print(' - %s' % repo.name)
        team.update_team_repository(repo, opts.perm)

if __name__ == '__main__':
    main()
