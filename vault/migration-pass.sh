#!/usr/bin/env bash

# Script to migrate secrets from password-store to vault instance

if [[ -z $VAULT_TOKEN ]]; then
  echo "Please set the varaible $VAULT_TOKEN"
  exit 1
fi
if [[ -z $VAULT_ADDR ]]; then
  echo "Please set the varaible $VAULT_ADDR"
  exit 1
fi

if [[ -z "${*}" ]]; then
    echo "Usage: migration-pass.sh <bitwarden_path> <vault_path>"
    echo
    echo " - password_store_path: path of the secret in bitwarden"
    echo " - vault_path: path of the secret in vault"
    echo 
    echo "Ex: migration-pass.sh fleet/waku/test/nodekeys waku/test/nodekeys"
    echo "Or"
    echo "migration-pass.sh fleet/waku/test/db/nim-waku waku/test/db/nim-waku"
    echo 
    exit 1
fi

BITWARDEN_PATH="$1"
VAULT_PATH="$2"

if [[ -n $PASSWORD_STORE_DIR ]]; then
  echo "env var PASSWORD_STORE_DIR not set, using default location ~/.password-store"
  PASSWORD_STORE_DIR=$HOME/.password-store/
fi

declare -a params

if [[ ! -f "$PASSWORD_STORE_DIR/$VAULT_PATH" ]]; then
  # Extract last part of the path, push into a 
  params="$name=$(pass VAULT_PATH)"
fi
