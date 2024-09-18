#!/usr/bin/env python3
import requests
import json
import logging
from argparse import ArgumentParser

# Set up logging
log_format = "[%(asctime)s] [%(levelname)s] %(message)s"
logging.basicConfig(level=logging.INFO, format=log_format)
LOG = logging.getLogger(__name__)

HELP_DESCRIPTION = """
This is a utility script for migrating shards in the
Elasticsearch cluster when adding/removing nodes.
"""

HELP_EXAMPLE = """
Example: ./indices_migration.py --host http://localhost:9200
"""


def parse_args():
    parser = ArgumentParser(
        prog="Elasticsearch shard migration tool",
        description=HELP_DESCRIPTION,
        epilog=HELP_EXAMPLE,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    parser.add_argument(
        "-H",
        "--host",
        dest="es_host",
        default="http://localhost:9200",
        help="Elasticsearch host.",
    )
    group.add_argument(
        "-N",
        "--nodes-to-exclude",
        action="append",
        help="Nodes to migrate shards from.",
    )
    group.add_argument(
        "-S",
        "--show-nodes",
        action="store_true",
        help="Show nodes in the cluster and exit",
    )

    parser.add_argument(
        "-O",
        "--output",
        choices=["table", "json"],
        default="table",
        help="Output format for --show-nodes (choices: table, json). Default is table.",
    )

    return parser.parse_args()


class Node:
    def __init__(self, ip, name, master):
        """
        Initialize Elasticsearch node object with the IP, name and master flag.
        :param ip: IP address of the ES node host.
        :param name: Name of the ES node host.
        :param master: Boolean flag indicating if node is master.
        """
        self.ip = ip
        self.name = name
        self.master = master

    def __str__(self):
        """
        Return node string representation.
        """
        return f"{self.name} ({self.ip}) ({self.is_master})"

    def to_json(self):
        """
        Return the node as a dictionary suitable for JSON output.
        """
        return {"name": self.name, "ip": self.ip, "master": self.master}


class Elasticsearch:
    def __init__(self, host):
        """
        Initialize Elasticsearch client with the specified host.
        :param host: Elasticsearch host URL.
        """
        self.host = host
        self.nodes = self.__get_nodes()

    def __get_nodes(self):
        """
        Get all nodes in the ES cluster and return a list of Node objects.
        """
        url = f"{self.host}/_cat/nodes?format=json"
        try:
            LOG.info("Fetching all nodes in the ES cluster.")
            response = requests.request("GET", url)
            response.raise_for_status()
            return [
                Node(node["ip"], node["name"], node["master"] == "*")
                for node in response.json()
            ]
        except requests.exceptions.RequestException as e:
            LOG.error(f"Error fetching nodes from ES cluster: {e}")
            return []

    def show_nodes(self, output_format="table"):
        """
        Print Elasticsearch cluster nodes in either table or JSON format.
        :param output_format: 'table' for a human-readable table, 'json' for raw JSON output.
        """
        if output_format == "json":
            nodes_data = [node.to_json() for node in self.nodes]
            print(json.dumps(nodes_data, indent=2))
        else:
            print(f"\n{'ID':<4} {'Name':<30} {'IP':<16} {'Master':<10}")
            print("-" * 60)
            for idx, node in enumerate(self.nodes, start=1):
                print(f"{idx:<4} {node.name:<30} {node.ip:<16} {node.master:<10}")

    def migrate_shards(self, nodes_to_exclude):
        """
        Exclude selected Node objects from new shard allocations in the cluster
        and migrate all of the existing shards on them to other nodes.
        :param nodes_to_exclude: List of Node objects to be excluded.
        """
        if not nodes_to_exclude:
            raise ValueError("The nodes_to_exclude list cannot be empty.")

        try:
            ip_list = ",".join([node.ip for node in nodes_to_exclude])
            LOG.info(f"Migrating shards from nodes: {ip_list}")

            body = {"persistent": {"cluster.routing.allocation.exclude._ip": ip_list}}

            url = f"{self.host}/_cluster/settings"
            response = requests.request(
                "PUT",
                url,
                headers={"Content-Type": "application/json"},
                data=json.dumps(body),
            )
            response.raise_for_status()
            LOG.info(f"Successfully started shard migration from nodes: {ip_list}")
        except requests.exceptions.RequestException as e:
            LOG.error(f"Error starting shard migration: {e}")


def main():
    args = parse_args()

    es_host = args.es_host
    nodes_to_exclude = args.nodes_to_exclude
    show_nodes = args.show_nodes

    es = Elasticsearch(es_host)

    if not es.nodes:
        LOG.warning("No nodes available in the cluster.")
        return

    if show_nodes:
        output_format = args.output
        LOG.info(f"Showing nodes in ES cluster in {output_format} format and exiting.")
        es.show_nodes(output_format)
        return

    nodes_in_cluster = lambda node: node.name in nodes_to_exclude
    if nodes_to_exclude:
        es.migrate_shards(list(filter(nodes_in_cluster, es.nodes)))
    else:
        LOG.info("No nodes selected.")


if __name__ == "__main__":
    main()
