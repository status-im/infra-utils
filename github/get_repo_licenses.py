#!/usr/bin/env python3
import os
import sys
import csv
import json
from optparse import OptionParser
from github import Github, GithubException

HELP_DESCRIPTION='Utility for generating list of repos with license info.'
HELP_EXAMPLE='Example: ./get_repo_licenses.py -o status-im -o logos-co'

#GH_ORGS = ["embark-framework", "embarklabs", "vacp2p", "dap-ps", "status-im"]

def parse_opts():
    parser = OptionParser(description=HELP_DESCRIPTION, epilog=HELP_EXAMPLE)
    parser.add_option('-o', '--github-orgs', type='string', action="append",
                      help='Names of organizations to scan.')
    parser.add_option('-T', '--github-token', default=os.environ.get('GH_TOKEN', None),
                      help='GitHub API token.')
    parser.add_option('-t', '--github-repo-type', default='public',
                      help='GitHub Repository type to list.')
    parser.add_option('-d', '--csv-dialect', default='excel',
                      help='CSV dialect to use when formatting.')
    parser.add_option('-c', '--csv', action='store_true',
                      help='Generate CSV output.')

    (opts, args) = parser.parse_args()

    assert opts.github_orgs,  parser.error('No GH orgs provided!')
    assert opts.github_token, parser.error('No GH token provided!')

    return opts, args

def get_repos(gh, org, repo_type='all', no_forks=True):
    all_repos = gh.get_user(org).get_repos(repo_type)
    for repo in all_repos:

        # Don't print the urls for repos that are forks.
        if no_forks and repo.fork:
            continue

        yield repo

def main():
    (opts, args) = parse_opts()

    gh = Github(opts.github_token)

    repos = []
    for org in opts.github_orgs:
        for repo in get_repos(gh, org, repo_type=opts.github_repo_type):
            license_obj = repo.raw_data.get('license')
            license_name = None
            if license_obj is not None:
                license_name = license_obj['name']
            if license_name == 'Other':
                license_name = 'multiple licenses'
            repos.append({
                'Org': repo.owner.login,
                'Name': repo.name,
                'URL': repo.html_url,
                'License': license_name,
                'Description': repo.description,
            })

    if opts.csv:
        fieldnames = ['Org', 'Name', 'URL', 'License', 'Description']
        writer = csv.DictWriter(
            sys.stdout,
            dialect=opts.csv_dialect,
            quoting=csv.QUOTE_ALL,
            fieldnames=fieldnames
        )
        writer.writeheader()
        writer.writerows(repos)
    else:
        print(json.dumps(repos, indent=2))

if __name__ == '__main__':
    main()
