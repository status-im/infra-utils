#!/usr/bin/env bash

# This can be easily used with something like:
# for B in $(list_old_branches.sh); do git branch --delete "${BRANCH}"; done

function getCommitUnix() {
    git show --no-patch --no-notes --pretty='%at' ${1}
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
    if [[ ${BRANCH_NAME} = release* ]]; then
        continue
    fi
    COMMIT_DATE_UNIX=$(getCommitUnix remotes/origin/$BRANCH_NAME)
    if [[ ${COMMIT_DATE_UNIX} < ${OLDER_THAN} ]]; then
        echo "${BRANCH_NAME}"
    fi
done
