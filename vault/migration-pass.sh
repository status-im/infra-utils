#!/usr/bin/env bash
set -e
# Script to migrate secrets from password-store to vault instance
#

if [[ -z $VAULT_TOKEN ]]; then
  echo "Please set the variable $VAULT_TOKEN"
  exit 1
fi
if [[ -z $VAULT_ADDR ]]; then
  echo "Please set the variable $VAULT_ADDR"
  exit 1
fi

if [[ -z "${*}" ]]; then
    echo "Usage: migration-pass.sh <vault_path> <pass_path> <other_pass_path>"
    echo
    echo " - vault_path: path of the secret in vault"
    echo " - pass_paths: list of path to secret in the password-store, can be a directory to copy all file under it"
    echo
    echo "Ex: migration-pass.sh waku/test/nodekeys services/airflow/admin/ services/airflow/fernet-key"
    exit 1
fi

VAULT_PATH="${1}"
shift

VAULT="secret"

if [[ -z $PASSWORD_STORE_DIR ]]; then
  echo "env var PASSWORD_STORE_DIR not set, using default location ~/.password-store"
  PASSWORD_STORE_DIR=$HOME/.password-store
fi

params="{}"
for PASS_PATH in $@; do
  if [[ -f "$PASSWORD_STORE_DIR/$PASS_PATH.gpg" ]]; then
    echo "Reading file $PASS_PATH"
    field_name=$(basename $PASS_PATH)
    echo "Copying secret from $field_name"
    jq_param=".\"${field_name/./_}\"=\"$(pass $PASS_PATH)\""
    params=$(echo "${params}" | jq "${jq_param}")
  fi

  if [[ -d "$PASSWORD_STORE_DIR/$PASS_PATH" ]]; then
    echo "Reading all file in directory $PASS_PATH"
    files=$(ls "$PASSWORD_STORE_DIR/$PASS_PATH/")
    while IFS= read -r file; do
      if [[ -f "$PASSWORD_STORE_DIR/$PASS_PATH/$file" ]]; then
        echo "Copying secret from ${file}"
        field_name=${file/.gpg/}
        jq_query=".\"${field_name/./_}\"=\"$(pass $PASS_PATH/${field_name})\""
        params=$(echo $params | jq "${jq_query}")
      else
        echo "Ignoring the sub directory ${file}"
      fi
    done <<< "$files"
  fi
done

echo "$params" | vault kv put -mount=${VAULT} ${VAULT_PATH} -
