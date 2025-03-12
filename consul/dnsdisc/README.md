# DNS Discovery Tool

A utility for generating DNS Discovery records for Ethereum node discovery. This tool queries services registered in Consul and creates DNS TXT records in CloudFlare to enable ENR-based node discovery.

## Installation

1. (Optional but recommended) Create a virtual environment.

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. **Clone and build nim-dnsdisc**

   ```bash
   git clone https://github.com/status-im/nim-dnsdisc.git
   cd nim-dnsdisc

    # Build `tree_creator` utility
    make creator

    # Run tree creator utility with default configuration
    ./build/tree_creator
   ```
   For more details on the tree creator utility, see the [tutorial](https://github.com/status-im/nim-dnsdisc/blob/main/docs/tutorial.md).


2. **Set up environment variables and SSH tunnel**

   Export these environment variables from password store (mind the environment: `staging` or `prod`):

   ```bash
   export PRIVATE_KEY=$(pass services/dns-discovery/prod/staging/private-key)
   export CF_TOKEN=$(pass cloud/Cloudflare/token)
   export CONSUL_HTTP_TOKEN=$(pass services/consul/tokens/agent-default)
   ```

   Create an SSH tunnel to a host with Consul agent:

   ```bash
   ssh -L 8500:127.0.0.1:8500 -N -f user@boot-01.do-ams3.status.staging
   ```

3. **Run the DNS Discovery tool**

   Example usage for status staging environment:

   ```bash
   ./dnsdisc.py -x -e status -s staging -d boot.staging.status.nodes.status.im -n nim-waku-enr -C /path/to/nim-dnsdisc/build/tree_creator -i nim-waku-boot-enr
   ```

   **Note:** The `-x` flag performs a dry run, which is highly recommended to see what changes will be made before applying them.

   To see full ENR records, run with the debug log level: `-l debug`.

## Troubleshooting

**NOTE:** Do not use terraform consul http token which won't have permissions to read from consul catalog, instead use:

```bash
export CONSUL_HTTP_TOKEN=$(pass services/consul/tokens/agent-default)
```