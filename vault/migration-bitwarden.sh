#!/usr/bin/env bash
set -e

if [[ -z $VAULT_TOKEN ]]; then
  echo "Please set the variable VAULT_TOKEN">&2
  exit 1
fi
if [[ -z $VAULT_ADDR ]]; then
  echo "Please set the variable VAULT_ADDR" >&2
  exit 1
fi

if [[ -z "${*}" ]]; then
    echo "Usage: migration-bitwarden.sh <vault_path> <bitwarden_path> <bitwarden_path> <bitwarden_path>"
    echo
    echo " - vault_path: path of the secret in vault"
    echo " - bitwarden_path: list of path of secrets in bitwarden"
    echo
    echo "Example:"
    echo " - migration-bitwarden.sh path/in/vault secret/in/bitwarden"
    echo " - migration-bitwarden.sh path/in/vault secret/in/bitwarden other/secret/in/bitwarden"
    echo
    exit 1
fi

VAULT_PATH="$1"
shift
VAULT="secret"
params={}
for BW_PATH in $@; do
  echo "Reading secret from $BW_PATH"
  object=$(bw get item ${BW_PATH})
  notes=$(echo $object | jq -r '.notes')

  if [[ $notes == *"Migrated to Vault"* ]]; then
    echo "Secret already migrated"
    exit 0
  fi

  if [[ $(echo $object | jq -e 'has("fields")') == true ]]; then
    echo " - Reading fields groups"
    critera=".fields | (map({ (.name|tostring): (.value|tostring) })| add )"
    tmp=$(echo "${object}" | jq -r "${critera}")
    params=$(echo "${params} ${tmp}" | jq -s add)
  fi
  if [[ $(echo $object | jq -e 'has("login")') == true ]]; then
    echo " - Reading login groups"
    critera=".login | {username: .username, password: .password}"
    tmp=$(echo "${object}" | jq -r "${critera}")
    params=$(echo "${params} ${tmp}" | jq -s add)
  fi
done
echo "${params}" | vault kv put -mount=${VAULT} $VAULT_PATH -


# Notes update to indicate password migration
for BW_PATH in $@; do
  object=$(bw get item ${BW_PATH})
  notes=$(echo $object | jq -r '.notes')
  # Update notes
  timestamp=$(date +%F)
  jq_note=".notes=\"${notes} Migrated to Vault - ${timestamp}\""
  echo ${object} | jq "$jq_note" | bw encode | bw edit item $(echo $object | jq -r '.id')
done
