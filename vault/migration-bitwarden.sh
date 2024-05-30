#!/usr/bin/env bash


if [[ -z $VAULT_TOKEN ]]; then
  echo "Please set the varaible $VAULT_TOKEN"
  exit 1
fi
if [[ -z $VAULT_ADDR ]]; then
  echo "Please set the varaible $VAULT_ADDR"
  exit 1
fi

if [[ -z "${@}" ]]; then
    echo "Usage: migration-bitwarden.sh <bitwarden_path> <type> <vault_path>"
    echo
    echo " - bitwarden_path: path of the secret in bitwarden"
    echo " - type: type of secret (field / pwd)"
    echo " - vault_path: path of the secret in vault"
    echo 
    echo "Ex: migration-bitwarden.sh fleet/waku/test/nodekeys field"
    echo "Or"
    echo "migration-bitwarden.sh fleet/waku/test/db/nim-waku pwd"
    echo 
    exit 1
fi

BITWARDEN_PATH="$1"
TYPE="$2"
VAULT_PATH="$3"
VAULT="secret"

extract_field ()
{
  while read i; do 
    name=$(echo $i | jq -r ".name")
    value=$(echo $i | jq -r ".value")
    params="$params$name=$value "
  done < <(bw get item $BITWARDEN_PATH | jq -c '.fields[]')
}

extract_pass ()
{
  username="username=$(bw get item $BITWARDEN_PATH | jq -c '.login.username')"
  password="password=$(bw get item $BITWARDEN_PATH | jq -c '.login.password')"
  params="$username $password"
}


declare -a params

if [[ $TYPE == "field" ]]; then
  extract_field
elif [[ $TYPE == "pwd" ]]; then
  extract_pass
fi

echo "Writing Bitwarden ${TYPE} of ${BITWARDEN_PATH} into ${VAULT} of ${VAULT_PATH}"

vault kv put -mount=${VAULT} "$VAULT_PATH" $params
