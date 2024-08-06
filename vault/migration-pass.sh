#!/usr/bin/env bash

# Script to migrate secrets from password-store to vault instance
#

if [[ -z $VAULT_TOKEN ]]; then
  echo "Please set the varaible $VAULT_TOKEN"
  exit 1
fi
if [[ -z $VAULT_ADDR ]]; then
  echo "Please set the varaible $VAULT_ADDR"
  exit 1
fi

if [[ -z "${*}" ]]; then
    echo "Usage: migration-pass.sh <pass_path> <vault_path>"
    echo
    echo " - pass_path: path of the secret in the password-store"
    echo " - vault_path: path of the secret in vault"
    echo 
    echo "Ex: migration-pass.sh fleet/waku/test/nodekeys waku/test/nodekeys"
    echo "Or"
    echo "migration-pass.sh fleet/waku/test/db/nim-waku waku/test/db/nim-waku"
    echo 
    exit 1
fi

PASS_PATH="$1"
VAULT_PATH="$2"
VAULT="secret"

if [[ -z $PASSWORD_STORE_DIR ]]; then
  echo "env var PASSWORD_STORE_DIR not set, using default location ~/.password-store"
  PASSWORD_STORE_DIR=$HOME/.password-store
fi

declare -a params


if [[ -f "$PASSWORD_STORE_DIR/$PASS_PATH.gpg" ]]; then
  echo "Reading file $PASS_PATH"
  field_name=$(basename $PASS_PATH)
  echo $field_name
  jq_param=".\"${field_name/./_}\"=\"$(pass $PASS_PATH)\""
  echo $jq_param
  params=$(echo "{}" | jq "${jq_param}")
fi


if [[ -d "$PASSWORD_STORE_DIR/$PASS_PATH" ]]; then
  echo "Reading all file in directory $PASS_PATH"
  params="{}"
  files=$(ls "$PASSWORD_STORE_DIR/$PASS_PATH/")
  while IFS= read -r file; do
    echo "File name ${file}"
    if [[ -f "$PASSWORD_STORE_DIR/$PASS_PATH/$file" ]]; then
      field_name=${file/.gpg/}
      jq_query=".\"${field_name/./_}\"=\"$(pass $PASS_PATH/${field_name})\""
      echo 
      #echo ${jq_query/\n/\\n}
      echo 
      params=$(echo $params | jq "${jq_query}")
    fi
    echo
    echo "params: $params"
  done <<< "$files"
fi

echo "$params" | vault kv put -mount=${VAULT} ${VAULT_PATH} -
