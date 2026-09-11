---
title: Events and Notifications
status: current
version: "3.0"
audience: frontend, agents
last_reviewed: 2026-09-01
---

# Events and Notifications

[State and data](./state-and-data.md) owns **what is true now** — which lane
holds a value, who may write it, how it is read. This page owns the other half:
**that something just happened**, and how one part of a package tells another
without threading a callback through every layer in between.

Both mechanisms are needed, and neither substitutes for the other.

## The dividing line

**A store answers "what is true now". A bus says "this just happened".**

Two identical states can be reached by different acts. A draft holding the text
`"deploy"` is the same snapshot whether the user typed it, restored it from
storage, or pulled it back out of the queue — and a subscriber reading that
snapshot cannot tell which. That difference is the only thing a bus is for. If
a listener would be satisfied by the state alone, it does not need an event.

The corollary: a bus MUST NOT be the mechanism that performs a change. It
announces one that already completed. A bus that carries "now do X" is a second,
untyped API for whatever owns X, and the owner loses the ability to sequence its
own steps.

## Three tests a prop must pass to become an event

Apply all three. A prop that fails any one of them stays a prop.

1. **Is it a notification, or a question?** Anything returning a value — a
   `Promise<boolean>` from a confirm, a three-way choice, a `ReactNode` — stays
   a prop. An event has no return channel, and a bus that grows one is a
   function call with extra indirection.
2. **Is it read during render?** A prop whose VALUE decides what renders, or
   whose mere PRESENCE gates whether a control appears at all, stays a prop.
   The bus is for effects. A listener writing state during render is the
   render-loop failure this codebase keeps rejecting.
3. **Does it actually cross layers?** One parent handing a callback to its own
   child is not coupling. An event there adds a subscription and removes
   nothing.

The pressure this relieves is real and measurable: a component that grows one
prop per "someone downstream needs to know" reaches dozens, and every layer
between the knower and the reactor carries a parameter it does not use. Where a
package caps its prop count, that gate exists for the same reason.

## Naming

`subject:verb`, past tense — `queue:taken`, `turn:sent`, `draft:written`.

An event states what HAPPENED. A name in the imperative (`focus:composer`) is a
command wearing an event's clothes, and admits exactly the "bus performs the
change" failure above. If the only name that fits is imperative, the thing is a
command: give it a method on the owner, not an event.

## Shape

- **One typed map, no untyped escape hatch.** The event name and its payload
  are declared together, so a wrong payload is a type error rather than a
  listener that silently never matches.
- **One bus per unit of isolation, never module-scoped.** Two of the same
  surface open side by side must not hear each other. A singleton cannot
  express that; a per-instance bus created beside its store can.
- **Created by ref, not by render.** A bus rebuilt on re-render leaves every
  existing subscription attached to a dead instance — and nothing fails, so it
  reads as an event that never fires.
- **`on` returns an unsubscribe.** Subscribers are effects; effects clean up.
- **Copy handlers before dispatch.** Fix the listener list at the moment of the
  emit. A `Set` tolerates deleting the CURRENT entry mid-iteration, so a
  one-shot removing itself is safe either way — the case that is not is one
  handler unsubscribing ANOTHER, which without the copy is silently skipped for
  that emit. Everyone listening when the event happened hears it.

Declare the bus in the package that emits. Modelling its shape on an existing
one is right; importing it across a boundary the package otherwise does not
depend on is not — a package must not take a transport dependency to talk to
itself.

## Where a store library fits

On the **store** side of the line, not this one.

- A store library owns the snapshot: it backs `useSyncExternalStore`, which
  needs a `getState`. A bus has no `getState` and cannot replace it. Where a
  store already exposes `subscribe`/`notify`, that is not a bus and must not be
  merged into one — two mechanisms, on purpose.
- An immutable-update helper owns how that snapshot is *updated*: a patch
  expressed as mutation, applied structurally. It has no bearing on
  notification.

**MUST**: a shared package declares a store library as a **peer** dependency,
never a bundled one, and mirrors it into `devDependencies` for its own tests.
The reason is [architecture and ownership](./architecture-and-ownership.md): a
package that ships its own copy gives the host two installed versions, and a
hook from one cannot read a provider from the other. Nothing fails at build
time; the symptom is a component that reads an empty store beside one that reads
a full one. Let the consuming app own the single installed version.

A store update and an event are frequently both correct for one act — the store
records the new truth, the bus announces the act. Emit AFTER the state settles,
never as part of settling it.

## Sequencing traps

These are where migrations to a bus go wrong. Check each before moving a
callback.

- **Two callers, opposite orders.** When two paths reach the same end state by
  ordering their steps differently — one writes then removes, the other removes
  then writes — that asymmetry is usually deliberate, protecting a cancel path.
  Emitting from the shared step and letting a listener perform the other one
  silently inverts one of them. Emit as a notification after BOTH steps
  complete.
- **Deliberately optimistic timing.** A callback fired before the state it
  describes has settled is sometimes exactly right, because something
  downstream must observe the intent before the result lands. Moving the emit
  into the owner "for tidiness" regresses that, and the regression is a timing
  window no test written after the move would think to cover.
- **Feedback through a persistence layer.** If a save path watches the value a
  listener writes, restore → emit → write → save → restore is a loop. Establish
  that one of the two is the only writer before wiring the second.

## Verification

A bus is invisible to the typechecker beyond its map, so assert behaviour:

- Handlers registered for a name receive the emit; handlers for another do not.
- Unsubscribing stops delivery.
- **The mid-dispatch case, explicitly**: register a handler that removes a
  DIFFERENT one, and assert the removed handler still received this emit.
  Registration order matters for this test — the remover must run first — and
  a test written around self-removal asserts nothing, because that case passes
  without the copy.

Every one of these needs to fail on the mutant it names. Delete the handler
copy; if the suite stays green, the test is describing a mechanism the code
does not have.
