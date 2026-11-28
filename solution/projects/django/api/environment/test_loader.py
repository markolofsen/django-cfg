"""Pure settings contract tests; no Django startup, database or real mail."""
import json
import os
import secrets
import unittest
from unittest.mock import patch

from pydantic import ValidationError

from api.environment.loader import DEVELOPMENT_SECRET_KEY, EnvironmentConfig


class EnvironmentLoaderTests(unittest.TestCase):
    def load(self, variables):
        with patch.dict(os.environ, variables, clear=True):
            return EnvironmentConfig(_env_file=None)

    def test_no_default_administrator(self):
        self.assertEqual(self.load({}).admin_emails, [])

    def test_explicit_administrator_list(self):
        recipients = ["admin@example.com", "ops@example.com"]
        self.assertEqual(self.load({"ADMIN_EMAILS": json.dumps(recipients)}).admin_emails,
                         recipients)

    def test_development_can_use_sample_secret(self):
        self.assertEqual(self.load({"IS_DEV": "true"}).secret_key, DEVELOPMENT_SECRET_KEY)

    def test_production_rejects_default_and_short_secret(self):
        for values in ({"IS_PROD": "true"},
                       {"IS_PROD": "true", "SECRET_KEY": "short"}):
            with self.subTest(configured="SECRET_KEY" in values):
                with self.assertRaisesRegex(ValidationError, "Production requires"):
                    self.load(values)

    def test_production_accepts_explicit_secret(self):
        key = secrets.token_urlsafe(48)
        settings = self.load({"IS_PROD": "true", "SECRET_KEY": key})
        self.assertEqual(settings.secret_key, key)
        self.assertEqual(settings.env.env_mode, "production")


if __name__ == "__main__":
    unittest.main()
