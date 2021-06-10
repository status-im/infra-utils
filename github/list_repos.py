#!/usr/bin/env python3
import os
from github import Github

GH_TOKEN = os.environ['GH_TOKEN']
GH_ORGS = ["embark-framework", "embarklabs", "vacp2p", "dap-ps", "status-im"]

gh = None

def get_repos(org, no_forks=True):
    all_repos = gh.get_user(org).get_repos('private')
    for repo in all_repos:

        # Don't print the urls for repos that are forks.
        if no_forks and repo.fork:
            continue

        yield repo

if __name__ == '__main__':
    gh = Github(GH_TOKEN)

    for org in GH_ORGS:
        for repo in get_repos(org):
            print('"{}/{}",'.format(repo.owner.login, repo.name))
