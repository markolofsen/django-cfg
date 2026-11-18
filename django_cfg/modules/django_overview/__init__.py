"""Built-in Overview tabs of the admin: "MCP" (connect your assistant) and "Modules".

Both are ordinary dashboard tabs (``modules/django_dashboard``), contributed by
``tabs.get_dashboard_tabs()`` through the dashboard resolver, so a project gets
them without configuration:

- **MCP**, while MCP is enabled: every profile (URL, tool set, which credential
  it takes) and install commands for Claude Code, Codex and any other client,
  carrying the signed-in admin's own key. The key is never in the page: the
  commands show a mask, and "Show" / "Copy" fetch the real value by ``POST``
  (CSRF, ``Cache-Control: no-store``). See ``mcp_connect.py``.
- **Modules** (superusers): on / off / warning / error per module (MCP, Notion,
  Telegram, email, RQ and ``rqcron``, LLM keys, Constance, OAuth, analytics,
  logging) with a one-line hint. Booleans and names only, never a value. See
  ``module_status.py``.

Track: ``@dev/active/overview-mcp-and-modules/PLAN.md``.
"""
