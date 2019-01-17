#!/usr/bin/env python
import os
from github import Github

g = Github(os.environ['GH_TOKEN'])

org = g.get_organization('status-im')

for repo in org.get_repos():
    contents = repo.get_dir_contents('/')
    # check if repo contains package.json
    found = [f for f in contents if f.path == 'package.json']
    if len(found) > 0:
        print(repo.name)
