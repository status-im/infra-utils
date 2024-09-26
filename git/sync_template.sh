#!/usr/bin/env bash

function help() {
    echo 'Usage: ./sync_template.sh "my commit message" file/to/copy another/file/to/copy ...'
}

[[ "$#" -lt 2 ]] && { help; exit 1; }

# First argument is the message
COMMIT_MESSAGE="${1}"
shift

for DIR in $(ls -d ~/work/infra-*); do
    [[ "${DIR}" =~ .*/infra-role-.*$ ]] && continue
    [[ "${DIR}" =~ .*/infra-tf-.*$ ]] && continue
    [[ "${DIR}" =~ .*/infra-wazuh-.*$ ]] && continue
    [[ "${DIR}" =~ .*/infra-(lido|utils|pass|template)$ ]] && continue
    echo '---------------------------------'
    pushd "${DIR}"
    git reset
    git stash -u
    git fetch --verbose origin $(git rev-parse --abbrev-ref HEAD)
    git rebase origin/$(git rev-parse --abbrev-ref HEAD)
    for FILE in $@; do
        cp "${HOME}/work/infra-template/${FILE}" "./${FILE}"
        git add "./${FILE}"
    done
    git commit -m "${COMMIT_MESSAGE}"
    git push
    git stash apply
    popd
done
