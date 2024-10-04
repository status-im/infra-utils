#!/usr/bin/env bash

function help() {
  echo "Usage: ./vault-migration.sh old-path new-path"
  echo "This script required env variables for ADDR, TOKEN, CA_CERT and CLIENT_CERT"
}

OLD_PATH=$1
NEW_PATH=$2

[[ "$#" -lt 2 ]] && { help; exit 1; }

echo "Moving secret from $OLD_PATH to $NEW_PATH"
vault kv get -format=json -mount=secret ${OLD_PATH} | \
  jq ".data.data" | \
  vault kv put -mount=secret ${NEW_PATH} -
