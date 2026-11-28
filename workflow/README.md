# Team development workflow

This portable workflow is installed at this repository's **actual Git root**.
It requires Python 3 and Git. The scripts do not launch AI agents, grant
credentials, run tests automatically, merge branches or deploy applications.

1. Read [the agent rules](../AGENTS.md) and [parallel guide](PARALLEL.md).
2. Inspect `python3 workflow/coord.py status` and
   `python3 workflow/lanes.py status` from this Git root.
3. Assign disjoint task paths and open independent branches as documented.
4. Review committed diffs and evidence; integrate exact SHAs under one lead.
5. Record the next approved step in [CURRENT.md](CURRENT.md).

The local `runtime/` directory is ignored by Git. Never commit machine
identities, credentials, claim records or task reports with customer data.
