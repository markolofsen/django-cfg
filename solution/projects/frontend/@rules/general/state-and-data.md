---
title: State and Data
status: current
version: "3.0"
audience: frontend, backend, agents
last_reviewed: 2026-09-01
---

# State and Data

Choose state by ownership, lifetime, and arrival mechanism. Library preference
comes last.

This page owns **what is true now**. When a subscriber needs to know that
something HAPPENED — a difference two identical snapshots cannot express — see
[Events and notifications](./events-and-notifications.md).

## Classify before implementing

| State class | Examples | Default owner |
|---|---|---|
| URL-addressable | selected entity, section, shareable filter | router URL |
| Server pull | profile, settings, paginated list | query cache |
| Server push/read model | presence, transcript deltas, live activity | external store attached once |
| Cross-route client session | auth, open work tabs, uploads | external store |
| Persisted preference | theme choice, density, last safe filter | storage-backed preference store |
| Feature workflow | wizard phase, mutation state, draft | reducer/local state or scoped store |
| Ephemeral view state | hover, one popover, input focus | component state or the DOM |
| Derived value | filtered rows, status label, permissions | compute from source state |

Do not mirror URL or server cache data into local state unless editing requires a
draft. If a draft exists, define reset, conflict, and save behavior.

## The three data lanes

### 1. Query cache for pull data

Use the product's public domain-state facade for request/response reads. A
generated query hook or query wrapper MAY implement that facade privately.

- Keys MUST describe the resource and all inputs that change the result.
- Use one configured provider for focus/reconnect policy, auth, deduplication,
  and slow-load instrumentation.
- Preserve previous data during revalidation when the identity remains useful.
- Mutations MUST invalidate or update the canonical key, not a component-local
  copy.
- Feature and shell presentation MUST NOT import generated query hooks, declare
  cache keys, or call raw query-cache mutation.

### 2. Read-model store for push data

Use a module-level external store when data arrives as WebSocket/SSE/native
events or must survive route unmounts.

- Attach subscriptions once at application bootstrap.
- Seed with a snapshot when possible, then fold deltas.
- Reconcile after reconnect; never assume no missed events.
- A delta may only mark the store synchronized for the facts it actually
  carries. When one entity in the snapshot produces several derived rows, an
  event naming that entity does not describe them — fold it, then reconcile.
  Advancing a cursor on such an event silences the refetch that would have
  brought the rest, and nothing fails: the rows are simply missing until the
  next unrelated read.
- Expose `loaded`, freshness, and error separately from an empty collection.
- Return and call cleanup functions in tests, a scenario workbench, and any
  non-global host.

### 3. Transport/controller wrapper

Use a query wrapper over a controller when the raw generated hook cannot express
the required boundary behavior: feature detection, normalized unavailable
state, DTO mapping, auth ceremony, or host capability.

Do not create one wrapper per screen. Create one reusable seam, then let feature
hooks project its generic load state into domain-specific names.

## Calling a generated API client

A generated client is the contract, so hand-writing a URL, a wire interface, or
a query string beside one is a second copy that drifts. Call the operation.

What a generator does NOT hand you is error semantics, and that is where the
traps are. Every trap below has been measured against a real generated client;
which of them apply depends on the generator, so **probe your own before
assuming** — each is cheap to confirm and expensive to discover in production.

**A thrown value may carry no status.** With `throwOnError: true` the client
throws the parsed response BODY — an object with no `status` field. So this
compiles, type-checks, and never matches:

```ts
try { await X.call({ throwOnError: true }) }
catch (err) { if (err.status === 404) return null }   // dead branch
```

The expected empty state becomes a thrown failure at a caller documented as
never throwing, and nothing fails at build time. **Rule:** `throwOnError: true`
only where EVERY non-2xx is a real error. If any status is a legitimate outcome,
omit it and read the status off the response:

```ts
const response = await X.call({ path });
if (response.response?.status === 404) return null;
if (response.error) throw response.error;
return map(response.data);
```

**A non-JSON answer may arrive as data, not as a failure.** The client picks its
parser from `Content-Type`. A server that answers an unknown route with an HTML
document (an SPA catch-all, a proxy error page) therefore produces a `200` whose
`data` is a STRING typed as the operation's payload. Nothing throws; the caller
maps a document as if it were its own DTO. Guard any call that a stale or
mismatched backend might not serve, and translate it into an honest
"unsupported" at the transport seam rather than at each caller.

**Absent is not empty.** `data === undefined` means the server said nothing;
defaulting it to `[]` renders a broken surface as an empty one. Distinguish them.

**A generated type may be WEAKER than the hand-written one it replaces.** A
backend's list type commonly reflects as `nullable`, and an omit-when-empty
string as optional, whatever the server's own comment promises. Those nulls
surface at the boundary, which is
where they belong: coalesce them into the domain shape rather than casting them
away. A cast that silences the error also discards the one signal that the wire
can send something the screen cannot render.

**A URL string is the right answer when the BROWSER performs the request.** A
`<video src>`, an `<img src>` or a streaming player's own fetch navigates on its
own, so it needs a string; a generated call that resolves to a `Blob` cannot be
handed to one. That is also why such routes commonly accept their credentials in
the query — a media navigation cannot set a header. Route the CALLS through the
generated client and keep one URL builder for the navigations; do not "finish
the migration" by replacing a `src` with a client call.

**Cache a boot fact by the OPERATION, not by a URL.** A path-keyed cache makes
every writer repeat the reader's URL as a string, so one endpoint lives in two
places that no gate compares — and the generated client already owns that URL.
Key on the read function's identity instead, so an invalidation names the fact
it forgets and a renamed route cannot strand a key. Reserve such a cache for
facts that change only through a write this application performs; anything the
host can change underneath needs a freshness policy instead.

### Testing a call that goes through a generated client

Generated clients typically call `fetch(new Request(...))` — one argument. A
test that stubs `fetch` and reads `args[0]` as a URL string gets
`[object Request]`, and one that spies on an internal transport method asserts
against a layer the call no longer passes through: green while the request it
actually sends goes unchecked.

Stub the network and assert the real request — path, and body via
`await input.clone().json()`. This is strictly stronger than the mock it
replaces, because it proves the URL as well as the mapping.

## The single-facade product profile

A product MAY adopt a policy where every global business read-model and action
is exposed through domain-focused state hooks, whatever library backs them. Once
adopted, this keeps cache identity, mutations, live events, and transport
lifecycle out of feature code.

That policy means "one product-state facade", not "put every UI value in a
store". The following boundaries remain:

- The router owns durable URL state.
- React or the DOM owns ephemeral component state.
- Theme, locale, tooltip, and overlay runtimes keep their providers.
- The store owns global domain/read-model state only when it is the canonical
  owner, or a non-caching facade over one canonical engine.
- Where a query cache remains the canonical engine for ordinary pull reads, keep
  its types, keys, generated hooks, and raw cache-mutation calls private to the
  state package.
- Bootstrap configures each transport port and attaches each global live owner
  once. Screens never attach or reconfigure them.

If a store becomes the canonical owner of pull data, the architecture MUST
provide the query semantics it replaces: stable keys, request deduplication,
freshness, stale-while-revalidate, focus/reconnect policy, cancellation, race
protection, mutation invalidation, optimistic rollback, pagination, and memory
eviction. That list is the real price of the migration, and skipping any line of
it produces a cache that works until the second tab.

Do not fetch through the query cache, copy the result into a store, and let both
remain canonical. Either keep the query cache as the single owner behind a
deliberate domain API, or migrate ownership completely and remove the old cache
consumer. Adopt such a profile through an inventory and a phased vertical slice,
not a big-bang rewrite.

## Async state model

Avoid `isLoading + hasError + data` boolean combinations that permit impossible
states. Use a discriminated model or a centrally derived phase:

```ts
type LoadState<T> =
  | { kind: "unavailable" }
  | { kind: "loading" }
  | { kind: "ready"; data: T; refreshing: boolean }
  | { kind: "error"; message: string; previous?: T };
```

The exact type MAY differ. The visible states MUST remain mutually intelligible.

## Freshness and honest degradation

- Distinguish "never loaded" from "loaded and empty".
- Distinguish "the host was unreachable" from "the host returned an error".
- Keep last-known data when it remains safe and label it stale when freshness
  affects a decision.
- Do not infer healthy from the absence of an error.
- Do not infer stopped from the absence of a status response.
- Time-sensitive decisions MUST define a freshness window.
- Match the loading surface to the lane's latency, and know which lane each read
  is on. A slow remote lane — anything crossing a proxy or a second backend —
  renders a reserved-height skeleton in "never loaded", so the surface cannot
  reflow when the answer lands. A fast local lane MAY render its calm empty or
  guide state directly. Rendering NOTHING in "never loaded" is never an option
  for a slow lane: content that pops in seconds later reads as a bug, not as
  loading.

## Optimistic mutations

Use optimism when success is likely, rollback is clear, and the user benefits
from immediacy.

1. Capture the previous canonical snapshot.
2. Apply the optimistic update to the canonical cache/store.
3. Send an idempotent mutation where possible.
4. Replace with server truth on success.
5. Roll back and explain on failure.

Do not optimistically claim destructive, billing, permission, or security
changes succeeded unless the domain explicitly supports safe reconciliation.

## External-store discipline

- **Never write to a subscribed store during render.** `store.getState().set…()`
  in a render body is a cross-component update; React discards it and takes the
  commit with it, so the screen keeps the previous value while the URL and the
  store both moved on. Nothing throws — the only signal is a console warning
  naming the two components. Writes belong in an effect. Mutating a plain
  transport object during render is fine and sometimes required; the rule is
  about stores something else subscribes to.
- Select the smallest stable slice needed by the component.
- Keep actions explicit; avoid write access to arbitrary state fields.
- Persist only user-beneficial state, with a version and migration strategy.
- Never persist secrets or ephemeral auth material by convenience.
- Keep derivations out of stored state unless computation is expensive and
  invalidation is exact.
- Stores MUST not reach for a second client instance or configure auth.

## React derivation and memoization

Prepare the complete render model before JSX: derived values, formatted copy,
conditional nodes, mapped collections, variants, class names, and event
handlers. JSX composes prepared values and nodes; it does not perform business
or presentation decisions.

- Do not put `map`, `filter`, `find`, formatting calls, ternaries, boolean
  render branches, or newly-created callbacks in returned JSX.
- Prepare repeated nodes before the return. Extract a small child component
  when preparing the nodes would make the parent harder to read.
- A named handler MAY be an ordinary function. Memoize it only when identity is
  part of a child, effect, or subscription contract.

- Use `useMemo` for measured expensive work or required referential stability,
  not as a ritual.
- Use `useCallback` when identity affects a memoized child, subscription, or
  effect, not for every handler.
- Pure helpers belong at module scope when they do not need component closure.
- Do not use effects to derive state that can be calculated during render.

## Continuous values

Pointer coordinates, scroll progress, animation frames, and media time SHOULD
not enter React state on every frame. Use CSS, animation values, browser APIs,
or an external store designed for high-frequency updates.

## Data review

- Is the state in the URL if a reload or shared link should preserve it?
- Is pull data in one query cache and push data in one read model?
- Are empty, unavailable, stale, and error distinct?
- Does every status a caller branches on come from the RESPONSE, never from a
  thrown value's assumed `.status`?
- Is the mutation updating the canonical source rather than a shadow copy?
- Can reconnect recover missed events?
- Is memoization solving a demonstrated identity or cost problem?
