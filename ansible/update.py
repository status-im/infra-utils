#!/usr/bin/env python3
# I could use yaml module, but it fucks ups the order and formatting.
import re
from os import getenv
from os.path import isdir, expanduser
from subprocess import check_output

path = 'ansible/requirements.yml'
repos_path = getenv('ANSIBLE_REPOS_PATH', '~/work')

def extractKeyValue(line, keys):
    for key in keys:
        matches = re.match(('[- ] %s: (.*)' % key), line)
        if not matches:
            continue
        else:
            return (key, matches.group(1))

    return (None, None)

with open(path, 'r') as f:
    contents = f.readlines()

# Read file
lines = iter(contents) 
entries = []
entry = {}
keys_possible = ['name', 'src', 'version', 'scm']

for line in lines:
    if line.strip() == '---':
        continue

    key, value = extractKeyValue(line, keys_possible)

    if key is None:
        entries.append(entry.copy())
    else:
        entry[key] = value

# Append last entry due to lack of last newline.
entries.append(entry)

# Read commits from repos
for entry in entries:
    matches = re.match('^git@github.com:[^/]+/(.+).git$', entry['src'])
    if not matches:
        raise Exception('Unable to find full repo name: %s' % name)
    entry['full_name'] = matches.group(1)

    cwd = expanduser('%s/%s' % (repos_path, entry['full_name']))
    if not isdir(cwd):
        print('No such repo: %s' % cwd)
        continue

    commit = check_output(['git', 'rev-parse', 'HEAD'], cwd=cwd)
    new_version = commit.decode().strip()
    if entry.get('version') is None:
        print('untrack: %s - %s' % (new_version, entry['full_name']))
    elif new_version != entry['version']:
        entry['version'] = new_version
        print('UPDATED: %s - %s' % (new_version, entry['full_name']))
    else:
        print('current: %s - %s' % (new_version, entry['full_name']))

lines = ['---\n']
for entry in entries:
    lines.extend([
        ('- name: %s\n'    % entry['name']),
        ('  src: %s\n'     % entry['src']),
        ('  version: %s\n' % entry['version']) if entry.get('version') else None,
        ('  scm: %s\n'     % entry['scm']),
        '\n',
    ])

# remove empty lines
lines = list(filter(lambda l: l is not None, lines))

# write file
with open(path, 'w') as f:
    contents = f.writelines(lines[:-1])
