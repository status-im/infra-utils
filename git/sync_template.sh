#!/usr/bin/env bash
set -e
set -x

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
    [[ "${DIR}" =~ .*/infra-(lido|utils|pass|docs|template)$ ]] && continue
    [[ -f "${DIR}/.envrc.secrets" ]] || continue
    echo "------------------------------------------------>>> ${DIR}"
    pushd "${DIR}" >/dev/null
    git checkout master
    git reset
    git status -s >/dev/null && git stash -u
    git fetch --verbose origin $(git rev-parse --abbrev-ref HEAD)
    git rebase origin/$(git rev-parse --abbrev-ref HEAD)
    for FILE in $@; do
        cp "${HOME}/work/infra-template/${FILE}" "${PWD}/${FILE}"
        git add "./${FILE}"
    done
    git status
    git commit -m "${COMMIT_MESSAGE}" && { git show --stat; git push; }
    git stash apply || true
    popd >/dev/null
done
