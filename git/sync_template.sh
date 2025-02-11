#!/usr/bin/env bash
set -euo pipefail

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
    [[ "${DIR}" =~ .*/infra-(lido|utils|pass|docs|repos|template)$ ]] && continue
    [[ -f "${DIR}/.envrc.secrets" ]] || continue

    echo "------------------------------------------------>>> ${DIR}"
    if git -C "${DIR}" log --grep "${COMMIT_MESSAGE}" | grep commit >/dev/null; then
        echo "Commit already exists."
        git -C "${DIR}" status -sb
        continue
    fi
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
    if git diff --cached --quiet; then
        echo "Nothing staged."
    else
        git commit -m "${COMMIT_MESSAGE}" && { git show --stat; }
    fi

    git stash apply || true
    popd >/dev/null
done
