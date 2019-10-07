#!/usr/bin/env bash

# This script is a helper for when dependabot makes too many fucking PRs

# first argument is the branch name
branch="${1}"
shift

# start with a new branch
git checkout -b "${branch}"
git commit --no-verify --allow-empty -m "combined prs"

# rest of the arguments should be PR numbers
for pr_id in "${@}"; do
    echo "Including: #${pr_id}"
    git fetch origin "pull/${pr_id}/head:pr-${pr_id}"
    git merge --squash "pr-${pr_id}"
    git commit --no-verify --amend --no-edit .
done
