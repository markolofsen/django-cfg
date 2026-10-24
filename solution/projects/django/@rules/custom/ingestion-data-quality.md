---
title: Ingestion Data Quality
status: current
version: "1.0"
audience: backend, agents
last_reviewed: 2026-09-10
---

# Ingestion Data Quality

This catalogue is filled by an LLM reading scraped text from ~20 parsers. Bad
values do not arrive as errors — they arrive as plausible numbers, publish
successfully, and are found later by someone who counted something and
disagreed with the total.

`apps/catalog/plausibility/` is where "what a real listing looks like" is
stated once. Three consumers read it:

| Consumer | Role |
|---|---|
| `normalizer/types/base/schema.py` | pydantic validators — reject or repair on the way IN |
| `catalog/checks.py` | `catalog.W008`, the standing count on `manage.py check` |
| `manage.py plausibility` | what is wrong now, **grouped by source** |

## Measure before you write a threshold

Every constant in `_rules.py` carries the measurement that produced it, and
several first drafts were wrong in a way only measurement exposed:

- "A building bigger than its plot is impossible" — 762 of 858 such rows are
  ordinary multi-storey homes. The rule is a **ratio band**, not the
  inequality.
- "A `rental_period` means it is a rental" — 96 published sales carry one, and
  the expensive ones are genuine income properties sold with a letting
  arrangement. The rule needs the cadence AND the magnitude.
- "$50M is implausible" — flags 20 real Caribbean listings. Ceilings are
  **per country**.

**A rule that flags a genuine listing teaches an operator to ignore the
report.** Put the boundary in open space: check that no real rows sit just
inside it, and record the gap you found in the constant's docstring.

## The source column is the diagnosis

`manage.py plausibility` groups by parser because the shape of the spread names
the layer to fix:

- **One parser** → that parser's bug. Fix it at the source.
- **Spread evenly across many** → the prompt. Fix the shared fragment.
- **One parser, in BOTH directions at once** → not a parser bug at all. A
  one-way skew is systematic; a two-way spread is a classifier guessing,
  usually because the source text contradicts itself. Measured 2026-09-10:
  one parser produced 11 sales labelled rent and 9 rents labelled sale, from
  tenancies published under "for sale" headlines.

## Gate the flow, not the rows

**Repairing rows does not hold.** 94 mis-tagged listings accumulated within
hours of a manual currency repair — same source, same defect — because the
flow was never gated.

So a fix belongs in the validator, and the row-level report stays a report.
`RULES` deliberately never repairs: three batches in one week had more than one
correct answer, so a blanket relabel trades one wrong value for another.

## Prefer dropping a value to inventing one

When two fields disagree and only one can be right, ask which one the source
actually stated.

Worked example: a source emits `"floor_size": "32740 sq ft", "lot_size":
"32740 sq ft"` — one figure repeated, because a vacant lot has no floor area.
Rewriting the plot to `land × 10.7639` would make the ratio look right and the
number would still be a guess. Dropping the building size is honest: an absent
size is a state every consumer already renders.

**An invented number reaches the buyer as a fact.** `toDetail` maps
`land_size_sqm` to a property fact with `state: "confirmed"`, so a fabricated
plot renders as *verified*.

## Decline when the data cannot decide

A rule may legitimately cover only part of its own violations. Of 729 rows
carrying an identical building and land size, the property type answers 459 —
a lot has no floor area, a condo has no plot — and for `house`, `villa` and
`commercial` both fields are genuinely possible.

Those 270 keep both values and stay in `W008`. A rule that guessed would trade
a visible defect for an invisible one.

## Shared rules go in a shared fragment

`normalizer/types/base/prompt_fragments/` holds the cross-cutting prompt rules;
each specialist's `prompt.py` holds only what is specific to its type.

A rule that lives in one specialist's addendum is invisible to the other
eleven, and the second copy drifts. Measured 2026-09-10: the square-foot
conversion was mentioned only in `commercial_sale`'s addendum, while
`land_lot`'s said the opposite — so the same listing text produced a converted
plot and an unconverted floor area on one row.

Both fields end in `_sqm` and nothing had told the model what that meant.

## Related

- [`gates-and-verification.md`](./gates-and-verification.md) — `manage.py
  check` and what W008 sits beside.
- [`testing.md`](./testing.md) — why these validators are tested without a
  database, and why the negative cases carry the weight.
- [`app-roster-and-domains.md`](./app-roster-and-domains.md) — `catalog` vs
  `normalizer` ownership.
