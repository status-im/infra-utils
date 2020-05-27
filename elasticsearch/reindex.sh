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

function clone() {
  queryAPI POST "/${1}/_clone/${2}" '{"settings":{"index.blocks.write":null}}'
}

function read_only() {
  queryAPI PUT "/${1}/_settings" '{"settings":{"index.blocks.write":"true"}}'
}

function wait_green() {
  queryAPI GET "/_cluster/health/${1}?wait_for_status=green&timeout=9000s"
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
echo "*----------- ${old} ------------------------------"
echo "? $(printf '%-21s' ${old}) - Count: $(docs_count ${old})"
echo "? $(printf '%-21s' ${old}) - Size: $(size_in_bytes ${old}) MB"
echo "+ Creating: ${new}"
create "${new}" > /dev/null
echo "+ Reindexing: ${old} -> ${new}"
reindex "${old}" "${new}" > /dev/null
echo "? $(printf '%-21s' ${new}) - Count: $(docs_count ${new})"
echo "? $(printf '%-21s' ${new}) - Size: $(size_in_bytes ${new}) MB"
echo "! Deleting: ${old}"
delete "${old}" > /dev/null
echo "+ Cloning: ${new} -> ${old}"
read_only "${new}" > /dev/null
clone "${new}" "${old}" > /dev/null
wait_green "${old}"
echo "? $(printf '%-21s' ${old}) - Count: $(docs_count ${old})"
echo "? $(printf '%-21s' ${old}) - Size: $(size_in_bytes ${old}) MB"
echo "! Deleting: ${new}"
delete "${new}" > /dev/null
echo "*----------- ${old} ------------------------------"
