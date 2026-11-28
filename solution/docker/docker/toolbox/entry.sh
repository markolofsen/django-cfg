#!/bin/sh
set -eu
/usr/local/bin/docker-cfg-tools
exec "$@"
