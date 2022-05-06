#!/usr/bin/env python
import os
import sys
from github import Github

g = Github(os.environ['GH_TOKEN'])
org = g.get_organization('status-im')
team = org.get_team_by_slug(sys.argv[1])
print(team)
