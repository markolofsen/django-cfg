# `projects/django/@dev` — delivery notes

Plans, decisions and evidence for the **Django half** of this project: its apps,
its API surface, its settings and the migrations that shape them.

Read [`CLAUDE.md`](CLAUDE.md) before adding or moving a document. How code must
be written is [`../@rules`](../@rules), not here.

## This tree starts empty, on purpose

This project is the **example shipped with django-cfg** — a starting point to
copy. The structure is the point: it shows the shape your delivery notes should
take, not somebody else's backlog.

Open your first track by creating `planned/<kebab-case-name>/PLAN.md`. The
contract in [`CLAUDE.md`](CLAUDE.md) says what belongs in it.

## Which tree a track belongs in

| Tree | Owns |
|---|---|
| **this tree** | The Django half of this project |
| [`../frontend/@dev`](../frontend/@dev/README.md) | The frontend beside it |

A track that spans both lives in whichever it mostly changes, and the other
tree's README links to it. **Two plans for one piece of work is how they come to
disagree.**

## Status directories

**The directories are the map.** Each one's `README.md` is the index for its
tracks; this page keeps no second copy.

| Looking for | Read |
|---|---|
| What can be worked on now | [`active/README.md`](active/README.md) |
| What is waiting, on whom, and the unblock condition | [`blocked/README.md`](blocked/README.md) |
| What is approved but not started | [`planned/README.md`](planned/README.md) |
| What shipped, and its evidence | [`completed/README.md`](completed/README.md) |
| Why something was decided | [`decisions/README.md`](decisions/README.md) |
| Raw investigation feeding a track | [`research/README.md`](research/README.md) |
| Frozen history — never current status | [`_archive/README.md`](_archive/README.md) |

## Current tracks

| State | Track | Summary |
|---|---|---|
| — | Empty | No tracks yet. |

Checked 2026-09-11.
