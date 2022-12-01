#!/usr/bin/env python
import os
from github import Github
from optparse import OptionParser

HELP_DESCRIPTION='Utility for copying members from one GH org to another.'
HELP_EXAMPLE='Example: ./copy_members.py -i status-im -o logos-co'

def parse_opts():
    parser = OptionParser(description=HELP_DESCRIPTION, epilog=HELP_EXAMPLE)
    parser.add_option('-i', '--input-org',
                      help='GitHub organization to get members from.')
    parser.add_option('-o', '--output-org',
                      help='GitHub organization to add members to.')
    parser.add_option('-t', '--teams', type='string', action="append",
                      help='Names of teams to copy over. If not given: all.')
    parser.add_option('-d', '--dry-run', action='store_true',
                      help='Do not add any members, just print.')
    parser.add_option('-T', '--token', default=os.environ['GH_TOKEN'],
                      help='GitHub API token to query for repos.')

    (opts, args) = parser.parse_args()

    assert opts.input_org,  parser.error('No input org name given!')
    assert opts.output_org, parser.error('No output org name given!')

    return opts, args

def main():
    (opts, args) = parse_opts()

    g = Github(os.environ['GH_TOKEN'])

    in_org = g.get_organization(opts.input_org)
    out_org = g.get_organization(opts.output_org)

    invitations = [i.login for i in out_org.invitations()]

    for team in in_org.get_teams():
        print(' --- Team: %s' % team.slug)
        if opts.teams is None or team.name in opts.teams or team.slug in opts.teams:
            for member in team.get_members():
                    if out_org.has_in_members(member):
                        print('%s already a member' % member.login)
                    elif member.login in invitations:
                        print('%s already invited' % member.login)
                    else:
                        if not opts.dry_run:
                            out_org.add_to_members(member, role='member')
                        print('%s added to members' % member.login)

if __name__ == '__main__':
    main()
