# 02 — Bounds and arguments

Two halves of one question: what may come in, and how much may go out.

## Arguments arrive as whatever the model produced

A string where an integer was declared, a null, a missing key, an absurd limit
— **normal traffic, not misuse**. The schema is a hint to the model, never a
guarantee to the tool.

**Clamp rather than raise.** A tool that errors on `limit="25"` teaches the
agent the tool is broken, and the agent stops using it. That is a worse outcome
than a clamped answer, because the agent cannot ask a follow-up question to
discover its own formatting was at fault.

Accept the forms models actually send — `5`, `"5"`, `5.0`, `" 5 "` — and treat
anything uncoercible as the default. Two details that bite:

- `bool` is an `int` subclass, so `True` silently reads as `1` unless excluded.
- A caller asking for `0` or `-1` rows wants *some* rows and has miscounted.
  Clamp to 1. Returning an empty list would be read as "no such data", the
  single most expensive misreading this surface can produce.

The one exception to clamping is a value that would answer a **different
question**: an unknown enum, a filter slug that does not exist. Silently
ignoring those succeeds at the wrong task. Reject and name the argument.

## Ceilings belong to the group that pays for them

Put a group's limits in its own bounds module, as named constants with the
reasoning in the comment. A ceiling inlined at a call site is one nobody can
review; a ceiling with no comment is one nobody dares change.

**Do not hoist ceilings into shared code.** 100 rows of one domain and 25 of
another are different costs, and a shared default quietly becomes the ceiling
nobody chose.

Advertise the ceiling that will actually be enforced. If the schema says
`1-50` and the code clamps to 25, an agent that asked for 50 and got 25 reads
that as a broken server rather than a policy.

## Cap the product, not only the fields

This is the one most easily missed, and it is worth stating as a rule because
every individual decision leading to it looked reasonable.

A list result's cost is **rows × per-row size**, and a nested collection makes
the second factor unbounded. Capping rows at 25 and truncating a text field to
400 characters still permits an enormous payload if each row carries forty
nested objects — neither factor looks expensive alone.

Measured here on 2026-09-03: five searches at 25 rows returned 168k–490k
characters each, ~1.44M in total. Every one exceeded the caller's ceiling and
was spilled to a file unread. **Nothing errored.** The tool was correct,
privacy-safe and unusable, and the agent finished the task by shelling out to
`jq` over the spill files.

So: bound the whole payload, not just its parts. When the bound trips, degrade
in one **announced** step — drop the heavy fields, set a flag, and name the
tool that serves them — rather than truncating the JSON.

## Nesting is not free, and detail has its own tool

A list row exists to answer *"is this worth opening?"*. A detail tool exists to
answer everything else. Serving the full nested record in both collapses that
distinction and pays for it on every row.

A count is usually the right substitute: "this record has 40 images" is
information; 40 URLs are not.

## What to bound

Rows, query length, time range, execution time, **and payload size**. That last
one is the one most often written in a standard and absent from the code.
