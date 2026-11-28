# Chat bridge — how the AI drives the user's page

When the assistant answers a question about the page, it can also
**act on it** — point at the screen, move focus, scroll an element into
view. This module is that control surface, plus the overlay that draws
the spotlight.

---

## The idea

The chat sends the backend a snapshot of the user's page (the
`page-snapshot` engine). Every interactive element in that snapshot got
a short ref id — `@e4`. The assistant, knowing those refs, can reply:

> "Click **Save** to apply your changes."

…and attach a directive: `point at @e4`. This module resolves `@e4`
back to the live DOM element and draws a spotlight on it.

This is the intelligent successor to the old scripted product Tour —
the spotlight is the same, but *what* it points at is decided by the AI
in context, not a hard-coded step list. The SVG renderer here is in
fact adapted from that deleted Tour component.

**Read-only by default.** A `point` directive highlights / focuses an
element; it never types, clicks, or changes the user's data. The
write-style commands (`fill`, `click`) are deliberately stubbed.

---

## The round trip

```
 capture: page-snapshot engine assigns @e1, @e2, … to interactive nodes
          and keeps a ref → element registry
   │
   ▼  snapshot sent with the chat message (request body metadata)
 backend: the LLM, given the snapshot, may append a directive marker:
          <<directives>[{"type":"point","ref":"@e4","focus":true}]</directives>>
          the marker is parsed + validated, stripped from the reply,
          and emitted as a `directive` SSE event
   │
   ▼  directive SSE event arrives on the client
 this module: resolve @e4 → element via the snapshot registry,
              draw the spotlight, optionally focus
```

---

## Layout

The module has two layers — `page-tooling/browser-bridge/` is *how the AI drives the
browser*, `overlay/` is *how a highlight is drawn*.

```
page-tooling/browser-bridge/
  index.ts             Public barrel.
  perform.ts           Resolve, scroll, wait, act (the page action).
  registry.ts          BridgeCommand interface + the command registry.
  set-bridge-resolver.ts Holds the live ref→element resolver the commands read.
  directive-bus.ts     SSE `directive` event → singleton bus.
  window.ts            installChatBridge — dev-only window.__chatBridge.
  commands/
    index.ts           Registers + re-exports every built-in command.
    highlight.ts       highlight, focus, clear.
    scroll.ts          scrollTo.
    inspect.ts         inspect.
    write.ts           fill, click (stubs — need a confirmation gate).
  overlay/
    index.ts           Overlay barrel.
    types.ts           PointDirective, HighlightTarget, SpotlightRect, CSTRefId.
    resolve-ref.ts      resolveRefs() — CST ref → live element via a RefResolver.
    use-highlight-targets.ts  Hook: directives → geometry-tracked targets.
    spotlight-canvas.tsx     Pure SVG-mask renderer (scrim, cut-outs, pulse).
    highlight-overlay.tsx    The component: hook + canvas + captions.
```

Commands are one-per-file: adding a capability is a new file in
`commands/`, registered in `commands/index.ts`.

---

## Usage

```tsx
import { HighlightOverlay } from '@djangocfg/widget-chat/browser-bridge';

<HighlightOverlay
  directives={directivesFromLastDirectiveEvent}
  resolver={snapshotRefRegistry}   // the page-snapshot ref registry
  ttlMs={6000}
  onDismiss={() => clearDirectives()}
/>
```

- `directives` — the `directives` array from the latest `directive` SSE
  event. Empty → the overlay renders nothing.
- `resolver` — anything with `resolve(ref) => HTMLElement | null`. The
  `page-snapshot` engine's `RefRegistry` satisfies this. Structurally
  typed on purpose, so this module does not import the capture engine.

In development, `installChatBridge()` exposes the registry on
`window.__chatBridge` — run `__chatBridge.help()` for the command list,
or `__chatBridge.highlight(['@e4'])` to see the spotlight without an
AI / SSE round-trip.

---

## Staleness

A ref resolves against the snapshot that produced it. If the user has
since navigated or the element was removed, `resolve()` returns null (or
the element is detached) — that target is silently dropped. The overlay
only ever shows live elements.

---

## Decoupling notes

- This is infrastructure — "the AI reads and acts on the user's page" —
  and the sibling of `page-tooling/page-snapshot/`. A chat surface is merely a
  consumer. In ui-tools the rule was "`lib/` must never import from
  `tools/`", which is why the bridge carries its own minimal
  `logger.ts`; here the same rule reads as: this module imports no
  viewer, and no viewer's dependency may reach it.
- It does not import the `page-snapshot` capture engine. It depends only
  on the structural `RefResolver` interface, so the two stay
  independent.
- The directive type is `point` only. The shape is a discriminated
  union on `type`, so a future write-style directive could be added —
  but that is a different risk class (it would change user data) and is
  deliberately out of scope here.
