#!/usr/bin/env python3

# Source: https://github.com/threatstack/rest-api-examples

from mohawk import Sender
import requests
import os
import sys
import json

def get_or_throw(key_name):
    res = os.getenv(key_name, None)
    if res is None:
        print("Environment variable '" + key_name + "' is required.")
        sys.exit(1)
    return res


HOST = os.getenv("TS_HOST", 'api.threatstack.com')
USER_ID = get_or_throw("TS_USER_ID")
ORG_ID = get_or_throw("TS_ORG_ID")
API_KEY = get_or_throw("TS_API_KEY")

BASE_PATH = 'https://' + HOST
URI_PATH = '/v2/agents?status=online'

credentials = {
    'id': USER_ID,
    'key': API_KEY,
    'algorithm': 'sha256'
}
URL = BASE_PATH + URI_PATH
sender = Sender(credentials, URL, "GET", always_hash_content=False, ext=ORG_ID)

response = requests.get(URL, headers={'Authorization': sender.request_header})

print(json.dumps(json.loads(response.text), indent=4))
