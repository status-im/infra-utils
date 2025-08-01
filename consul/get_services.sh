#!/usr/bin/env bash

CONSUL_URL="${CONSUL_URL:-http://localhost:8500/v1/catalog}"
SERVICE="${1}"
shift

if [[ -z "${SERVICE}" ]]; then
    echo "USAGE: ${0} <service_name> [service_metadata_names|...]" >&2
    exit 1
fi

# Collect service metadata names
EXTRA_COLUMNS=('.ServiceMeta.version')
for NAME in ${@}; do
    EXTRA_COLUMNS+=(".ServiceMeta.\"${NAME}\"")
done

function join() { for i in "${@}"; do echo -n ", $i"; done; echo; }

readarray -t DCS < <(curl -s "${CONSUL_URL}/datacenters" | jq -r '.[]')

for DC in "${DCS[@]}"; do
    curl -s "${CONSUL_URL}/service/${SERVICE}?dc=${DC}"
done \
    | jq -r ".[] | [.Node, .ServiceName, .ServiceID$(join "${EXTRA_COLUMNS[@]}")] | @tsv" \
    | column -t
