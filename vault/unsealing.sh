#!/usr/bin/env bash
set -Euo pipefail

CONSUL_HOST="${CONSUL_HOST:-localhost}"
CONSUL_PORT="${CONSUL_PORT:-8500}"
CONSUL_URL="http://${CONSUL_HOST}:${CONSUL_PORT}/v1/catalog"

function help() {
  echo "This script check if all Vault instances are unsealed."
  echo "To unseal the host, add the parameter unseal"
  echo "Example ./$@ unseal"
  echo "The following variables needs to be set:"
  for VAR in $ENV_VARS; do
    echo "- $VAR"
  done
}

ENV_VARS="VAULT_CACERT VAULT_CLIENT_CERT VAULT_CLIENT_KEY CONSUL_HTTP_TOKEN"
# Fail on missing variables
for VAR in $ENV_VARS; do
  [[ ! -v $VAR ]] && { help; exit 1; }
done

# Verfy Consul API is available.
nc -z "${CONSUL_HOST}" "${CONSUL_PORT}" 2>/dev/null \
    || { echo "ERROR: Setup SSH tunnel to Consul ${CONSUL_PORT} port!" >&2; exit 1; }

# Prompt for shard unseal key if unseal argument is used.
unseal_key=''
if [[ $# == 1 && $1 == "unseal" ]]; then
  read -s -p "Provide unseal shard key: " unseal_key
fi

# Fetching Vault address from Consul
vault_addr=""
readarray -t DCS < <(curl -s "${CONSUL_URL}/datacenters" | jq -r '.[]')
for DC in "${DCS[@]}"; do
    vault_addr="${vault_addr} $(curl -s "${CONSUL_URL}/service/vault?dc=${DC}" | jq -r '.[].Node')"
done

# Calling each Vault to get status
result='[]'
for addr in ${vault_addr}; do
  export VAULT_ADDR="https://${addr}.status.im:8200"

  status=$(vault status -format=json)
  elt=$(echo $status | jq -r "{hostname:\"$addr\",sealed:.sealed,progress:.progress}")
  result=$(echo "${result}" | jq ".+=[${elt}]")
  sealed=$(echo "${status}" | jq -r ".sealed")

  if [[ "${sealed}" == "true" ]] && [[ -n "${unseal_key}" ]]; then
    echo "Unsealing the host ${addr}"
    vault operator unseal "${unseal_key}"
  fi
done

echo "Vaults status"
echo ""
echo "$result" \
    | jq -r '.[] | [.hostname, .sealed, .progress] | @csv' \
    | column -s, -t -N Hostname,Sealed,Progress \
    | sed -e 's,false,\x1b[32m&\x1b[0m,' -e 's,true,\x1b[31m&\x1b[0m,'
