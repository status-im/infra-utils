#!/usr/bin/env python3
import os
from github import Github

gh = Github(os.environ['GH_TOKEN'])

org = gh.get_organization('status-im')

#print("Scopes:", gh.oauth_scopes)

for repo in org.get_repos():
    skip = any([
      repo.fork,
      repo.archived,
      not repo.private,
      repo.name.endswith('-pass'),
    ])
    if skip:
        continue

    print(repo)
    repo.add_to_collaborators('status-im-auto', permission='pull')
