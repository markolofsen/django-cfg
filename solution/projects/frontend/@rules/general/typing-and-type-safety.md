---
title: Typing and Type Safety
status: current
version: "3.0"
audience: frontend, agents
last_reviewed: 2026-09-01
---

# Typing and Type Safety

The typechecker is the only gate that reads TYPES across the whole frontend.
A bundler transpiles per-module and never checks them. Other deterministic
gates exist (see [Verification](#verification)) but each answers a narrower
question, so a type that stops describing reality is not a style problem — it is
the failure of the one thing that could have caught the bug.

## `any` is forbidden

**MUST NOT** write `any` in hand-authored source. Not as an annotation, not as
a cast, not as a type argument, not in a `.d.ts` you own, and not in tests.

This is not aspirational: the rule holds the line rather than asking for a
migration, and it is measurable — a census over every non-generated file should
return zero hand-written `any`.

Scan **every** product source root the repository has, not the one you think of
first. A census that omits a root reports a clean result it never looked for,
and the omitted root is usually the newest group of packages — the one most
likely to have taken a shortcut.

`any` is not "unknown". It is **an instruction to stop checking**, and it
spreads: every property read off an `any` is `any`, every value derived from it
is `any`, and each one silently disables the checks around it. A single `any`
at a boundary can disarm a whole call chain that looks typed.

What it costs, concretely: when an import failed to resolve, the constants it
imported became `any`, and the object keyed by them turned into `TS7053` errors
three functions away. The real defect was one wrong path; the type system
reported it as seven unrelated indexing failures, because `any` had already
destroyed the information needed to say what was wrong.

### Use instead

| You have | Use | Why |
|---|---|---|
| A value of genuinely unknown shape | `unknown` | Forces a narrowing before use — the check happens where the knowledge is |
| A wire payload | The generated type from the API package | It is the contract; a hand-written mirror is a second source of truth |
| An object whose keys you do not know | `Record<string, unknown>` | Keys stay strings, values stay unproven |
| A function you do not call | `(...args: never[]) => unknown` | Accepts any function, promises nothing about it |
| A generic that "could be anything" | A type parameter `<T>` | Preserves the caller's type instead of erasing it |
| A third-party module with no types | A local `.d.ts` describing **what you use** | Narrow and honest beats broad and false |

Narrowing `unknown` is the work `any` was avoiding, and it is usually four
lines:

```ts
// BAD — every downstream read is unchecked
function exitCode(output: any): number | null {
  return output.code ?? null;
}

// GOOD — the check sits where the shape is asserted
function exitCode(output: unknown): number | null {
  if (typeof output !== "object" || output === null) return null;
  const code = (output as { code?: unknown }).code;
  return typeof code === "number" ? code : null;
}
```

### Generated code is exempt, and only generated code

A generated client tree may contain `any` and MUST NOT be hand-edited — the fix
for a bad generated type is a change to the source contract plus a regeneration.

The exemption is the DIRECTORY, not the pattern. Copying an `any` out of
generated code into your own file makes it yours.

## The neighbours of `any`

**MUST NOT** use `as` to assert a type the value has not been proven to have.
A cast is a claim the checker cannot verify; `as unknown as T` is that claim
with the evidence deliberately destroyed, and it is never correct.

Legitimate casts are narrow and local: asserting a literal type
(`as const`), or narrowing a `unknown` immediately after a runtime check that
proves it.

**MUST NOT** use `@ts-ignore`. If a suppression is genuinely unavoidable, use
`@ts-expect-error` with a one-line reason — it FAILS when the underlying error
goes away, so it cannot outlive its cause. `@ts-ignore` silently survives
forever.

**MUST NOT** use non-null `!` to silence a possibly-undefined value. It is a
cast with the same properties and worse ergonomics: it produces a runtime
`TypeError` at a line that looks safe. Turn `noUncheckedIndexedAccess` on for
this reason — handle the `undefined` the index access genuinely returns.

**AVOID** widening a parameter to make a call site compile. If a function takes
`string` and you hold `string | undefined`, the question is what should happen
when it is absent — answering it at the call site is the work; widening the
signature moves the same question onto every other caller.

## Boundaries own their narrowing

**MUST**: a value entering from outside the type system — a wire response,
`localStorage`, a URL param, a `postMessage`, a third-party callback — is
narrowed at the boundary module that receives it, and everything downstream
receives a real type.

Narrowing scattered across consumers is how two of them come to disagree about
the same payload, and neither is wrong at its own line.

**MUST**: a generated wire type is mapped into a domain type at the transport
layer, not consumed directly by a feature. The wire shape is the backend's to
change; the domain shape is ours to keep stable.

## Types describe reality, or they are worse than nothing

A type that no longer matches the runtime is a **confident lie** — it silences
exactly the check that would have caught the drift.

**MUST**: when the runtime meaning of a value changes, change its type in the
same edit, even when the old type still compiles. A persisted value that changed
meaning while keeping its shape can pass every test, because the fixtures encode
the same wrong assumption as the code.

**SHOULD**: prefer a discriminated union over optional fields that are only
valid in combination. `{ kind: "error"; message: string } | { kind: "ok";
data: T }` makes the invalid state unrepresentable; four optional fields makes
it merely undocumented.

**SHOULD**: name a type after what it IS, not where it came from.
`ChannelMessage` survives the retirement of the library its shape was borrowed
from; `ChatMessage` imported from a dead package does not.

## Verification

A repository has several deterministic gates. What it does not have is anything
that runs them on a schedule — **a person runs them**, so a rule they would
catch is still upheld by whoever is editing until someone does.

The repository profile names its gates: which one decides types, which one runs
the lint rules that ban `any`, and which of them are fast enough to run at the
end of an edit. Know the coverage boundary between them. Where the typecheck
does not lint, the `any` ban bites only when someone runs the linter, and a
green typecheck says nothing about it.

Two lint rules SHOULD be `error` wherever hand-authored source lives:
`@typescript-eslint/no-explicit-any` and `ban-ts-comment`. Applying them to one
package group and not another leaves the rule true only where it was configured.

To answer "is there an `any` here" without waiting for a lint pass, grep for the
pattern across every product source root, excluding generated directories.
Quote any `--include` glob: unquoted, the shell expands it before `grep` sees
the flag, and the zero that follows is the query failing, not the tree being
clean.

Prefer a per-package typecheck while working — seconds, versus minutes for a
whole workspace — and batch the workspace-wide gates into one pass at the end.
