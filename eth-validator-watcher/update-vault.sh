#!/usr/bin/env bash

# Script to update the Vault Secrets with the file generated

# Loop over all .json files in the current directory
for file in *.json; do
    # Check if there are any .json files
    if [ -f "$file" ]; then
        echo "Sending into vault the content of: $file"
        sed -i '0,/,/s/,//' $file
        # Replace the following line with your command
        cat $file | vault kv put -mount=secret nimbus/mainnet/archive/${file%.json} config=-
    else
        echo "No .json files found in the current directory."
        exit 1
    fi
done


