#!/usr/bin/env bash

# This can be easily used with something like:
# for B in $(list_old_branches.sh); do git branch --delete "${BRANCH}"; done

function getCommitUnix() {
    git show --no-patch --no-notes -s --pretty='%at' "origin/${1}" 2>/dev/null
}

function getCommitAuthorName() {
    git show --no-patch --no-notes -s --format='%an' "origin/${1}" 2>/dev/null
}

OLDER_THAN_DAYS="120"
if [[ ! -z "${1}" ]]; then
    OLDER_THAN_DAYS="${1}"
fi

CURRENT_TIME=$(date +%s)
OLDER_THAN_UNIX=$(( ${OLDER_THAN_DAYS} * 86400 ))
OLDER_THAN=$(( ${CURRENT_TIME} - ${OLDER_THAN_UNIX} ))

REMOTE="origin"
REMOTE_BRANCHES=$(git ls-remote --heads --heads ${REMOTE} | cut -f2)

for BRANCH in ${REMOTE_BRANCHES}; do
    BRANCH_NAME="${BRANCH/#refs\/heads\/}"

    if [[ ${BRANCH_NAME} =~ ^(release|gh-pages).*$ ]]; then
        continue
    fi

    COMMIT_DATE_UNIX=$(getCommitUnix $BRANCH_NAME)
    AUTHOR_NAME=$(getCommitAuthorName $BRANCH_NAME)

    if [[ -z "${COMMIT_DATE_UNIX}" ]]; then
        continue
    elif [[ ${COMMIT_DATE_UNIX} < ${OLDER_THAN} ]]; then
        printf "%-20s %s\n" "${AUTHOR_NAME}" "${BRANCH_NAME}"
    fi
done
