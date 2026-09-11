---
title: Documentation Governance
status: current
version: "2.0"
audience: backend, platform, agents
last_reviewed: 2026-09-01
---

# Documentation Governance

Documentation is code: owned, verified, and updated **in the same change** as
the behavior it describes. Which surfaces exist here and which command checks
them is in [`../custom/`](../custom/README.md).

## One job per surface

A repository accumulates several documentation surfaces — published docs,
delivery plans, per-subtree instruction files, and a long-form standard. Each
needs exactly one job, and a fact belongs to exactly one of them:

- **Current behavior** → the published docs.
- **Durable rationale for a decision** → a decision record, append-only.
- **Future or unconfirmed work** → a plan. **Never** a current page.
- **A subsystem invariant** → the nearest local instruction file.
- **Cross-cutting policy** → this handbook.

The rule that keeps this honest: **link, don't copy.** One source of truth per
fact, and the others point at it.

## The most damaging defect is a path that moved

A named path, module, command or symbol that no longer exists is a **defect,
not staleness**. It costs the reader time and their trust in every other line
on the page, and it does not announce itself: no test fails, no check reddens.

Worse, a wrong doc does not merely fail to help — **it actively directs work in
the wrong direction.** A page naming a registry file that was split six weeks
ago sends every reader to a dead path while reading as authoritative.

Two duties follow, and they carry the whole weight:

1. **Verify what you are about to touch — and what is around it.** Do not
   correct one line and step over a false one beside it. The marginal cost of
   checking neighbouring claims while the file is already open is near zero.
2. **A structural change obliges you to revisit every doc it invalidates**, not
   only the page you came to edit. A split config, a renamed app, a retired
   command reaches files you never opened. **Grep for the old name before you
   close the branch.**

## Dates and staleness

Where pages carry a review date, **bump it only on a page you actually re-read
against the code.** Stamping an unverified page marks a lie as reviewed, which
is worse than leaving it visibly stale.

Where a staleness check compares a page's date against the commit dates of the
code it references, understand what it can and cannot see:

- It sees only pages that **have** a reference pointing at a file that moved.
- A page with a weak or missing reference **never flags**, no matter how wrong
  it gets.
- **A brand-new capability has no page to flag at all.**

So a green staleness check means "nothing the check can see is stale" — never
"the docs are correct". After clearing its list, ask the question it cannot:
*did anything ship that no page describes yet?*

A reference must name the file that **embodies** the claim — never a directory,
never an aggregate file. The test: would every commit to this file require
re-reading the page?

## Refreshing after a change wave

**Do not find the worklist by reading the log and judging.** A wave is
routinely hundreds of commits over hundreds of files; skimming produces a
plausible sample, not a worklist, and the docs it misses are invisible.

Compute the worklist from the tools, then read: the staleness check gives you
the per-page assignments, and the change data tells you which subsystems moved
most — those deserve reading even when their dates look fresh.

**A refresh that only bumps dates is worse than no refresh**: it converts
"stale and flagged" into "wrong and trusted".

## Review checklist

- Does each fact live on exactly one surface, with links elsewhere?
- Did this change update its documentation in the same commit?
- Is every command, path and symbol on the page real **today**?
- If this change moved or split something: which other pages now say something
  false?
- Was a review date bumped only where the page was genuinely re-read?
