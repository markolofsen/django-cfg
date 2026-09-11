---
title: Components and Interactions
status: current
version: "3.0"
audience: design, frontend, agents
last_reviewed: 2026-09-01
---

# Components and Interactions

Components should make the correct behavior easy to express and incorrect states
hard to represent.

Components and hooks MUST remain pure: the same props, state, and context produce
the same render. Do not mutate input snapshots or run side effects during render.
Time, random IDs, subscriptions, logging, and transport calls need an explicit
event, initializer, hook, or injected dependency.

## Component shape

A feature component typically follows this reading order:

1. Inputs and narrow state subscriptions.
2. Domain/query hooks.
3. Derived view model.
4. Events and mutations.
5. Explicit blocking state returns.
6. Main composition.

The render boundary is strict: all decisions and handlers are prepared before
returned JSX. This does not require memoizing every value.

## Data before JSX

Returned JSX is a declarative composition boundary, not a calculation area.

- Prepare labels, variants, classes, optional props, conditional subtrees, and
  mapped child nodes before the return.
- Pass named handlers; do not create event callbacks in markup.
- Keep input parsing and state transitions in those handlers, not in `onChange`
  or `onClick` expressions.
- Prefer an early return or a prepared `content` node for loading, error,
  unavailable, and empty branches.
- Extract a focused child component when a row needs per-item decisions. Do not
  hide a large render algorithm inside `array.map()` in JSX.

JSX MAY contain static markup, prepared variables, direct prop forwarding, and
already-prepared children only.

A contract this mechanical SHOULD be enforced by a gate rather than by review;
the repository profile names the one that runs here and the scope it covers.
Where a gate carries a baseline of existing debt, re-baselining is not a fix —
it records the violation as permitted. Move the decision to the render-model
phase, or extract a focused child component.

## Props and contracts

- Props MUST be typed without `any`.
- Prefer a discriminated union when prop combinations have distinct modes.
- Use one object parameter for hooks with several related options.
- Pass domain data or a small view model, not an entire store.
- Callbacks express user intent (`onRetry`, `onSelectMachine`) rather than DOM
  mechanics (`setModalOpen`).
- Keep optional props genuinely optional. A missing required capability MUST
  fail at compile time or render an explicit unavailable state.

## View models

When domain data needs formatting, permission decisions, or status projection,
derive a view model in a pure function. Test the function when it contains
branching product logic.

Do not mutate transport objects to add labels or UI flags. Do not store formatted
copy as server state.

## State machines over boolean soup

Multi-step, async, or interruptible workflows SHOULD use discriminated states:

```ts
type EnrollmentState =
  | { kind: "idle" }
  | { kind: "creating" }
  | { kind: "ready"; command: string; expiresAt: string }
  | { kind: "expired" }
  | { kind: "error"; message: string };
```

Events define valid transitions. Impossible combinations such as
`isLoading && isExpired && command` should not compile.

## Forms

- Use a visible label above or adjacent to every field. Placeholder is not a
  label.
- Keep description and error text associated with the control.
- Validate format early and business rules at the server boundary.
- Preserve user input after a recoverable server error.
- Place errors near the field or action that can fix them.
- Use native autocomplete, input mode, and semantic types.
- Do not disable submit before the user can understand why. Explain unmet
  requirements.
- Prevent duplicate submission while a request is active.

## Dialog, sheet, popover, or route

Choose by task, not by desired animation:

| Surface | Use when |
|---|---|
| Popover/menu | short contextual choice or utility |
| Dialog | focused decision that must complete or cancel before return |
| Sheet/side panel | contextual detail that benefits from retained background |
| Dedicated route | deep, shareable, multi-step, or independently navigable task |

Global dialog state is appropriate when a custom dialog opens from multiple
features or a shortcut. Local controlled state is simpler for one owner.
Imperative promise-based confirm/alert/prompt is appropriate for generic
decisions. Do not force every overlay into one registry.

### Registry or local state

One question decides it: **does anything OUTSIDE this component need to open
it?** More than one trigger, a keyboard shortcut, or a deep link — registry.
One button beside the overlay it opens — local `useState`, and that is the
finished answer, not debt to migrate later.

Local is not the weaker option, because a locally-owned overlay cannot outlive
its screen in the first place: it is declared inside that screen, so navigating
away unmounts the component and the flag dies with it. The registry needs a
route subscription precisely because its flags live in a global store that the
screen's unmount does not touch.

Moving a single-owner overlay into the registry therefore buys no behaviour and
costs three things: a unique id in a global namespace, state separated from the
component that owns it, and a reader who must now look in two files to answer
"what opens this". Reach for the registry when the first question says yes, not
to make a set of overlays look uniform.

## Overlay rules

- Mount global hosts once.
- Set initial focus intentionally and restore focus to the trigger.
- Escape closes only when cancellation is safe.
- Clicking outside MUST NOT discard risky work without warning.
- Dialog titles and descriptions are semantic, not merely visual.
- Nested modal surfaces SHOULD be avoided.
- Mobile adaptation MAY change a dialog to a sheet while preserving semantics.
- **An overlay MUST NOT outlive the screen it belongs to.** A modal still
  floating after the reader navigated away describes a screen that is no longer
  there, and on a compact frame it covers the one they asked for.
- **Enforce that in the registry, never by a hook each overlay opts into.** A
  rule applied by opt-in is missing wherever someone forgot, and nothing fails
  to say so — the registry subscribes once and every member gets it for free.
  This is also why an overlay that opens from several places belongs in the
  registry rather than in local state.
- **The unit is the SECTION, not the URL.** A modal belongs to a screen, so
  moving within one — another chat, another tab of the same area — must leave it
  alone, while leaving the area closes it. Closing on every navigation is the
  easy rule and the wrong one.
- Overlay state that is really SCREEN state — a panel sitting beside the content
  rather than over it, owned by the same hook as the selection — stays local. It
  is not a modal, and the registry is payload-less by design.

## Feedback

| Feedback | Best location |
|---|---|
| Field validation | under the field |
| Mutation failure with local recovery | beside the affected control/content |
| Persistent degraded system state | banner, status area, or page notice |
| Transient success | toast or local acknowledgement |
| Long-running operation | persistent progress surface that survives navigation |

A toast MUST NOT be the only record of an important error or a result the user
must reference later.

A snapshot-gated action reserves its space and label immediately: render the
control at once, disabled, with its FINAL label while the gating snapshot
loads. It enables when the snapshot confirms — it never pops in later, never
swaps labels on enable, and is never optimistically active (an early click
would race the very gate the snapshot exists to enforce). If the snapshot can
resolve to a different affordance entirely (an "Installed" link instead of an
install button), a neutral progress label is the honest placeholder.

For products with a typed application event bus, global toasts SHOULD be emitted
as semantic attention events and presented by one root adapter. Deduplicate by
stable operation identity and affected scope, not by rendered prose. Expected
pull failures (offline, unavailable, stale data) remain in their owning content
surface; automatically toasting every failed GET creates noise and hides the
difference between transient feedback and durable system state.

## Keyboard and focus

- Interactive elements MUST be reachable and operable by keyboard.
- Focus order follows reading and visual order.
- Focus rings MUST remain visible in every theme.
- Shortcuts MUST not fire while the user is typing unless specifically scoped.
- Display platform-appropriate shortcut labels.
- Global shortcuts require conflict ownership and a discoverable help surface.

## Copy and clipboard

Use the shared copy hook/button so permission errors and success feedback remain
consistent. Secrets require extra care:

- reveal deliberately;
- avoid copying adjacent labels or whitespace;
- communicate expiry and one-time visibility;
- never write the secret into logs, URLs, analytics, or persistent state.

## Component review

- Are invalid prop/state combinations unrepresentable?
- Are form, focus, keyboard, and cancellation behaviors complete?
- Is the chosen overlay less disruptive than a route and more useful than a
  popover?
- Does feedback remain visible long enough to act on?
- Are shared primitives used for clipboard, dialogs, toasts, and focus traps?
