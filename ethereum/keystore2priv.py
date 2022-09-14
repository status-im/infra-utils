#!/usr/bin/env python3
import sys
import binascii
from web3.auto import w3

keystore_password = sys.argv[1]
keystore_file_path = sys.argv[2]

with open(keystore_file_path) as keyfile:
    encrypted_key = keyfile.read()
    private_key = w3.eth.account.decrypt(encrypted_key, keystore_password)

print(binascii.b2a_hex(private_key).decode('utf-8'))
