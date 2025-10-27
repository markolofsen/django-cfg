#!/bin/sh
set -e

# Substitute environment variables in config template
sed -e "s/\${CENTRIFUGO_API_KEY}/${CENTRIFUGO_API_KEY}/g" \
    -e "s/\${CENTRIFUGO_TOKEN_HMAC_SECRET}/${CENTRIFUGO_TOKEN_HMAC_SECRET}/g" \
    -e "s/\${CENTRIFUGO_ADMIN_PASSWORD}/${CENTRIFUGO_ADMIN_PASSWORD}/g" \
    -e "s/\${CENTRIFUGO_ADMIN_SECRET}/${CENTRIFUGO_ADMIN_SECRET}/g" \
    -e "s/\${CENTRIFUGO_LOG_LEVEL}/${CENTRIFUGO_LOG_LEVEL}/g" \
    /centrifugo/config.template.json > /tmp/config.json

# Start Centrifugo with generated config
exec centrifugo -c /tmp/config.json
