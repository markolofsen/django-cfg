"""Django settings, one module per run mode.

| Module | Loaded by | Database |
|---|---|---|
| ``base`` | ``manage.py`` for everything except ``test`` | Postgres |
| ``test`` | ``manage.py test`` (see ``manage.py``) | SQLite, in-memory |

**This file stays empty of settings.** ``base`` publishes its values with
``locals().update(...)``, i.e. at runtime — and if that lived in this
``__init__``, importing ``api.settings.test`` would run the sibling *before*
the parent had finished, so the child would inherit a handful of names instead
of the full settings dict. Keeping the base in its own module means ``from
api.settings.base import *`` imports something already fully executed.
"""
