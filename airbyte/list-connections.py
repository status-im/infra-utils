#!/usr/bin/env python
import os
import logging
import requests
import json

# Setup logging.
log_format = '[%(levelname)s] %(message)s'
logging.basicConfig(level=logging.INFO, format=log_format)
log = logging.getLogger(__name__)

DESCRIPTION = '''
    This script list all connections in an Airbyte instance.
'''

AIRBYTE_URL="http://localhost:8101"

headers= {
    'Content-type': 'application/json'
  }

class Connection:
    def __init__(self, name, sourceId, destId, namespace, prefix, status, schedule):
        self.name = name
        self.sourceId = sourceId
        self.sourceName = ""
        self.destId = destId
        self.destName = ""
        self.namespace = namespace
        self.prefix = prefix
        self.status = status
        self.schedule = schedule

    def __str__(self):
        return f"| {self.name} | {self.sourceName} | {self.destName} | {self.namespace} | {self.prefix} | {self.status} | {self.schedule} |"
class Airbyte:

    def __init__(self, url):
        self.url = url
        self.workspace = "0"

    def call_api(self, endpoint, data: str=""):
        resp = requests.post(f"{self.url}/{endpoint}", headers=headers, data=data)
        log.debug("resp %s", resp)
        return resp.json()

    def get_workspace_id(self):
        workspaces = self.call_api('api/v1/workspaces/list')
        workspace_id = workspaces['workspaces'][0]['workspaceId']
        self.workspace = workspace_id
        return workspace_id

    def list_connections(self):
        _connections =self.call_api('api/v1/connections/list', data=json.dumps({"workspaceId": self.workspace}))
        connections = []
        for _con in _connections.get('connections'):
            try:
                connection = Connection(
                    _con.get('name'),
                    _con.get('sourceId'),
                    _con.get('destinationId'),
                    _con.get('namespaceFormat'),
                    _con.get('prefix'),
                    _con.get('status'),
                    _con.get('scheduleType'))
                connection.sourceName = self.get_source(connection.sourceId).get('sources')[0].get('name')
                connection.destName = self.get_destination(connection.destId).get('destinations')[0].get('name')
                connections.append(connection)
                log.info(connection)
            except Exception as e:
                log.error("something went wrong %s", e)
        return connections

    def get_source(self, source_id):
        source = self.call_api('api/v1/sources/search', data=json.dumps({"source_id": source_id}))
        log.debug(source.get('sources')[0])
        return source

    def get_destination(self, destination_id):
        destination = self.call_api('api/v1/destinations/search', data=json.dumps({"destination_id": destination_id}))
        return destination

def main():
    conn = Airbyte(AIRBYTE_URL)
    w_id = conn.get_workspace_id()
    log.info("workspace Id : %s", conn.workspace)
    connections = conn.list_connections()

main()
