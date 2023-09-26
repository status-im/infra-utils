#!/usr/bin/env bash

CONSUL_URL="${CONSUL_URL:-http://localhost:8500/v1/catalog}"
SERVICE="${1}"

[[ -z "${SERVICE}" ]] && { echo "No service name given!" >&2; exit 1; }

readarray -t DCS < <(curl -s "${CONSUL_URL}/datacenters" | jq -r '.[]')

for DC in "${DCS[@]}"; do
    curl -s "${CONSUL_URL}/service/${SERVICE}?dc=${DC}"
done \
    | jq -r '.[] | [.Node, .ServiceName, .ServiceID, .ServiceMeta.version] | @tsv' \
    | column -t
