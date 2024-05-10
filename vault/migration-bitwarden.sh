#!/usr/bin/env bash


if [[ -z $VAULT_TOKEN ]]; then
  echo "Please set the varaible $VAULT_TOKEN"
  exit 1
fi
if [[ -z $VAULT_ADDR ]]; then
  echo "Please set the varaible $VAULT_ADDR"
  exit 1
fi

if [[ -z "${*}" ]]; then
    echo "Usage: migration-bitwarden.sh <bitwarden_path> <vault_path> <type>"
    echo
    echo " - bitwarden_path: path of the secret in bitwarden"
    echo " - vault_path: path of the secret in vault"
    echo " - type: type of secret (field / pwd), default value: pwd"
    echo 
    echo "Ex: migration-bitwarden.sh fleet/waku/test/nodekeys waku/test/nodekeys field"
    echo "Or"
    echo "migration-bitwarden.sh fleet/waku/test/db/nim-waku waku/test/db/nim-waku"
    echo 
    exit 1
fi

BITWARDEN_PATH="$1"
VAULT_PATH="$2"
TYPE="pwd"
VAULT="secret"

if [[ -n $3 ]]; then
  TYPE="$3"
fi

if [[ $TYPE == "field" ]]; then
  critera=".fields | (map({ (.name|tostring): (.value|tostring) })| add )"
elif [[ $TYPE == "pwd" ]]; then
  critera=".login | {username: .username, password: .password}"
fi

echo "Writing Bitwarden ${TYPE} of ${BITWARDEN_PATH} into ${VAULT} of ${VAULT_PATH}"
bw get item ${BITWARDEN_PATH} | jq -r "${critera}" | vault kv put -mount=${VAULT} $VAULT_PATH -
