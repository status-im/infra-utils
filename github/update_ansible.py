#!/usr/bin/env python3
# I could use yaml module, but it fucks ups the order and formatting.
import re
from os.path import isdir, expanduser
from subprocess import check_output

path = 'ansible/requirements.yml'

with open(path, 'r') as f:
    contents = f.readlines()

# Read file
lines = iter(contents) 
entries = []
for line in lines:
    matches = re.match('- name: (.*)', line)
    if not matches:
        continue
    name = matches.group(1)

    matches = re.match('  src: (.*)', next(lines))
    if not matches:
        raise Exception('Unable to find source URL: %s' % name)
    src = matches.group(1)

    matches = re.match('^git@github.com:[^/]+/(.+).git$', src)
    if not matches:
        raise Exception('Unable to find full repo name: %s' % name)
    full_name = matches.group(1)

    matches = re.match('  version: (.*)', next(lines))
    if not matches:
        raise Exception('Unable to find current version: %s' % name)
    version = matches.group(1)

    matches = re.match('  scm: (.*)', next(lines))
    if not matches:
        raise Exception('Unable to find version control type: %s' % name)
    scm = matches.group(1)

    entries.append({
        'name': name,
        'full_name': full_name,
        'src': src,
        'version': version,
        'scm': scm,
    })

# Read commits from repos
for entry in entries:
    cwd = expanduser('~/work/%s' % entry['full_name'])
    if not isdir(cwd):
        print('No such repo: %s' % cwd)
        continue
    commit = check_output(['git', 'rev-parse', 'HEAD'], cwd=cwd)
    new_version = commit.decode().strip()
    if new_version != entry['version']:
        entry['version'] = new_version
        print('Updated: %s - %s' % (new_version, entry['full_name']))

lines = ['---\n']
for entry in entries:
    lines.extend([
        ('- name: %s\n'    % entry['name']),
        ('  src: %s\n'     % entry['src']),
        ('  version: %s\n' % entry['version']),
        ('  scm: %s\n'     % entry['scm']),
        '\n',
    ])


# Write file
with open(path, 'w') as f:
    contents = f.writelines(lines[:-1])
