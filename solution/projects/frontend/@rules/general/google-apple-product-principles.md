---
title: Google and Apple Product Principles
status: current
version: "1.0"
audience: product, design, frontend, backend, agents
last_reviewed: 2026-09-01
---

# Google and Apple Product Principles

This standard combines two complementary disciplines: Google-style systems
engineering and Apple-style product clarity. They are not visual preferences or
slogans; they are a decision order for every product change.

## Google: make the system explainable

### One source of truth

- Every durable fact has one authoritative owner and every other surface reads
  or derives it. Do not synchronize copies with effects, polling, or duplicate
  settings.
- The server owns security, capability availability, machine state, side
  effects, and durable operational policy. The client owns presentation and
  explicitly user-scoped preferences.
- A route registry owns web destinations; typed path builders construct URLs;
  feature workflows emit navigation intents.
- A capability is not enabled because a menu is visible. Its server-side guard,
  bootstrap projection, route behaviour, and UI discovery must agree.

### Clear boundaries and simple contracts

- Give each layer one job: domain language, transport protocol, state facade,
  feature workflow, or shell composition. Avoid cross-layer convenience imports.
- Prefer small typed contracts with a version and explicit unavailable state to
  ambient build constants, undocumented flags, or trial-and-error `403`s.
- Add abstractions only around a repeated stable contract. Keep a single use
  case local until a second consumer proves the boundary.
- Design for reconnect, reload, direct links, partial failure, and rollback
  before optimizing the happy path.

### Operational quality

- Make the safe path the default and fail closed before external side effects.
- Keep compatibility and migration explicit; preserve readable durable records
  even when their write capability is no longer available.
- Instrument meaningful transitions and outcomes without logging prompts,
  secrets, paths, or other sensitive payloads.
- Test pure policy/derivation first, then contract boundaries, then the real
  browser flow. A hidden button is not proof that a feature is disabled.

## Apple: make the product understandable

### Start from the user’s next decision

- Start with the user’s outcome, then define state, recovery, and hierarchy;
  do not start from a component inventory or a backend endpoint.
- The primary work loop gets the default screen and the quietest path. Rare,
  advanced, and diagnostic controls appear only when they help a real decision.
- Prefer a strong default to configuration. A setting earns its place only when
  different users reasonably need different durable behaviour.
- AI-first interfaces should prioritize legible results, evidence, and next
  actions over collecting extra input from the user.

### Progressive disclosure without deception

- Hide irrelevant complexity, never material risk, loss, permission impact, or
  recovery information.
- Do not tease unavailable features with disabled navigation, lock-filled
  menus, waitlists, or unexplained empty states. Either provide a supported
  path or remove it from normal discovery.
- Use one calm recovery action at a time. Keep technical detail available in a
  stable disclosure or dedicated route for the user who needs it.
- Preserve context, drafts, focus, and scroll during ordinary refresh and
  navigation. Background work must not interrupt an active task.

### Calm, precise interaction

- Use semantic controls, stable names, visible focus, accessible status, and
  real links for destinations. Tooltips supplement meaning; they do not create
  it.
- Build hierarchy with typography, spacing, grouping, and restraint before
  adding surfaces, borders, badges, or motion.
- Use accent color for meaningful action and selection, not decoration. Motion
  must communicate feedback or continuity.
- Keep copy concrete and human: name what happened, what remains possible, and
  the next useful action. Do not expose protocol language as primary UI copy.

## Resolving tension

When the two mindsets appear to disagree, use this order:

1. Preserve safety, correctness, and a single owner.
2. Preserve the user’s task and recovery path.
3. Prefer the smaller contract and quieter interface.
4. Add configuration or visible complexity only with evidence that the default
   fails a real user group.

Example: a beta toggle may reveal capabilities already authorized by the
server, but it cannot enable a parked daemon feature. This preserves a simple
interface while keeping capability authority and side-effect safety explicit.

## Review prompts

- What is the single source of truth for this decision?
- Which layer owns the state, side effect, and recovery?
- What does the first-time user need to understand in ten seconds?
- What can be removed from the default path without concealing a risk?
- Does reload, reconnect, direct entry, and failure preserve an honest task?
- Would another team understand the contract without reading this screen's JSX?
