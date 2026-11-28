#!/bin/sh
# Installs only inside this customer's dedicated source/dependency volumes.
set -eu
cd /workspace/solution/projects/frontend
node -e 'const p=require("./package.json"); if(p.packageManager!=="pnpm@9.15.4")process.exit(1)'
npm install --prefix /var/dev-data/pnpm-toolchain \
  --ignore-scripts --no-audit --no-fund --no-package-lock --save=false \
  --loglevel=error pnpm@9.15.4
PNPM=/var/dev-data/pnpm-toolchain/node_modules/pnpm/bin/pnpm.cjs
test "$(node "$PNPM" --version)" = "9.15.4"
node "$PNPM" install --frozen-lockfile --store-dir /var/dev-data/pnpm-store
echo 'CANONICAL_FRONTEND_FROZEN_INSTALL_PASSED'
# Source workspace packages export dist/ entrypoints consumed by dev apps.
# Build the proven small foundation sequentially; never run a monorepo-wide
# parallel build during dependency preparation.
for package in @djangocfg/api @djangocfg/i18n @djangocfg/nextjs; do
  node "$PNPM" --filter "$package" build
done
echo 'CANONICAL_FRONTEND_LIBRARY_BUILDS_PASSED'
