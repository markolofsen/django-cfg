#!/bin/sh
set -eu
for name in python python3 pip node pnpm git curl rsync rg ps tar gzip sha256sum timeout flock cmdop; do
  command -v "$name" >/dev/null || { printf 'Missing required toolbox program: %s\n' "$name" >&2; exit 78; }
done
cmdop --version >/dev/null

if [ "${1:-}" = '--report' ]; then
  python --version
  node --version
  pnpm --version
  git --version
  rsync --version | head -n 1
  rg --version | head -n 1
  ps --version
  cmdop --version
  sha256sum /usr/local/bin/cmdop
fi
