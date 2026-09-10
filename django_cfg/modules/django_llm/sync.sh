#!/usr/bin/env bash
#
# Sync this django_llm tree against the canon. All logic is in scripts/sync.py;
# this exists so the call is short and identical in every checkout.
#
#   ./sync.sh check                # read-only, exits 1 on drift
#   ./sync.sh sync                 # canon -> every tree
#   ./sync.sh promote project      # this tree -> canon -> every tree
#   ./sync.sh sync --dry-run       # print the plan, write nothing
#
# Needs python3 only — sync.py is stdlib-only on purpose, so it still runs when
# the engine beside it is broken.
#
# The logic lives in `.scripts/`, dot-prefixed to mark it as tooling rather
# than shipped code — the same signal `@docs/` and `@dev/` carry here.

set -euo pipefail
exec python3 "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/.scripts/sync.py" "$@"
