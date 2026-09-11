---
title: Comments and Code Narration
status: current
version: "3.0"
audience: frontend, backend, agents
last_reviewed: 2026-09-01
---

# Comments and Code Narration

A comment earns its place by carrying what the code cannot: why this shape, what
it connects to, what breaks if you change it. Anything the reader can see by
reading the line below is noise, and noise is not free — it pushes the valuable
comments off the screen and rots independently of the code.

Default to **no comment**. Write one when a specific question would otherwise
cost the next reader a search.

## Write a comment for

- **Why, not what.** The constraint, trade-off, or rejected alternative.
- **Coupling the file cannot show.** "The server composes this same shape when
  it builds the URL — the two builders must stay mirrored." Cross-repository
  couplings are the strongest case for a comment: nothing else in the file can
  point at the other half.
- **Load-bearing order or adjacency.** If moving a line silently breaks
  something, say so and name the failure.
- **What a defect would look like**, in one sentence, so the fix is not undone
  by someone who cannot see what it prevents. Write the FAILURE, not its
  history: "an empty label writes a bare `@` that names nobody" — never who
  reported it, when, or on which machine.
- **A deliberate absence.** Why a thing that looks missing is missing — a
  removed section, an ungated route, a parameter kept for old links.
- **A temporary state**, with its removal condition.

## Do not write

- Restatements: `// increment the counter` above `count += 1`.
- Section banners and decorative dividers.
- Type or signature echoes — the types already say it.
- Changelog and attribution: `// added 2026-08-16 by …`. Git owns that.
- Commented-out code. Delete it; it is in history.
- `// TODO` with no owner and no condition. Put it in the plan or leave it out.
- **Dates, names, and incident stories.** "measured 2026-08-22", "the owner
  reported", "reproduced on the staging box", "before phase 7 this mounted with
  nothing". The constraint is timeless; the anecdote goes stale the moment the
  surrounding code moves, and it is what turns a two-line note into a page.
  Delivery notes, git history and ADRs hold the story — none of them rot in
  place.
- **Track and plan references** in source: `E17-11`, `plan71 T2`, `F2`. They
  mean nothing to a reader who does not have the plan open, and they outlive
  the plan.
- **A rule number or a page name from this handbook.** The rules move; a
  comment citing one becomes a pointer to nothing. State the constraint itself.
- **Narration of a past shape.** "This used to read `connected: false`…". Say
  what the code must do and what breaks otherwise; the reader is not repairing
  a version they never saw.

Comments MUST be **English**, whatever language the discussion happened in.

### Two things that look like provenance and are not

Enforcing the rules above by a pattern sweep destroys both of these. **Read what
the word is DOING before removing it** — the same token is attribution in one
comment and domain vocabulary in the next.

- **"owner" is usually domain vocabulary.** It names the party a record belongs
  to ("a linked device of the owner's own account") or the single owner of a
  piece of state — the term the architecture page is built on ("one owner of the
  capability", "two owners of one selection"). Only attribution goes: *the owner
  hit this*, *owner decision*, *owner, 2026-08-20*.
- **Non-English text is often quoted UI copy or an i18n constraint.** A comment
  reasoning about what the screen says must be able to quote it, and so must one
  explaining why a date is interpolated rather than concatenated — in many
  languages the word order around it moves. Keep the quoted string, write the
  surrounding sentence in English. What goes is the quoted *complaint* or
  *decision*, not the quoted *interface*.

**If you automate the check, the unit is the comment LINE.** A per-character
scan of non-Latin script reported 4569 violations across 90 files where there
were 233 — one module header describing a translated catalogue scored 503 by
itself. Strip string and template literals before matching, or every ISO date in
a fixture counts as a violation.

## Keep them compact

Value per line is the measure, not length. A rule of thumb: **one paragraph**;
more only when the reasoning genuinely does not compress — a multi-repository
coupling, an incident with a non-obvious cause.

Compress by cutting hedging and restatement, never by cutting the reason:

```ts
// BAD — three lines that say what the code says
// This function takes an id and returns a path.
// It encodes the id first.
// Then it returns the string.

// GOOD — one line the code cannot say
// Encoded because an id may contain `:`, which the wire format uses as a separator.
```

If a comment needs several paragraphs to justify a design, it is probably a
decision record or a plan. Link to it instead of inlining it.

## Prefer a better name to a comment

A comment explaining what an identifier means is usually a naming bug. Rename
first; comment only what a name cannot hold.

## Keep them true

- A comment that contradicts the code is worse than none — readers trust it and
  a doc that copies it launders the error further.
- Change the comment in the same edit as the code it describes.
- When deleting code, delete its comment. An orphan comment about a removed
  branch reads as a live rule.

## Doc comments

Exported symbols SHOULD carry a short doc comment when the name alone does not
convey the contract: ownership, units, invariants, failure behaviour. Skip it
when the name is complete (`isSettingsSectionId`).

Module headers are for files that own a contract — a URL registry, a store, a
transport seam. They state what the module owns and what may not be duplicated
elsewhere. They are not a table of contents.

## Applies to agents too

Generated commentary drifts long and confident. Same bar: an agent MUST NOT add
a comment that narrates the diff, and SHOULD delete restatements it finds while
editing a file it already touched.
