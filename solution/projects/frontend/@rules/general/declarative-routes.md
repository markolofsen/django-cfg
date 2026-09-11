---
title: Declarative Routes and Links
status: current
version: "2.0"
audience: frontend, design, agents
last_reviewed: 2026-09-01
---

# Declarative Routes and Links

Every internal destination MUST be constructed by the application route
registry. Components, feature modules, and navigation data MUST NOT concatenate
internal path strings or serialize their own query parameters.

The registry is an application-shell concern. It owns route identity, static
roots, dynamic-segment builders, typed query shapes, the labels navigation
renders, and any canonicalization policy. That gives the product one place to
change a path without silently breaking links, browser history, or deep links —
and it is why a rename is one edit rather than a repository-wide literal search.

## The two owners

The registry splits into two responsibilities, whatever the files are called:

```text
route roots      the whole URL space, as literals — nothing else declares one
path builders    every URL carrying a dynamic segment or a query, plus the
                 canonical query-parameter names
```

- Roots are literals in exactly one module.
- A builder owns every URL with a dynamic segment or a query.
- Query parameter NAMES are centralized so two features cannot disagree about a
  spelling.
- **Encoding belongs to the builder.** An identifier is not automatically
  URL-safe: an ID containing `:` or `/` survives an explicit slug/unslug pair
  and is destroyed by a hand-built template literal, which then produces a route
  that resolves to nothing. The failure is silent, because the malformed URL is
  a perfectly valid string.

Query types MUST use product IDs or narrow unions, not arbitrary strings,
wherever the domain knows the allowed values. A union makes an unhandled value a
type error; a `string` makes it a screen that renders the default and reports
nothing.

## The URL is the state, and nothing may answer beside it

A screen's destination lives in the address. A component MUST NOT keep a second
variable that can answer the same question, because the two disagree the moment
a browser Back, a shared link, or a resize changes one without telling the
other.

The shapes it takes:

```ts
const effectiveId = activeId ?? internalId;   // memory answers when the URL does not
```

That line lets a remembered pick survive a navigation: Back changes the address
and the frame while the old subject stays on screen. A local boolean beside an
addressed selection is the same defect one layer up — four such flags once lived
in one component under four different names, each disagreeing with the URL in a
different case, and none of them wrong on its own line.

- Derive from the address; never mirror it.
- Where an address genuinely cannot express a state, give the state its own
  address rather than a boolean (see the two sections below).
- A pick NAVIGATES. Patching the current query instead narrows whatever path
  happens to be open: a pick made from a list route produced `<list route>?id=…`
  — still the list — so the row read as dead while behaving exactly as written.

## A subject gets a path; a filter gets a query

| Kind | Form | Example |
|---|---|---|
| One subject, its own screen | path segment | `/items/<id>`, `/settings/<section>` |
| A lens over a list | query | `?filter=online`, `?lens=upcoming` |
| A one-shot arrival intent | query, consumed and stripped | `?show=exposure` |

A subject addressed by query cannot be told apart from its area root — the
pathname is identical — so a frame cannot know whether it is showing a
destination or a list, and neither can a reader looking at the address bar.

Delivered links keep working: where a query form already shipped it stays
READABLE, while every builder emits the path. Read both, write one.

## A menu is a route

An area root always resolves to SOMETHING — a default section, the latest
conversation — so it cannot express "nothing is selected". Where that state
needs a screen, it gets an address: `/<area>/mobile` renders the list with
nothing marked current.

- Register that literal segment BEFORE the dynamic one, or the catch-all
  swallows it. A forgiving param resolver makes this silent: one that turns an
  unknown segment into the DEFAULT section reports nothing, so the menu renders
  as the overview and looks merely wrong rather than broken.
- Derive a Back destination from the address rather than passing it in. Threaded
  screen by screen it becomes something each new screen can forget — and two
  did, keeping a Back that only flipped a pane while the URL still named the
  section.

## A path segment survives the static build

An application shipped as a client-rendered static bundle can still address a
subject by path. Three things have to hold, and they are a SET: any one alone is
not enough.

**1. The server answers an unknown path with the shell.** A static bundle is
not "files without a server" — a handler ships beside the files and returns the
shell document for anything that is not a real asset. The rule is "is this a
file?", never a list of known routes, so nesting depth is irrelevant and a new
route needs no server change. Where no such handler exists — a bare static
server without a fallback rule, a `file://` open — a path segment does NOT
survive and a query is the only option.

**2. Asset URLs are absolute, not relative.** With a relative base, a page at
`/items/<id>` asks the browser for `/items/assets/…` and gets the shell document
back: the app fails with "unexpected token `<`" and points at nothing. This is
the one failure the DEPTH of a URL can cause, and it is why the base is pinned.

**3. Lazy chunks resolve against the IMPORTER, not the page.** They inherit the
importing module's origin AND path prefix, so a deep address changes nothing
about how they load.

Points 2 and 3 are a PAIR, and separating them has already cost an outage: with
a plain root-absolute base the bundler emitted a root-absolute joiner, so a
chunk URL resolved against `https://<cdn>/<prefix>/assets/entry.js` dropped
`/<prefix>/` and every lazy chunk 404'd behind the CDN while the entry loaded
fine. Both halves live in the build config and the deployment's URL rewriting;
neither may be changed alone.

**Verify with a control, not a bare 200.** A server with a shell fallback
answers `200 text/html` for every unknown path BY DESIGN, so a 200 on a deep
route proves nothing. Fetch a real asset in the same command: it must return
`text/javascript` while a made-up one returns the shell. If both look alike the
probe is blind — most often because the process being probed is serving an older
bundle than the one on disk.

## Use in components

Navigation receives a registry result; a router call consumes one too.

```tsx
<Link to={paths.itemDetail(item.id)}>{item.name}</Link>
```

```ts
const next: ListView = view === "table" ? "calendar" : "table";
navigate(paths.list({ view: next }), { replace: true });
```

Use a real link for a destination and a real button for an action. Do not style
a `button` as navigation, and do not rebuild a route from the current location
plus a template literal. Parse URL input once at the route or feature edge,
validate it against domain values with a named guard, and pass the resulting
typed object to the builder.

A row that navigates MUST carry an `href`, not only a click handler: without it
there is no open-in-new-tab, no modifier-click, and no visible destination. A
menu whose rows had ids but no hrefs is how one area's picks silently patched
the current query instead of navigating.

Navigation menus derive from registry entries rather than copied strings, so a
moved route cannot leave a stale rail item behind.

## Navigation out of a working surface is deliberate

A control that sits inside a composer, a transcript, or any surface a reader is
typing into MUST NOT navigate on a single click. On a phone the control is a
thumb's width from the send button, and a mis-tap costs the room being worked
in.

Offer the destination as a button inside a popover or a confirm, so leaving is a
second, deliberate act. Where the control has no destination to offer, render it
as a report rather than a dead door — opener-or-nothing, never a disabled link.

## Registry rules

- Internal JSX MUST NOT contain `to="/…"` or ``to={`/…`}`` literals.
- Internal `navigate`, redirects, breadcrumbs, cards, menu entries, and CTA
  links MUST use the registry.
- External URLs and `mailto:` links have separate, explicitly named external
  link owners. They do not belong in internal route builders.
- A builder returns a canonical URL. Invalid or unsupported URL input is parsed
  at the consuming feature and recovered with a visible state or a reset, never
  by rendering a broken destination.
- The registry stays framework-light: strings and types only. It MUST NOT import
  React, hooks, or feature components.
- Features emit navigation intents rather than importing shell topology. A
  reusable component SHOULD accept an href or an intent from its caller.
- A redirect alias is a registry entry with a stated reason and, where the alias
  exists only for links already delivered, a removal condition.
- A route added for one viewport still resolves on every other. Redirecting it
  by width makes a shared link open something the address does not name, and
  swaps the screen out from under a reader who merely resized a window.

## Review checklist

- Is each durable destination represented exactly once in the registry?
- Are dynamic segments encoded through the builder and query keys centralized?
- Does every internal link, navigate call, breadcrumb, and menu entry derive
  from a registry entry?
- Is anything answering the same question as the URL — a `??` fallback, a local
  flag, a remembered pick?
- Does a subject have a path and a filter a query?
- Are query values typed and validated before they change visible results?
- Does a renamed route require one registry change?
- Does a new path-addressed subject still resolve under the static build, proved
  by a probe whose control distinguishes an asset from the shell?

Product-specific route decisions — which navigation surface owns which section,
which aliases are retained, what redirects where — belong in the repository's
own product-invariants page, not here.
