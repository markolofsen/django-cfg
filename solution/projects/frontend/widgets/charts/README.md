# @djangocfg/widget-charts

Small data visualisations: five charts and three indicators.

## Install

```bash
pnpm add @djangocfg/widget-charts @djangocfg/ui-core
```

| Subpath | What |
|---|---|
| `./activity-graph` | a GitHub-style contribution calendar |
| `./commit-graph` | a branch/merge graph beside a commit list |
| `./sparkline` | a bare trend line |
| `./smooth-line` | a monotone-cubic line with axes and points |
| `./gauge` | a single value on an arc |
| `./fps` | a live frame-rate readout |
| `./rating` | stars, read-only or interactive |
| `./status-indicator` | a dot with a state and a label |

Each also exports a `Lazy*` wrapper.

## Why one package

They share a shape, not a library: each is a few hundred lines of SVG or canvas
over `@djangocfg/ui-core`'s palette, and none carries a charting dependency the
others would pay for. Eight packages of one file each would be worse for
everyone — the root barrel here costs nothing.

## Verify

```bash
pnpm --filter @djangocfg/widget-charts check-types test
```
