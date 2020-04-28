#!/usr/bin/env bash

function getCommitUnix() {
    git show --no-patch --no-notes --pretty='%at' ${1}
}

OLDER_THAN_DAYS="60"
CURRENT_TIME=$(date +%s)
OLDER_THAN_UNIX=$(( ${OLDER_THAN_DAYS} * 86400 ))
OLDER_THAN=$(( ${CURRENT_TIME} - ${OLDER_THAN_UNIX} ))

REMOTE="origin"
REMOTE_BRANCHES=$(git ls-remote --heads --heads ${REMOTE} | cut -f2)

for BRANCH in ${REMOTE_BRANCHES}; do
    BRANCH_NAME="${BRANCH/#refs\/heads\/}"
    COMMIT_DATE_UNIX=$(getCommitUnix remotes/origin/$BRANCH_NAME)
    if [[ ${COMMIT_DATE_UNIX} < ${OLDER_THAN} ]]; then
        echo "${BRANCH_NAME}"
    fi
done
