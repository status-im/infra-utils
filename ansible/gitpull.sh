#!/usr/bin/env bash
set -e

for DIR in ~/work/infra-*; do
    pushd $DIR >/dev/null
    NAME=$(basename $DIR)
    BRANCH=$(git rev-parse --abbrev-ref HEAD)
    if [[ "${BRANCH}" != "master" ]]; then
        printf "%-30s - %s\n" "$NAME" "FEATURE"
    elif git diff --quiet; then
        git pull origin master >/dev/null 2>&1
        printf "%-30s - %s\n" "$NAME" "UPDATED"
    else
        printf "%-30s - %s\n" "$NAME" "DIRTY"
        git status
    fi
    popd >/dev/null
done
