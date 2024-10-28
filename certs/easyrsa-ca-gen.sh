#! /usr/bin/env nix-shell
#! nix-shell -i bash -p easyrsa openssl
set -x
set -e
export CN='devops@example.org'
export SANS='DNS:*.example.com,DNS:*.example.org'
export EASYRSA_BATCH=1
# Certificate Authority Private Key Password
export CA_PASS="${CA_PASS:-changeMeIfYouCare}"
export CLIENT_PASS="${CLIENT_PASS:-changeMeIfYouCare}"
export EASYRSA_PASSIN="pass:${CA_PASS}"

# Initializa PKI files
easyrsa init-pki
# PKI init config
cat > pki/vars << EOF
set_var EASYRSA_DN          "cn_only"
set_var EASYRSA_CA_EXPIRE   36500
set_var EASYRSA_CERT_EXPIRE 1825
EOF
# Create Certificate Authority
EASYRSA_PASSOUT="pass:${CA_PASS}" \
easyrsa --req-cn="${CN}" build-ca
# Create Server Certificate
easyrsa --san="${SANS}" build-server-full server nopass
# Create Client Certificate
easyrsa build-client-full client nopass
# Certificate Revoke List
easyrsa gen-crl
# Combine client certificate and key
openssl pkcs12 -export \
    -out client.p12 \
    -passin "pass:${CA_PASS}" \
    -passout "pass:${CLIENT_PASS}" \
    -inkey pki/private/client.key \
    -in pki/issued/client.crt \
    -certfile pki/ca.crt
