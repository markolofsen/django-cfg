## Local django-cfg (editable mode)

To use the local `~/djangocfg` source instead of PyPI:

```bash
make install-local
```

Runs `uv sync`, then calls `~/djangocfg/scripts/install_local_djangocfg.sh --venv .venv` which does `pip install -e ~/djangocfg[full]` and removes `.venv/lib/python3.12/site-packages/django_cfg/` so Python imports from the local source via `_django_cfg.pth`.

To install into any project venv directly:
```bash
bash ~/djangocfg/scripts/install_local_djangocfg.sh --venv /path/to/.venv
```

**Never run `uv sync` manually when using local django-cfg** — it reverts to PyPI.
