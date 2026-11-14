"""What a person needs to connect an assistant to an MCP profile: an install
script and an agent skill, both served by the profile's own endpoint.

* ``script.py``: ``<endpoint>/install.sh``, a fixed POSIX ``sh`` template.
* ``skill.py``: ``<endpoint>/SKILL.md``, generated from the live server.
* ``views.py``: the two views, gated like ``/info/``.
"""
