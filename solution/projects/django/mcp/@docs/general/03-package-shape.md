# 03 — Package shape

Where a tool's code goes, and why the layout is load-bearing rather than
tidiness.

## A group is a package

```text
tools/<group>/
  __init__.py     the tool registrations — a TOOLS list
  _bounds.py      this group's ceilings, private
  _helpers.py     this group's shared query and formatting code, private
  <tool>.py       one file per tool
tools/_shared/
  arguments.py    reading caller arguments safely
  responses.py    how every tool speaks back
```

One file per tool, named after what the tool is called. The point is that an
agent reporting `<group>_<verb>` tells you the file to open without a search.

Underscore-prefix everything group-private. It also keeps discovery from
treating a helper as a tool module, where the loader globs `*.py`.

## The shim, and why deleting it registers nothing

Where discovery imports `tools/*.py`, a directory is invisible to it. Converting
`<group>.py` into `<group>/` and deleting the file registers **nothing** — no
error, no tools, and a `tools/list` that simply comes back shorter.

So the flat module stays as a shim that imports the package's `TOOLS` and
registers them. Name it distinctly from the package (`<group>_tools.py` beside
`<group>/`); a module and a package with the same name cannot coexist in one
directory.

Inside a package, import absolutely. A relative import in a module that is also
reachable through the shim resolves differently depending on which path loaded
it.

## Shared code is for the shape of an answer, not the content of one

`_shared/` holds how tools speak — argument coercion, the empty shape, the dump
helper. It does not hold ceilings (see 02) and it does not hold domain queries.

A group's helpers exist to **reuse the domain rather than re-express it**. Where
the application already defines a visibility gate, a filter contract or a
privacy allow-list, call it. Restating any of them in the MCP layer creates a
second source of truth that has to be corrected twice — and the copy that is
missed is the one serving an agent.

This matters more than usual for a privacy allow-list: a hand-written
projection leaks a field the first time someone adds one to the model. An
allow-list serialiser makes the new field invisible until someone consciously
exposes it, which is the safe direction of failure.

## A task is a scheduling decision

Where tools enqueue background work, the task holds *when* it runs and calls
into the service layer for *what* it does. A task that grows its own domain
logic becomes a second implementation reachable only through a worker — the
hardest place to test and the easiest to let drift.
