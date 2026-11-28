# Project agent instructions

This Git repository includes a cooperative workflow for multiple development
agents. Start with [workflow/README.md](workflow/README.md) and
[workflow/PARALLEL.md](workflow/PARALLEL.md).

One integration lead owns the real Git main checkout, live services, migrations,
shared dependencies, integration tests and authorized publication. Each writing
agent must register a task with an exact base SHA and non-overlapping paths,
use the separate local checkout created by workflow/lanes.py, and submit its
exact commit and evidence for review. Never override another agent's claim.

The workflow is coordination, not a security sandbox or an autonomous agent.
CMDOP is an optional transport to the machine, not the agent council.
No local lane inherits the canonical repository's Git remotes or credentials.
The owner controls code review, protected branches, secrets and deployment.
