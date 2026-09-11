---
title: Executable UI Specifications
status: current
version: "3.0"
audience: product, design, frontend, qa, agents
last_reviewed: 2026-09-01
---

# Executable UI Specifications

For agent-built interfaces, prose acceptance criteria are necessary but not
sufficient. Important UI states should be reproducible, inspectable, and
testable without manually recreating production conditions.

## Scenario catalog as product contract

Define a scenario for every materially different user decision:

```text
first load
empty
ready with representative data
ready at data extremes
background refresh with stale content
partial failure
blocking failure
unavailable/offline
permission denied
mutation in flight
mutation rejected
compact viewport
long locale / RTL when supported
reduced motion
```

Not every component needs every scenario. Every feature surface MUST cover the
states it claims to support.

## Where the repository has a scenario workbench

Some repositories run a scenario workbench — a harness that mounts components in
isolation with typed fixtures. Where one exists, its scenarios are executable
examples, smoke tests, and review fixtures, and these rules apply. Where none
exists, the scenario catalog above is still the contract; it is discharged by
unit tests over the view model plus browser verification.

- Keep fixtures deterministic and typed.
- Name scenarios by user-visible state, not implementation prop combinations.
- Render pure views without importing application singletons at module load.
- Provide scenario-level adapters for transport, router, time, permissions, and
  feature flags.
- Reuse the product's real providers and semantic tokens.
- Include narrow/wide layout wrappers only where the component does not own its
  dimensions.
- A scenario that represents an accessibility baseline SHOULD opt into a
  blocking automated a11y assertion rather than remain permanently advisory.
  Nothing runs that suite for you — a person runs it before a release, so an
  un-run suite is silence, not a pass.

A workbench is not a second application. It should exercise the same public
components and contracts as the shipped host; a scenario that reimplements the
feature proves the reimplementation works.

Where the scenario FILES live, and what happens to a directory's gates when a
shared harness appears, is owned by
[Code organization and naming](code-organization-and-naming.md#the-workbench-gets-its-own-folder-once-it-needs-a-harness).
The short version: beside the subject until a harness exists, then a `stories/`
folder, and every gate that exempted the workbench re-keys onto the path
segment.

## Separate connected and view layers

A connected component owns data hooks and navigation integration. A view owns
rendering and interaction intents.

```tsx
export function StatusPanelConnected() {
  const model = useStatusModel();
  return <StatusPanelView {...model} />;
}
```

Cover the view with typed scenarios. Integration-test the connected wrapper.
Do not duplicate feature logic in a scenario-only implementation.

## Interaction contracts

Use scripted interactions in the workbench, or browser component tests, for
meaningful local behavior:

- keyboard navigation and focus restoration;
- open, cancel, confirm, and retry;
- validation and preserved input;
- selection and URL/navigation intents;
- copy and mutation feedback;
- disabled/busy repeat-action protection.

Query by accessible role, label, and visible name. `data-testid` is a fallback
for a real testing contract; CSS selectors and DOM paths are implementation
details.

## Visual contracts

Visual regression is most useful when the matrix is intentional:

| Axis | Representative coverage |
|---|---|
| Theme | light and dark |
| Width | compact, standard, wide |
| Content | empty, typical, long/extreme |
| State | healthy, degraded, error, busy |
| Locale | source locale plus one long/RTL stress case |
| Motion | normal and reduced when animation affects layout |

Freeze clocks, random values, animations, network responses, and caret/cursor
effects for screenshots. Review semantic changes, not raw pixel churn.

## Where a real-browser lane exists

Not every repository has an automated end-to-end runner, and adding one is a
decision, not a default. Where a real-browser lane DOES exist, it is for
behavior that crosses component boundaries:

- direct route entry, reload, back, and forward;
- authentication and re-authentication;
- query/cache/reconnect behavior;
- WebSocket/SSE and live updates;
- file upload/download and browser permissions;
- responsive master/detail focus continuity;
- integration with an embedding host;
- one critical happy path and its highest-risk recovery path.

Keep such tests isolated. Use user-facing locators and web-first assertions so
the runner waits for actual visible state instead of sleeping for guessed
durations.

Where no such lane exists, the same list is the **manual** browser-verification
checklist, and it is not optional — the coverage obligation belongs to the
behavior, not to the tooling. Say which of the two you did.

## React determinism

Components and hooks MUST be pure with respect to their inputs.

- Do not call `Date.now()`, `new Date()`, `Math.random()`, or UUID generation
  directly during render when the value affects output.
- Inject a clock/ID source, initialize state once, or update from an effect/event.
- Never mutate props, state snapshots, hook arguments, or values after passing
  them to JSX.
- Keep side effects outside render.
- Run Strict Mode and the React Hooks ESLint rules.
- Treat manual memoization as a measured optimization, especially as React
  Compiler can automate common memoization in compatible projects.

Determinism makes stories, screenshots, tests, replay, and agent diagnosis much
more reliable.

## The utility-CSS static contract

Where the product uses a scanning utility-CSS framework, that scanner reads
TEXT; it does not understand runtime string construction.

```tsx
const toneClass = {
  healthy: "bg-success text-success-foreground",
  warning: "bg-warning-background text-warning-foreground",
} as const;
```

- Map variants to complete, statically detectable class strings.
- Never construct `bg-${tone}-500` or similar runtime fragments.
- Register every workspace and source-shipped library root the scanner must
  read. A root it was never pointed at emits no utilities, and nothing reports
  it.
- Use an inline safelist only as a deliberate exception with a documented owner.
- Test the production build; a dev server can conceal a missing generated
  utility, because it generates on demand from what it happens to see.

## Contract-focused tests

- Unit tests verify pure state transitions, derivations, schemas, and store
  contracts.
- Scenario/component tests verify isolated visible states and interactions.
- End-to-end tests, where the repository runs them, verify cross-boundary user
  behavior; otherwise a browser walkthrough carries that obligation.
- Do not mock the unit being tested. Mock slow, nondeterministic, destructive,
  or externally controlled dependencies.
- Reset stores, timers, handlers, and module mocks between tests.
- Test names describe behavior, not internal calls.

## Agent evidence bundle

For a material UI change, the agent handoff SHOULD include:

```text
changed routes and scenarios
scenario IDs or reproducible fixture names
test commands run, with their results, and which lanes the repository has
browser console result
theme and viewport coverage
screenshots for visual review
known untested states and reason
bundle or performance impact when relevant
```

This turns "done" into evidence another human or agent can reproduce.

## Primary references

- [React rules and purity](https://react.dev/reference/rules)
- [Tailwind source detection](https://tailwindcss.com/docs/detecting-classes-in-source-files)
- [Storybook UI testing](https://storybook.js.org/docs/writing-tests)
- [Storybook accessibility testing](https://storybook.js.org/docs/writing-tests/accessibility-testing)
- [Playwright best practices](https://playwright.dev/docs/best-practices)
- [Vitest testing in practice](https://vitest.dev/guide/learn/testing-in-practice)

