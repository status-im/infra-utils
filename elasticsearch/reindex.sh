#!/usr/bin/env bash

set -e
#set -x

function queryAPI() {
  method=$1
  path=$2
  data=$3
  cmd="curl -s -X${method} http://localhost:9200/${path}"
  if [[ -n "${data}" ]]; then
    cmd+=" -f -H 'content-type:application/json' -d '${data}'"
  fi
  eval "${cmd}"
}

function create() {
  queryAPI PUT "${1}" '{"settings":{"number_of_replicas":1,"number_of_shards": 1}}'
}

function reindex() {
  queryAPI POST "_reindex" "{\"source\":{\"index\":\"${1}\"},\"dest\":{\"index\":\"${2}\"}}"
}

function delete() {
  queryAPI DELETE "${1}"
}

function stats() {
  queryAPI GET "${1}/_stats"
}

function docs_count() {
  stats "${1}" | jq '._all.primaries.docs.count'
}

function size_in_bytes() {
  stats "${1}" | jq '._all.primaries.store.size_in_bytes / (1000*1000) | floor'
}

index="$1"
if [[ -z "${index}" ]]; then
  echo "First argument has to be an index name!"
  exit 1
fi

old="${index}"
new="${index}-re"
echo "*------ ${old} -----------------------------------"
echo "? $(printf '%-14s' ${old}) - Count: $(docs_count ${old})"
echo "? $(printf '%-14s' ${old}) - Size: $(size_in_bytes ${old}) MB"
echo "+ Creating: ${new}"
create "${new}"
echo "+ Reindexing: ${old} -> ${new}"
reindex "${old}" "${new}"
echo "? $(printf '%-14s' ${new}) - Count: $(docs_count ${new})"
echo "? $(printf '%-14s' ${new}) - Size: $(size_in_bytes ${new}) MB"
echo "! Deleting: ${old}"
delete "${old}"
echo "+ Re-Reindexing: ${new} -> ${old}"
reindex "${new}" "${old}"
echo "? $(printf '%-14s' ${old}) - Count: $(docs_count ${old})"
echo "? $(printf '%-14s' ${old}) - Size: $(size_in_bytes ${old}) MB"
echo "! Deleting: ${new}"
delete "${new}"
echo "*------ ${old} -----------------------------------"
