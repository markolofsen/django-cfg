"""django_frontend_errors: browser errors stored, one row per signature.

``django_monitor`` receives browser events and writes log lines. This app is the
queryable copy, on by default (``FrontendErrorsConfig(enabled=False)`` opts out):
it adds a table grouped by fingerprint, a stock-admin changelist and the MCP tools
``frontend_errors_top`` / ``frontend_errors_recent``. See README.md.
"""
