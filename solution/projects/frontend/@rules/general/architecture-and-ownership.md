---
title: Architecture and Ownership
status: current
version: "3.0"
audience: frontend, backend, platform, agents
last_reviewed: 2026-09-01
---

# Architecture and Ownership

Architecture exists to make change local. Every concept needs one owner, a
small public contract, and dependencies that point toward stable layers.

## Reference dependency flow

Package names vary, but the responsibilities remain:

```text
domain        pure product language, schemas, state machines
api           generated wire contracts and low-level clients
transport     host protocols, auth, streaming, error normalization
stores        public domain-state facades, read models, global workflows
ui            product-agnostic composition and visual primitives
widgets       self-contained blocks liftable into another product
features      user workflows and domain presentation
shell/app     routes, providers, authentication gates, host wiring
```

Allowed dependencies SHOULD point downward or sideways through an explicit
public contract. The app shell composes; it does not absorb feature logic.

### The widget direction

Where a repository separates a **widget** tier — self-contained blocks meant to
be liftable into another product — the direction of dependency is the whole
point of the split.

**MUST**: a widget may depend on a package; a package MUST NOT depend on a
widget. The reverse edge makes the block unliftable, which is the only property
the separation protects.

**A screen layer is the one defensible exemption**: it composes widgets the way
the app shell does, and sits among the packages only because nothing has moved
it. State such an exemption in the checker WITH its reason, so a reader can tell
a decision from an oversight, and do not add a second one to make an import
compile.

A gate SHOULD enforce this mechanically, and it SHOULD read the package
**manifests** rather than the import statements: a dependency a package does not
declare cannot resolve, so the manifest is the enforceable boundary and an
import scan is a proxy for it. Nothing runs such a gate on a schedule — it fails
when a person runs it, so an undeclared edge added today is found at the next
manual pass. The repository profile names the command.

## Layer responsibilities

### Domain

- MUST be framework-independent where practical.
- Owns product terms, discriminated states, validation schemas, and stable IDs.
- MUST NOT expose generated transport types as the product model.

### API and transport

- Generated API code owns the wire shape and MUST NOT be hand-edited.
- An HTTP operation the schema contract already describes MUST be invoked
  through its generated method or hook. Hand-written callers MUST NOT duplicate
  generated paths or wire DTOs — a second spelling of one endpoint is a copy
  nothing compares.
- Transport owns HTTP, WebSocket, SSE, native bridges, tokens, retries, and
  protocol-specific errors.
- A generated query hook MAY be consumed only at a state/transport adapter
  boundary. Presentation MUST depend on a domain contract rather than a wire
  hook, cache key, or generated mutation helper.
- A controller/transport seam SHOULD be used when auth ceremony, feature
  detection, DTO shaping, streaming, or error semantics differ from the raw
  generated client.

The goal is not "generated code is forbidden above transport". The goal is one
configured wire client and no wire-specific policy leaking into presentation.

### Stores

- Own the public domain-state API for global product reads and actions.
- Own pushed read models, cross-route sessions, and durable client state.
- MAY facade one private query cache without copying its data into a second
  canonical store cache.
- MUST NOT become a cache for every GET request merely to claim store
  ownership.
- MUST expose narrow selectors, strict actions, reset/dispose seams, and
  explicit lifecycle wiring.
- MUST receive the configured transport capability from application bootstrap;
  a store never constructs or configures a second HTTP client.
- Derived presentation data normally belongs in a pure view-model projection,
  not persisted in the store.

### UI

- Shared library UI is domain-neutral.
- Product UI may know product concepts but MUST accept navigation and host
  actions as intents when this preserves portability.
- Shared components MUST have a real second consumer or a stable cross-feature
  contract. Do not create a generic abstraction in anticipation.

### Features and shell

- Features own workflows, view models, local errors, and visible states. They
  consume public domain-state facades and do not know cache keys, raw cache
  mutation, generated client configuration, or subscription lifecycle.
- The shell owns route topology, global provider composition, auth gates,
  top-level overlays, and host-specific navigation.
- Features SHOULD emit `onOpenThing(id)` rather than importing application URL
  literals. Shell adapters translate intent into typed paths.

## One owner per concern

| Concern | Typical owner |
|---|---|
| Route topology and typed URL builders | shell/app |
| Authentication session and re-auth gate | one auth store/service |
| REST cache policy | one query provider |
| WebSocket subscription lifecycle | application bootstrap or read-model store |
| Theme mode | one root theme provider |
| Theme values | static semantic CSS tokens |
| Global dialogs/toasts | one root surface/provider |
| Global attention routing and deduplication | one typed application event + shell presenter |
| Feature workflow state | feature hook, reducer, or store |
| Translation key schema | feature-owned locale namespace |

Two owners create races. If two places need the same fact, share its owner or
derive a projection; do not synchronize copies with effects.

## Public package contracts

- Export a deliberate surface from `index.ts` or package `exports`.
- Consumers MUST import public entry points, not internal folders.
- Heavy dependencies SHOULD use explicit subpath exports.
- Keep types and runtime in the same ownership layer.
- Cycles are architectural defects, even when the bundler tolerates them.

## Provider composition

Mount application-wide providers once, ordered from foundational to contextual:

```text
error boundary
  -> theme and locale
  -> authentication / configured clients
  -> query cache
  -> router
  -> router adapter
  -> signed-in shell
  -> global overlays and feature hosts
```

Exact nesting depends on context requirements. A router adapter that calls
router hooks MUST sit inside the router context. Do not nest duplicate tooltip,
toast, theme, query, or dialog providers in screens.

## Boundary errors

Normalize errors at the boundary that understands them:

- transport maps network/protocol failures;
- domain maps validation and business rejection;
- feature maps them to actionable copy;
- error boundaries catch unexpected rendering failures.

Do not stringify an unknown exception directly into user-facing text. Log the
diagnostic detail and show a stable message plus recovery action.

Global attention MUST NOT create a second untyped event channel when the product
already has a typed application bus. Producers emit presentation-light facts
(semantic key, scope, severity, stable copy); the root presenter owns the design
system toast API and deduplication. Raw errors, callbacks, JSX, cache keys, and
transport objects do not cross the event payload.

Application bootstrap MUST isolate optional domains. Authentication resolution,
roster wiring, settings wiring, and live subscriptions are not one all-or-nothing
transaction. A failed optional adapter degrades its own capability and remains
observable without resetting an accepted session or preventing unrelated domains
from starting.

## When to add a backend endpoint

Add or reshape an endpoint when it improves a product contract, not merely to
avoid a few frontend lines.

Good reasons:

- the UI needs one consistent snapshot across related values;
- client composition causes avoidable latency or authorization complexity;
- pagination/filtering must happen before large data crosses the wire;
- a mutation needs transactional semantics or idempotency;
- the backend can express a safer capability-oriented operation.

Weak reasons:

- formatting a label;
- hiding a stable client-side derivation;
- duplicating an existing cache key under a new aggregate endpoint without a
  measured consistency or latency problem.

Document freshness, authorization, error model, idempotency, and compatibility
for every new contract.

## Architecture review

- Can this feature be changed without editing unrelated layers?
- Is every state and side effect owned once?
- Are wire types prevented from becoming accidental product language?
- Does a shared abstraction have a stable contract and real reuse?
- Are providers mounted once at the lowest common correct scope?
- Is backend work solving consistency, safety, or latency rather than taste?
