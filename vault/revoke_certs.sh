#!/usr/bin/env bash
set -euo pipefail

# Usage: revoke_certs.sh hq.logs.wg

REVOKE=false

[[ "${1:-}" =~ ^(-r|--revoke)$ ]] && { REVOKE=true; shift; }
REGEX="${1:?regex required}"

vault list -format=json "pki/certs" | jq -r '.[]' |
while read -r SERIAL; do
    CERT_PEM="$(vault read -field=certificate "pki/cert/$SERIAL")"
    COMMON_NAME="$(openssl x509 -noout -subject -nameopt RFC2253 <<<"$CERT_PEM" |
          sed 's/^subject=//; s/.*CN=\([^,]*\).*/\1/')"

    [[ "$COMMON_NAME" =~ $REGEX ]] || continue

    if $REVOKE; then
        vault write "pki/revoke" serial_number="$SERIAL" >/dev/null
        echo "REVOKED $COMMON_NAME $SERIAL"
    else
        echo "MATCH   $COMMON_NAME $SERIAL"
    fi
done
