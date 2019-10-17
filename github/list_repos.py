#!/usr/bin/env python3
import os
from github import Github

GH_TOKEN = os.environ['GH_TOKEN']

gh = None

def gather_clone_urls(organization, no_forks=True):
    all_repos = gh.repos.list(user=organization).all()
    for repo in all_repos:

        # Don't print the urls for repos that are forks.
        if no_forks and repo.fork:
            continue

        yield repo.clone_url

if __name__ == '__main__':
    gh = Github(GH_TOKEN)

    clone_urls = gather_clone_urls("status-im")
    for url in clone_urls:
        print(url)
