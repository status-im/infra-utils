#!/usr/bin/env python3
import os
import time
import logging
from github import Github
from optparse import OptionParser

HELP_DESCRIPTION='Utility for moving and renaming repos.'
HELP_EXAMPLE='Example: ./move_repo.py -o status-im/old-repo-name -n logos-co/new-repo-name'

# Setup logging.
log_format = '[%(levelname)s] %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format)
LOG = logging.getLogger(__name__)

def parse_opts():
    parser = OptionParser(description=HELP_DESCRIPTION, epilog=HELP_EXAMPLE)
    parser.add_option('-o', '--old', type='string',
                      help='Old name of repo.')
    parser.add_option('-n', '--new', type='string',
                      help='New name of repo.')
    parser.add_option('-t', '--team', type='string', default='devops',
                      help='Add this team to moved repo.')
    parser.add_option('-p', '--perm', type='string', default='pull',
                      help='Grant these permissions to the team.')
    parser.add_option('-T', '--github-token', default=os.environ.get('GH_TOKEN', None),
                      help='GitHub API token.')
    parser.add_option('-l', '--log-level', default='info',
                      help='Change default logging level.')

    (opts, args) = parser.parse_args()

    assert opts.github_token, parser.error('No GH token provided!')
    assert opts.old,          parser.error('No old repo name!')
    assert opts.new,          parser.error('No new repo name!')

    return opts, args

def grant_team_perms(gh, repo, team, perm):
    print('{}/{} + {}:{}'.format(repo.owner.login, repo.name, team, perm))
    org = gh.get_organization(repo.owner.login)
    team = org.get_team_by_slug(team)
    team.add_to_repos(repo)
    team.update_team_repository(repo, perm)

def main():
    (opts, args) = parse_opts()

    LOG.setLevel(opts.log_level.upper())

    gh = Github(opts.github_token)

    print('{} -> {}'.format(opts.old, opts.new))

    new_owner, new_name = opts.new.split('/')

    repo = gh.get_repo(opts.old)
    repo.transfer_ownership(new_owner=new_owner, new_name=new_name)

    # Wait for transfer to finish
    time.sleep(5)
    repo = gh.get_repo(opts.new)

    # Grant team permissions
    grant_team_perms(gh, repo, opts.team, opts.perm)
    grant_team_perms(gh, repo, 'devops', 'admin')

if __name__ == '__main__':
    main()
