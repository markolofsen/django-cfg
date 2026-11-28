# Current development work

No integration task is assigned at installation. No agent claim or task lane
is preloaded. Inspect live state before starting:

    python3 workflow/coord.py status
    python3 workflow/lanes.py status

The integration lead updates this committed cursor at handoff with the next
approved task. Keep per-agent state and private receipts out of Git.
