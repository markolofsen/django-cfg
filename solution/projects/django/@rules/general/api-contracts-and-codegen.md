---
title: API Contracts and Code Generation
status: current
version: "2.0"
audience: backend, platform, agents
last_reviewed: 2026-09-01
---

# API Contracts and Code Generation

An API whose clients are generated is a **contract with a compiler on the other
end**. A change that reads as cosmetic here can fail a build in a repository
you have never opened. The concrete pipeline, targets, and commands are in
[`../custom/`](../custom/README.md).

## The generated client is downstream of a schema, not of your intent

**MUST NOT** hand-edit a generated client, ORM, or schema artifact. It is
overwritten by the next generation, and the edit is lost with no diff to
explain why behaviour changed back.

**MUST**: regenerate from the source of truth and commit the result in the same
change as the code that altered it. A schema change committed without its
regenerated clients leaves every consumer describing an API that no longer
exists.

**Read the generated output before believing a change landed.** A serializer
edit that produces no schema diff has changed nothing a client can see — and it
compiles, passes tests, and looks done.

## A closed vocabulary MUST be pinned as an enum

This is the single most expensive class of contract defect, because the failure
is silent and lands downstream.

A field documented as "one of three values" and typed as a free string
generates a client typed `string`. Every consumer then re-narrows it by hand,
each in its own way, and none of them fails when a fourth value appears.

- **MUST**: declare the closed set in the schema so the generator emits an
  enum.
- **MUST**: treat an enum value as **wire vocabulary**. Renaming one is a
  breaking change for every generated consumer even when the Python constant it
  came from was internal.
- **MUST**: distinguish two values that mean different things. When one field
  can carry both "why this was granted" and "why this was withdrawn", a
  consumer branching on it cannot tell an award from a penalty. Pin the set, and
  if two meanings share a field, split the field.
- The **empty string or null is a value** when clients branch on its absence.
  Declare it rather than leaving the client to infer.

## Serializers own the wire, not the rules

- A serializer validates and shapes the DTO. It does **not** decide whether the
  actor is permitted — that is a permission, and putting it in a validator
  hides it from every non-HTTP caller.
- **AVOID** a serializer that reaches into the database per row. A field that
  issues a query is an N+1 the moment the endpoint returns a list; annotate or
  prefetch instead.
- Keep the response shape stable and additive. Removing or retyping a field is
  breaking; adding an optional one is not.

## Additive by default

**SHOULD**: evolve a contract by addition. Add the new field, populate both,
migrate consumers, then remove the old one in a later change.

A change is **breaking** if it removes a field, narrows a type, makes an
optional field required, renames anything, or changes the meaning of an
existing value. Breaking changes are a deliberate decision with a consumer
migration plan, not a side effect of a rename.

## Generation crosses repository boundaries

Where generated artifacts land in **other repositories**, two things become
true that are easy to miss:

- **The blast radius of a schema edit is not visible in this repository's
  tests.** Nothing here fails when a downstream client stops compiling.
- **A generation run is a write into someone else's tree.** Know which
  repositories a run touches before starting one, and do not leave a partial
  generation behind — a half-regenerated consumer is harder to diagnose than an
  entirely stale one, because part of it agrees with you.

**SHOULD**: a drift check exists that regenerates and compares, so a schema
edited without regeneration is caught. Its command belongs in `custom/`.

## Review checklist

- Was every generated artifact regenerated from source rather than patched, and
  committed in the same change?
- Was the generated output actually read, not assumed?
- Does every closed set of values carry an enum, with values that distinguish
  meanings a consumer must branch on?
- Is the change additive — or is it breaking, deliberately, with a named
  consumer migration?
- Which other repositories does this generation write into?
