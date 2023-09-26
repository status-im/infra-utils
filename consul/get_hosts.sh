#!/usr/bin/env bash

CONSUL_URL="${CONSUL_URL:-http://localhost:8500/v1/catalog}"

readarray -t DCS < <(curl -s "${CONSUL_URL}/datacenters" | jq -r '.[]')

for DC in "${DCS[@]}"; do
    echo "# DC: ${DC}"
    curl -s "${CONSUL_URL}/nodes?dc=${DC}" \
        | jq -r '.[] | [.Address, .Node, .Meta.os] | @tsv'
done
