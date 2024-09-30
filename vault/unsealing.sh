#!/usr/bin/env bash

CONSUL_URL="${CONSUL_URL:-http://localhost:8500/v1/catalog}"

ENV_VARS="VAULT_CACERT VAULT_CLIENT_CERT VAULT_CLIENT_KEY CONSUL_HTTP_TOKEN"

function help() {
  echo "This script check if all Vault instances are unsealed."
  echo "To unseal the host, add the parameter unseal"
  echo "Example ./$@ unseal"
  echo "The following variables needs to be set:"
  for VAR in $ENV_VARS; do
    echo "- $VAR"
  done
}

for VAR in $ENV_VARS; do
  if [[ ! -v $VAR ]]; then
    help
    exit 1
  fi
done

unseal=0
if [[ $# == 1 && $1 == "unseal" ]]; then
  unseal=1
fi

vault_addr=""
echo "Fetching Vault address from Consul"
readarray -t DCS < <(curl -s "${CONSUL_URL}/datacenters" | jq -r '.[]')
for DC in "${DCS[@]}"; do
    vault_addr=$(echo $vault_addr $(curl -s "${CONSUL_URL}/service/vault?dc=${DC}" | jq -r '.[].Node'))
done

echo $vault_addr

for addr in $vault_addr; do
  export VAULT_ADDR="https://$addr.status.im:8200"
  status=$(vault status -format=json| jq -r ".sealed")
  echo "Vault on $addr is $([ "$status" == 'false' ] && echo 'unsealed' || echo 'sealed')"
  if [[ $status == "true" && $unseal == 1 ]]; then
    echo "Unsealing the host $addr"
    vault operator unseal
  fi
done
