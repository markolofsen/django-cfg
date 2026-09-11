---
title: Product UX
status: current
version: "3.0"
audience: product, design, frontend, backend, agents
last_reviewed: 2026-09-01
---

# Product UX

The target is calm capability: a new user understands what is happening, while
an experienced user can act quickly without switching to a separate advanced
product.

## Start with the user's job

Before layout or components, write:

- the outcome the user wants;
- the information needed to decide;
- the primary action;
- the most costly mistake;
- what success, delay, partial failure, and recovery look like.

A page without a clear primary job SHOULD be split or reframed. A screen MAY
support many actions, but it MUST establish their hierarchy.

## Information hierarchy

Order operational content by decision value:

1. Current state in plain language.
2. The next useful or corrective action.
3. Essential evidence and consequences.
4. Secondary controls.
5. Technical detail on demand.

Do not lead with implementation vocabulary when the user is deciding whether
the system is healthy. "Online and ready" is more useful than a raw process
state. Preserve raw values in a technical disclosure for diagnosis.

## Progressive disclosure

Progressive disclosure is not hiding complexity. It is presenting complexity
at the moment it helps.

- Keep common decisions visible.
- Put diagnostics, IDs, bind addresses, and protocol metadata behind a stable
  disclosure or dedicated detail route.
- Never hide a blocker, degraded state, price, permission consequence, or data
  loss risk.
- Preserve disclosure state only when returning users benefit from it.
- Prefer a dedicated destination when disclosed content gains its own actions,
  lifecycle, or shareable URL.

## Action hierarchy

Each region SHOULD have at most one primary action.

| Intent | Presentation |
|---|---|
| Primary forward progress | primary button |
| Secondary safe action | outline or quiet button |
| Local utility such as copy or refresh | ghost/icon action with label or tooltip |
| Destructive or irreversible | explicit destructive treatment and confirmation |
| Navigation | link semantics, even when visually button-like |

Do not use color alone to create hierarchy. Do not place equally weighted
buttons side by side when their consequences differ.

## Status is a contract

A status indicator MUST answer a real question. Define its states before its
color.

```text
unknown -> connecting -> healthy
                    \-> degraded -> recovering
                    \-> stopped / failed
```

- Use one stable vocabulary across badges, rail indicators, detail views, logs,
  and notifications.
- Separate navigation selection from health. Selection answers "where am I?";
  health answers "is it working?".
- A steady healthy state SHOULD not pulse. Motion is reserved for transition or
  requested attention.
- Pair color with text, icon shape, tooltip, or accessible name.
- Use neutral unknown state instead of guessing from stale or absent data.

## Calm density

Product UI can be dense without feeling heavy.

- Use alignment and spacing before boxes.
- A card MUST communicate grouping, elevation, or interaction. It is not the
  default wrapper for every section.
- Avoid nested cards. Use sections, dividers, and whitespace inside a surface.
- Keep key-value rows scan-friendly: stable labels, aligned values, monospace
  only where character alignment matters.
- Use compact controls in repeated lists and comfortable controls in focused
  forms.
- Reserve the accent color for selection, action, and meaningful emphasis.

## Empty, loading, stale, and error states

Every data surface MUST define:

| State | User need |
|---|---|
| Initial loading | know the structure is coming without layout jump |
| Empty | understand whether this is normal and how to add data |
| Ready | perform the core job |
| Stale/revalidating | keep working with last-known data; show quiet sync feedback |
| Partial failure | retain useful content and identify what is missing |
| Blocking failure | understand impact and recovery action |
| Offline/unavailable | distinguish connectivity from an application error |
| Permission denied | know what access is required and who can grant it |

Use skeletons only when the final geometry is predictable. Use a compact status
message when it is not. Never replace valid stale content with a full-screen
spinner during background refresh.

## Destructive and risky operations

- State the object and consequence in the confirmation.
- Confirm near the action, not after an unrelated navigation.
- Require stronger friction only as risk rises; typing a name is for high-cost,
  hard-to-reverse actions.
- Disable repeat submission while a mutation is in flight.
- Show success where the result lives. Use a toast only for transient global
  acknowledgement.
- Prefer undo or soft delete when the domain supports it.

## Motion and delight

Motion MUST communicate feedback, hierarchy, continuity, or state change.

- Animate transform and opacity, not layout dimensions, when possible.
- Respect reduced-motion preferences.
- Avoid perpetual motion in operational screens except for a truly changing
  state.
- Keep navigation and data refresh stable; content should not jump merely to
  announce that it updated.

Delight comes from fast response, precise copy, preserved context, and good
defaults before it comes from animation.

## UX review questions

- Can a first-time user explain the page in ten seconds?
- Is the next action clear without being loud?
- Can an expert reach technical detail without fighting the interface?
- Are absence, delay, degradation, and failure distinguishable?
- Does every indicator carry information?
- Is the dangerous path harder than the safe path in proportion to risk?
- Does the mobile layout preserve the task rather than merely stack elements?

