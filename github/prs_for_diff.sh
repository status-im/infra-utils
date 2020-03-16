#!/usr/bin/env bash

START=$1
STOP=$2
REPO=${3:-status-im/status-react}

GH_URL=https://api.github.com

function ghapi() {
    curl -s -H "Authorization: token ${GH_TOKEN}" $@
}

if [[ -z "${@}" ]]; then
    echo "Usage: prs_for_diff.sh release/1.0.x release/1.1.x status-im/status-react"
    exit 1
fi

if [[ -z "${GH_TOKEN}" ]]; then
    echo "No GH_TOKEN env variable set!" 1>&2
    exit 1
fi

echo "Querying ${REPO}: ${START}...${STOP}"
echo
COMMITS=$(ghapi "${GH_URL}/repos/${REPO}/compare/${START}...${STOP}" | jq -r '.commits[].sha' | sort | uniq)

for SHA in $COMMITS; do
    PR_JSON=$(ghapi "${GH_URL}/search/issues?q=repo:${REPO}+type:pr+${SHA}" | jq '.items[0]')
    if [[ -z "${PR_JSON}" ]]; then
        echo "WARNING: No PR for: ${SHA}" 1>&2
        continue;
    fi
    URL=$(echo "${PR_JSON}" | jq -r .html_url)
    TITLE=$(echo "${PR_JSON}" | jq -r .title)
    NUMBER=$(echo "${PR_JSON}" | jq -r .number)
    # format as markdown links
    echo "* [#${NUMBER}](${URL}) - ${TITLE}"
    sleep 0.8
done
