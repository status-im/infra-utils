#!/usr/bin/env python3

import os
import re
import sys
import github
from github import Github
from optparse import OptionParser

# WARNING: Calling API across orgs can result in 404 due to lack of permissions.

HELP_DESCRIPTION='This a utility for adding a team to all GitHub repos of an org.'
HELP_EXAMPLE='Example: ./add_to_private.py -o "waku-org" -u "devops"'

def parse_opts():
    parser = OptionParser(description=HELP_DESCRIPTION, epilog=HELP_EXAMPLE)
    parser.add_option('-o', '--org', default='status-im',
                      help='GitHub organization to search for repos to update.')
    parser.add_option('-t', '--team', default='devops',
                      help='GitHub team to grant access to all repos in given org.')
    parser.add_option('-u', '--user',
                      help='GitHub team to grant access to all repos in given org.')
    parser.add_option('-p', '--perm', default='pull',
                      help='Permission to give: pull, triage, push, maintain, admin')
    parser.add_option('-r', '--repos-file',
                      help='File containign list of repo names or URLs.')
    parser.add_option('-T', '--token', default=os.environ['GH_TOKEN'],
                      help='GitHub API token to query for repos.')
    parser.add_option('-d', '--debug', default=False, action='store_true',
                      help='Print debug messages for GitHub calls.')

    return parser.parse_args()

def sanitize(line):
    return re.search(r'([^/]+?)/([^/]+?)$', line)[0].removesuffix('.git')

def main():
    (opts, args) = parse_opts()

    if opts.debug:
        github.enable_console_debug_logging()

    gh = Github(opts.token)

    if opts.repos_file and os.path.isfile(opts.repos_file):
        repos = []
        with open(opts.repos_file, 'r') as f:
            for line in f.readlines():
                try:
                    repos.append(gh.get_repo(sanitize(line)))
                except Exception as ex:
                    print(f'Failed to parse: {line}')
                    sys.exit(1)
    else:
        org = gh.get_organization(opts.org)
        repos = org.get_repos()

    for repo in repos:
        skip_conditions = [
          repo.fork,
          repo.archived,
          '-ghsa-' in repo.name,
        ]

        if any(skip_conditions):
            continue

        print(' - %s/%s' % (repo.organization.login, repo.name))
        if opts.user:
            repo.add_to_collaborators(opts.user, permission=opts.perm)
        else:
            org = gh.get_organization(repo.organization.login)
            try:
                team = org.get_team_by_slug(opts.team)
            except Exception as ex:
                print(f'No "{opts.team}" team in "{org.login}" GH org.')
                sys.exit(1)

            # Skip changing permissions if team is already there.
            if team in repo.get_teams():
                continue

            team.update_team_repository(repo, opts.perm)

if __name__ == '__main__':
    main()
