#!/usr/bin/env/bash

# Verify mandatory veriables are set
[[ -z "$OAUTH2_CLIENT_ID" ]]     && echo "Not set: OAUTH2_CLIENT_ID"     && exit 1
[[ -z "$OAUTH2_CLIENT_SECRET" ]] && echo "Not set: OAUTH2_CLIENT_SECRET" && exit 1
[[ -z "$OAUTH2_COOKIE_DOMAIN" ]] && echo "Not set: OAUTH2_COOKIE_DOMAIN" && exit 1
[[ -z "$OAUTH2_COOKIE_SECRET" ]] && echo "Not set: OAUTH2_COOKIE_SECRET" && exit 1
[[ -z "$OAUTH2_REDIRECT_URL" ]]  && echo "Not set: OAUTH2_REDIRECT_URL"  && exit 1
[[ -z "$OAUTH2_UPSTREAMS" ]]     && echo "Not set: OAUTH2_UPSTREAMS"     && exit 1

# This will apply the environment variables defined for docker container
# to the template to generate the oauth2 config file.
envsubst < /var/lib/oauth.cfg.tpl > /etc/oauth2.cfg

# Run the actual proxy
/bin/oauth2_proxy -config /etc/oauth2.cfg $@
