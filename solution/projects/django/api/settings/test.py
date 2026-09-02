"""Test settings — SQLite, for a fast local test run.

``manage.py test`` routes here automatically (see ``manage.py``).
"""

# `api.settings.base`, never `api.settings`. The base settings are a sibling
# module, not this package's `__init__`, and that is load-bearing: while they
# lived in the `__init__`, importing this module would run it before the
# parent had finished executing, so the child would inherit only a handful of
# names instead of the full settings dict. See `api/settings/__init__.py`.
from api.settings.base import *  # noqa: F401,F403 — the settings this overrides

# Use SQLite for tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'ATOMIC_REQUESTS': False,  # Allow writes in tests
        'TEST': {
            'NAME': ':memory:',
        },
    }
}

# Throttled API tests must not depend on a developer Redis process.
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'django-cfg-tests',
    }
}


# Disable migrations for faster tests
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


MIGRATION_MODULES = DisableMigrations()

# Faster password hashing for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable logging during tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
}

# Outbound mail must not reach the network from a test.
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

IS_TEST_RUN = True
