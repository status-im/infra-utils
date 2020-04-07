#!/usr/bin/env bash

set -e

if [[ -z "$API_TOKEN" ]]; then
    echo "The API_TOKEN env variable is not set"
    exit 1
fi

if [[ -z "$GUILD_ID" ]]; then
    echo "The GUILD_ID env variable is not set"
    exit 1
fi

docker run --rm -it -v "$PWD:/export" \
    tyrrrz/discordchatexporter \
    exportguild --bot \
        --token "$API_TOKEN" \
        --guild "$GUILD_ID" \
        --output "/export" \
        --format HtmlDark
