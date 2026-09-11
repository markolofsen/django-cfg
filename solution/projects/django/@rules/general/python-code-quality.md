---
title: Python Code Quality
status: current
version: "2.0"
audience: backend, agents
last_reviewed: 2026-09-01
---

# Python Code Quality

Quality means local reasoning, explicit failure handling, and checks that are
narrow enough to stay switched on. **Do not claim enforcement from a tool the
repository does not run** — the gate inventory in `custom/` names what actually
executes.

## Errors and control flow

- Handle every error explicitly. **Never `except:` bare**, and never a bare
  `except Exception` that swallows without re-raising or recording.
- Raise a domain-specific exception where a caller must tell failure modes
  apart. A caller that has to inspect an error message is a caller that will
  break on a reworded string.
- **AVOID inventing success.** A degraded result is reported as degraded, not
  silently substituted with a default, an empty list, or a cached value.
- A retry belongs only on an idempotent operation. Make the operation
  idempotent rather than retrying until the answer changes.

## Types and boundaries

- Type public function signatures and anything crossing a layer. Types inside a
  short private helper earn less.
- A string annotation that names a type nobody imports is broken for every
  type-aware tool even though it runs fine. If a name appears only under
  `TYPE_CHECKING`, import it there.
- **AVOID `Any` at a boundary.** It is a promise that the value has been
  validated somewhere else, and that somewhere is usually nowhere.

## A narrow gate that runs beats a broad gate that gets disabled

This is the most important rule on the page, because it decides whether any of
the others are enforced.

When a linter is first pointed at an unlinted repository, the honest default
selection produces hundreds or thousands of findings. **A thousand findings on
a repository nobody has linted is not a quality gate; it is a wall of red that
gets switched off within a day, taking the real findings with it.**

So select by **what points at a defect**, not by what is stylistically
improvable:

- **Keep**: undefined names, redefinitions where the second silently wins,
  unused variables that were meant to be used, syntax and IO errors, mutable
  default arguments, bare excepts, loop-variable capture in closures.
- **Leave out**: whole-codebase style modernisation. Rewriting an old typing
  idiom across hundreds of files is a refactor with its own diff and its own
  review — not something to discover through save-on-format.
- **Leave out, even when it finds real defects**, any rule that fires on
  working code by design. An unused-import check is the classic case: settings
  modules and package `__init__` files re-export names for their side effects,
  so the rule is wrong there more often than it is right. Run it **by hand**
  after moving code, where its precision is high.

Two disciplines follow:

- **Choose the selection by measurement, and record the measurement.** Write
  down what each candidate rule found on this tree and why it was kept or
  dropped. Without that, the next person re-litigates the config from taste.
- **Per-file exemptions carry their reason.** "Generated", "re-exports for the
  framework to find", "fixtures imported for their side effects" are reasons; a
  bare path list is a place to hide.

The same logic governs adding a rule later: a rule that would light up a
hundred existing files is a **refactor proposal**, not a gate change. Do the
refactor, then add the rule.

## One fact, one owner

Duplication that matters is not repeated *text* — it is the same **decision**
made in two places. Two copies of a helper are cheap; two answers to one
question drift, and the drift is silent until they disagree in production.

- Before adding a function that answers a question the system already answers
  ("is this user entitled?", "what does this cost?", "is this tenant active?"),
  find the existing owner and extend it.
- **A fix to a class is not done until every derivation is swept.** Grep the
  raw pattern and fix or explicitly exempt each site in the same change. A
  partial sweep is worse than none: it looks closed.
- When a rename or deletion lands, remove every derivation with it — fixtures,
  docs, generated output, exemption entries. A dangling reference to deleted
  code is a defect, not untidiness.

## Earning an abstraction

- Extract a shared helper on the **second real caller**, not the first
  anticipated one.
- **A seam whose only callers are its own tests has not shipped.** Tests keep
  it importable and looking alive while nothing reaches it from a running
  request or job.
- Delete dead code rather than parking it. "Kept for symmetry" and "a future
  caller will need it" are not reasons — and a dead helper whose behaviour is
  the defect you just fixed will be found by name and reused.
- A parameter no production path sets is dead even when a test keeps it valid.

## Comments

A comment states a constraint the code cannot show (an invariant, an ordering,
a provider quirk, an incident lesson). The default is **one to three lines**.

- **English only**, in every comment, docstring and identifier. Do not paste a
  chat quote into source — restate the constraint.
- **State the rule, then the failure mode in one clause.** "X, because Y breaks
  otherwise" beats three sentences reconstructing how Y was discovered.
- **No incident narratives**, no attribution, **no dates** unless the fact
  genuinely expires (a pinned provider version may carry one; "fixed
  2026-08-25" may not — the history already knows).
- **No delivery bookkeeping.** No plan IDs, no track paths, no "Closes F4".
  Those are renamed or archived within weeks, and the comment then points at
  nothing while still reading as authoritative. Write the **reason**, not the
  reference: what breaks if someone undoes this.
- **Do not restate the line below.** If the comment and the code say the same
  thing, delete the comment.

A comment claiming an invariant is a **claim**, and review must treat it as
one. Three shapes recur: the aspirational comment (describes what the code will
do once something lands), the stale comment (was true, behaviour moved), and
the unearned enforcement claim ("the gate enforces this"). Check that the gate
exists *and* that something runs it.

## Review checklist

- Does every failure path raise, return, or record — never silently succeed?
- Would a new lint rule light up existing files? Then it is a refactor, not a
  gate change.
- Does this add a **second answer** to a question the system already answers?
- Does each new seam have a production caller, not only a test?
- Does every comment claiming an invariant still hold today?
