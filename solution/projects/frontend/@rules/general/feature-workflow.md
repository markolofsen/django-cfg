---
title: Feature Workflow
status: current
version: "3.0"
audience: product, design, frontend, backend, qa, agents
last_reviewed: 2026-09-01
---

# Feature Workflow

Build the smallest complete vertical slice through product behavior, data,
states, accessibility, and verification. Do not build a polished happy-path
screen and defer the contract.

## Phase 1: frame the problem

Write a short feature brief:

```text
User and context:
Outcome:
Primary decision/action:
Risks and permissions:
Required information:
Success signal:
Failure and recovery:
Out of scope:
```

State assumptions explicitly. If the feature cannot name its primary outcome,
do not start component work.

## Phase 2: audit before inventing

Inspect:

- existing routes and neighboring workflows;
- current product components and patterns;
- the shared design-system source and its declared package exports;
- domain types and generated API contracts;
- stores, query keys, and transport capabilities;
- loading, empty, stale, error, permission, and compact-layout precedents;
- local documentation and behavior invariants.

Record what will be reused, extended, and intentionally retired.

## Phase 3: define states and navigation

Before JSX, specify:

- durable URL destinations and query state;
- view state machine;
- data freshness and availability states;
- permission gates;
- mutations, confirmations, idempotency, and rollback;
- responsive transition and focus behavior;
- analytics/observability events that answer a real product question.

A flow diagram or state table is preferred when more than two async transitions
exist.

## Phase 4: settle the contract

Choose the data lane from [State and data](./state-and-data.md). For every read
and mutation, define:

- input and output schema;
- authorization and capability detection;
- cache key and freshness;
- empty vs absent semantics;
- normalized error categories;
- retry and idempotency behavior;
- event/reconnect reconciliation if pushed;
- redaction and logging rules.

If the backend contract is missing, decide whether a frontend adapter, a mock,
or a new endpoint best preserves the future contract.

## Contract-first, not mock-always

Mocks are tools, not architecture.

Use a mock or scenario harness when:

- backend work is not yet available;
- deterministic rare states are hard to reproduce;
- a scenario workbench or tests need isolated visual states;
- UX exploration benefits from fast local transitions.

Use a real endpoint early when:

- auth, streaming, timing, or error semantics are the feature;
- the contract already exists;
- a mock would conceal integration risk.

Mock the interface and full state machine, not only a successful response. The
swap to real data should preserve the feature contract, but it need not be a
literal one-file change in every architecture.

## Phase 5: build a vertical slice

Recommended order:

1. Domain types and pure state/view-model logic.
2. Canonical route and data owner.
3. Read path with initial, empty, ready, stale, and error states.
4. Primary action with success and failure.
5. Responsive/focus behavior.
6. Secondary actions and technical detail.
7. Instrumentation, copy polish, and visual refinement.

Keep the slice runnable. Avoid a broad component scaffold with no real behavior.

## Phase 6: review the backend as UX

Backend behavior shapes the interface. Review:

- Can related status values be read consistently?
- Can long operations report progress or a durable job ID?
- Can retries duplicate work?
- Are validation errors field-addressable?
- Can the user safely cancel or undo?
- Are permissions expressed as capabilities rather than trial-and-error 403s?
- Does pagination/filtering scale before the dataset becomes a problem?
- Can reconnect reconstruct truth after missed events?

Change the backend when doing so simplifies the product contract or prevents an
incorrect UI, not merely to relocate formatting.

## Phase 7: polish with evidence

After behavior works:

- remove unnecessary containers and repeated labels;
- tune hierarchy, density, and line length;
- verify semantic tokens in both modes;
- shorten copy and make errors actionable;
- measure expensive rendering and bundle impact;
- add motion only when it communicates a state transition or feedback.

## Change discipline

- Keep unrelated refactors out of the feature unless they unblock the contract.
- Update the owning docs when behavior or invariants change.
- Generated code is regenerated, never patched.
- Shared-library fixes belong in the shared repository, then flow through its
  supported sync and publish process.
- Preserve concurrent work; diagnose a failing build before overwriting files.

## Feature-ready checklist

- [ ] User outcome and non-goals are written.
- [ ] Existing UI and contracts were audited.
- [ ] URL, state owner, and data lane are explicit.
- [ ] All visible async and permission states exist.
- [ ] Primary action and recovery path work end to end.
- [ ] Compact, keyboard, theme, and locale behavior are defined.
- [ ] Backend semantics support honest UI.
- [ ] Verification evidence is captured.
- [ ] Owning documentation is current.

