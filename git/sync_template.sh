#!/usr/bin/env bash
set -euo pipefail

function help() {
    echo 'Usage: ./sync_template.sh [-p] "my commit message" file/to/copy another/file/to/copy ...'
}

[[ "$#" -lt 2 ]] && { help; exit 1; }
GIT_PUSH=0
if [[ "$1" == '-p' ]]; then
    GIT_PUSH=1
    shift
fi

STASHED=0
# First argument is the message
COMMIT_MESSAGE="${1}"
shift

for DIR in $(ls -d ~/work/infra-*); do
    [[ "${DIR}" =~ .*/infra-role-.*$ ]] && continue
    [[ "${DIR}" =~ .*/infra-tf-.*$ ]] && continue
    [[ "${DIR}" =~ .*/infra-(lido|utils|pass|docs|repos|template)$ ]] && continue
    [[ -f "${DIR}/.envrc.secrets" ]] || continue

    echo "------------------------------------------------>>> ${DIR}"
    if git -C "${DIR}" log --grep "${COMMIT_MESSAGE}" | grep commit >/dev/null; then
        echo "Commit already exists."
        git -C "${DIR}" status -sb
        [[ "${GIT_PUSH}" -eq 1 ]] && git -C "${DIR}" push
        continue
    fi
    pushd "${DIR}" >/dev/null

    git checkout master
    git reset
    if git status -s >/dev/null; then
        git stash -u && STASHED=1
    fi
    git fetch --verbose origin $(git rev-parse --abbrev-ref HEAD)
    git rebase origin/$(git rev-parse --abbrev-ref HEAD)

    for FILE in $@; do
        cp "${HOME}/work/infra-template/${FILE}" "${PWD}/${FILE}"
        git add "./${FILE}"
    done

    git status
    if git diff --cached --quiet; then
        echo "Nothing staged."
    else
        git commit -m "${COMMIT_MESSAGE}" && { git show --stat; }
    fi

    if [[ "${STASHED}" -eq 1 ]]; then
        git stash apply || echo "MERGE CONFLICTS!"
    fi
    popd >/dev/null
done
