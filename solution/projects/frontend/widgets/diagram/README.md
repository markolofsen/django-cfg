# @djangocfg/widget-diagram

Mermaid diagrams, both halves: typed builders that WRITE the source, and a
full-parser renderer that DRAWS it. Supports the diagram types covered by the builders (`FlowDiagram`,
`SequenceDiagram`, `JourneyDiagram`) plus anything else Mermaid parses (gantt,
class, state, ER, pie, mindmap, …) via the `chart` prop. Click-to-fullscreen
via the floating toolbar.

## Install

```bash
pnpm add @djangocfg/widget-diagram @djangocfg/ui-core
```

## Which renderer

`@djangocfg/widget-media/diagram` is the OTHER one, and it is not a duplicate.

| | `widget-diagram` | `widget-media/diagram` |
|---|---|---|
| Parser | `mermaid`, ~84 MB unpacked | `beautiful-mermaid`, ~2 MB |
| Covers | everything mermaid parses | flowchart, sequence, state, class, ER — source otherwise |
| For | a surface whose job IS the diagram | a chat transcript, where most messages have none |

Do not import both into one app.

## Builders without a renderer

```ts
import { FlowDiagram } from '@djangocfg/widget-diagram/builders';
```

The `./builders` subpath holds no static edge to the parser, so a server pass,
a test or a CLI can write diagram source without resolving a renderer.
`src/entries.test.ts` walks the graph and holds that.

## Verify

```bash
pnpm --filter @djangocfg/widget-diagram check-types test
```

```tsx
import Mermaid from '@djangocfg/widget-diagram';

<Mermaid chart={`
flowchart LR
  A[Client] --> B[API] --> C[(DB)]
`} />
```

Builder API:

```tsx
import Mermaid, { FlowDiagram } from '@djangocfg/widget-diagram';

const chart = new FlowDiagram({ direction: 'LR' })
  .node('a', 'Client')
  .node('b', 'API')
  .edge('a', 'b')
  .build();

<Mermaid chart={chart} />
```

## Props

| Prop | Type | Default | Description |
|---|---|---|---|
| `chart` | `string` | — | Mermaid source. |
| `isCompact` | `boolean` | `false` | Tighter padding for embedded contexts. |
| `fullscreen` | `boolean` | `true` | Click-to-fullscreen via the floating toolbar. |
| `scrollIsolation` | `boolean` | `false` | Lock page wheel while hovering. Off by default — Mermaid SVGs don't scroll, the overlay just steals wheel events. |
| `debounceMs` | `number` | `300` | Re-render debounce after `chart` changes. Lower for static diagrams, higher while streaming. |
| `className` | `string` | — | — |

## Notes

- **~800KB bundle** — entry point is already `lazy()`-wrapped with a `Suspense` spinner, so the cost is only paid when a diagram is actually mounted.
- Theming pulls from `useThemePalette` / `useStylePresets` / `useBoxColors` (exported alongside the builders) — Mermaid colors follow the active app theme; do not hard-code hex.

---

Adapted from jalcoui (MIT).
