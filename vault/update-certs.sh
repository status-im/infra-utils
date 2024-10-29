#!/usr/bin/env bash


# This script update the Vault certificate in infra-pass after some DNS or IP modification.
# It only change the certificate used for TLS and for Cluster communication.
#
# For more information on the certificate generation, refer to https://docs.infra.status.im/vault/certificate_generation.html

WORKSPACE="/tmp/vault-certs"
CONFIG_PATH="${HOME}/work/infra-docs/docs/vault/files"

echo "Generating the workspace"
mkdir $WORKSPACE


echo "Copying the exising keys and certificate"

# pass services/vault/certs/root-ca/cert > ${WORKSPACE}/ca.crt
# pass services/vault/certs/root-ca/privkey > ${WORKSPACE}/ca.key
# pass services/vault/certs/client-ca/cert > ${WORKSPACE}/client-ca.crt
# pass services/vault/certs/client-ca/privkey > ${WORKSPACE}/client-ca.key
# pass services/vault/certs/tls/privkey > ${WORKSPACE}/server.key
# pass services/vault/certs/client-cluster/privkey > ${WORKSPACE}/client-cluster.key


echo "Generating the new Server TLS certificate"

openssl req -new \
  -key "${WORKSPACE}/server.key" \
  -out "${WORKSPACE}/server.csr" \
  -config "${CONFIG_PATH}/server-cert.cnf"

openssl x509 -req -days 365 \
    -in "${WORKSPACE}/server.csr" \
    -CA "${WORKSPACE}/ca.crt" \
    -CAkey "${WORKSPACE}/ca.key" \
    -CAcreateserial \
    -out "${WORKSPACE}/server.crt" \
    -extfile "${CONFIG_PATH}/server-cert.cnf" \
    -extensions req_ext

echo "Generating the new Client Cluster Certificate"

openssl req -new \
  -key "${WORKSPACE}/client-cluster.key" \
  -out "${WORKSPACE}/client-cluster.csr" \
  -config "${CONFIG_PATH}/client-cluster.cnf"

openssl x509 -req -days 365 \
    -in "${WORKSPACE}/client-cluster.csr" \
    -CA "${WORKSPACE}/client-ca.crt" \
    -CAkey "${WORKSPACE}/client-ca.key" \
    -CAcreateserial -out "${WORKSPACE}/client-cluster.crt" \
    -extfile "${CONFIG_PATH}/client-cluster.cnf" \
    -extensions req_ext

echo "Updating infra-pass"
cat ${WORKSPACE}/server.crt | pass insert services/vault/certs/tls/cert -m
cat ${WORKSPACE}/client-cluster.crt | pass insert services/vault/certs/client-cluster/cert -m

echo "Clean up the workspace"
rm -rf ${WORKSPACE}
