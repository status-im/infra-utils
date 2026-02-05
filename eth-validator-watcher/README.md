# Usage

Those scripts help update the config of eth-validator-watcher.

```bash
# Extract the validator address from the TSV
cat $HOME/work/infra-lido/docs/validators/mainnet.tsv | awk -f parse_lido_tsv.awk
# Send the content into vault
update-vault.sh
rm lido-*.json
```

# Requirements

* Have the infra-lido repo clone and up to date
* Have vault access configured in the session
* Have bash
