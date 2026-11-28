# @djangocfg/widget-overlay

Surfaces that sit over the page rather than in its flow.

## Install

```bash
pnpm add @djangocfg/widget-overlay @djangocfg/ui-core
```

| Subpath | What |
|---|---|
| `./responsive-dialog` | one API that is a dialog on desktop and a drawer on mobile |
| `./scroll-spy` | a nav that follows the reader's position |
| `./selection-toolbar` | actions that appear over a text selection |
| `./tour` | a step-by-step product tour |

## Why one package

That is what they share: each takes over part of the viewport, each has to
reason about focus, scroll and escape, and none carries a dependency the others
would pay for. They are `@djangocfg/ui-core` primitives with behaviour, not a
design system of their own.

## Verify

```bash
pnpm --filter @djangocfg/widget-overlay check-types test
```
