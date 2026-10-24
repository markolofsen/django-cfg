## Local django-cfg (editable mode)

Two ways to use the local `~/djangocfg` source instead of PyPI:

### Option A — `make install-local` (recommended)
Uses `~/djangocfg/scripts/install_local_djangocfg.sh`. Does **not** touch `pyproject.toml`.

```bash
make install-local
```

1. Removes `[tool.uv.sources]` from `pyproject.toml` if present
2. `uv sync` to install all deps from PyPI
3. `pip install -e ~/djangocfg[full]` via install script into `.venv`
4. Removes stale `site-packages/django_cfg/` so `.pth` editable link takes effect

**After:** `uv run` and `.venv/bin/python` both use local source. `uv sync` will revert to PyPI — avoid it.

### Option B — `make install-local-uv` (uv-managed)
Adds `[tool.uv.sources]` to `pyproject.toml` temporarily so `uv sync` resolves from local path.

```bash
make install-local-uv
```

**After:** `uv run` uses local source. `pyproject.toml` has a local path entry.
Run `make install` to remove it and revert to PyPI.

### Install script directly

```bash
bash ~/djangocfg/scripts/install_local_djangocfg.sh --venv /path/to/.venv
# or use the same script from the package itself:
bash /path/to/django-cfg/scripts/install_local_djangocfg.sh --venv .venv
```
