---
title: Stylesheets and Class Lists
status: current
version: "3.0"
audience: frontend, agents
last_reviewed: 2026-08-26
---

# Stylesheets and Class Lists

Utility classes are the default. This page is about the two places they stop
paying: when a rule needs a selector a class cannot express, and when a class
list has grown past the point a reviewer can read a mistake out of it.

[Tokens, themes, and styles](./tokens-themes-and-styles.md) owns WHICH values to
use. This owns WHERE the rule lives.

## Move a rule into a stylesheet when

- **The selector looks somewhere a class cannot.** A class styles the element it
  sits on. `:has()` looking down at a descendant, a rule that acts on a
  *sibling*, `:not([data-action="edit"])`, `:focus-within` on a container — none
  of these have a class-list form that stays legible.
- **The condition is structural, not stateful.** State that a component knows
  belongs in the component. "Every child except the one carrying this attribute"
  is structure, and it belongs beside the markup contract.
- **The list has outgrown review.** The measure is not a character count; it is
  whether a reviewer would notice a wrong bracket. An arbitrary variant repeated
  per property (`[&>button:not([data-action='x'])]:grid`,
  `…:size-6`, `…:opacity-0`, nine of them) reads as noise, and noise is where a
  typo lives unseen.

Keep it a class list when the rule is ordinary layout on the element itself.
Moving those to CSS buys nothing and costs the reader a second file.

## One owner per element

Do not split an element's styling across both. A row whose geometry is in a
class list and whose reveal-on-hover is in CSS has two places to look and two
places to forget. Pick the one that can express the whole rule, and put all of
it there.

When a component takes styling through a prop (`itemClassName`,
`chipClassName`), that prop is the seam: either the host passes a full class
list, or it passes ONE semantic class and the package's stylesheet owns the
rest. A prop carrying half of each is the shape to avoid.

## Decompose a package stylesheet by subsystem

A package's stylesheet grows until "is this rule still used?" becomes a question
about the whole file. Split it by the thing each group styles, one file per
subsystem, under `styles/`, and keep the published entry point as a list of
imports:

```
src/styles/index.css    ← the entry: doc comment + @import list, nothing else
src/styles/composer.css ← layout the composer's markup breaks without
src/styles/markdown.css ← how rendered message content reads
src/styles/ask.css      ← one component's own skin
```

Keep the entry INSIDE the folder as `index.css`, not beside it under the
package's own name. One directory answers "where are the styles", and the
`exports` map keeps pointing at the entry, so no consumer is affected. The
reason to split on SUBSYSTEM rather than on rule type is ownership: those three
answer to different questions, and a change to one should not require reading
the others.

Apply the same shape to any grouped set the package owns — a `locales/` folder
of dictionaries beside its `index.ts` reads the same way, and lets a directory
scan mean "every file here" with no exception list a new helper could join.

## A stylesheet a test reads

A rule that no test can see is a rule that silently rots — and CSS is the usual
place that happens, because no typecheck reaches it. Where a stylesheet carries
a load-bearing rule, assert it.

Read the entry point's `@import` list rather than naming files. Resolve those
paths against the ENTRY's directory, not the test's — they are relative to the
file that declares them:

```ts
const STYLES = join(import.meta.dirname, "styles");
const ENTRY = readFileSync(join(STYLES, "index.css"), "utf8");
const CSS = [...ENTRY.matchAll(/@import "\.\/([^"]+)"/g)]
  .map(([, path]) => readFileSync(join(STYLES, path), "utf8"))
  .join("\n");
```

A hardcoded filename goes stale the next time a sheet is split out, and a
missing file reads exactly like a missing rule.

A test that asserts ONE component's rule should read that component's sheet
directly (`styles/ask.css`), not the entry — the entry holds only imports, and
pointing a substring search at it finds nothing while looking correct.

**Assert the size before the content.** Every substring assertion passes over an
empty string, so an import list that resolved to nothing would turn the whole
suite green. One length check ahead of them is what separates "the rule is
there" from "I could not see".
