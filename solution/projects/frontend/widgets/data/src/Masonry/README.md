# Masonry

Virtualised Pinterest-style masonry grid. Items of arbitrary heights are
placed into N columns; each new item lands in the currently-shortest
column. Window-scroll virtualised — only items within the scroll
overscan are mounted, so the layout scales to thousands of tiles.

```tsx
import { Masonry, MasonryItem } from '@djangocfg/ui-tools/masonry';

<Masonry columnCount={3} gap={12}>
  {items.map((item) => (
    <MasonryItem key={item.id} className="rounded-md border bg-card p-4">
      <h4>{item.title}</h4>
      <p>{item.body}</p>
    </MasonryItem>
  ))}
</Masonry>
```

## Picking the column model

Pass **either** `columnCount` **or** `columnWidth` — not both.

| Mode | Use when | Behaviour |
| --- | --- | --- |
| `columnCount={n}` | You want exactly N columns regardless of width | Column width = `(container - gaps) / n` |
| `columnWidth={px}` | You want responsive columns | Column count = `floor(container / (px + gap))`, clamped to `maxColumnCount` |

Defaults: `columnWidth=200`, `gap=12`, `overscan=2` (viewports above and below the visible area).

## Rules of use

These come from the window-scroll virtualisation model. Violating them produces an empty or zero-height grid.

1. **Do not wrap `<Masonry>` in a fixed-height ancestor.** It measures `document.documentElement` and `window.scrollY`. Putting it inside `height: 600px; overflow: auto` makes it think the viewport is 600px and breaks scroll detection. If you need a scrollable region, use a non-virtualised CSS-columns grid instead.
2. **Do not put inline `height` on `<MasonryItem>` children.** The item's content drives measurement via `ResizeObserver`; an inline height stops the observer from reflecting the real layout.
3. **`fallback` is optional but recommended.** Without it Masonry renders a built-in muted skeleton on the first paint (before items are measured). Pass `fallback={<MySkeleton />}` if you want a specific look.

## Props

```ts
interface MasonryProps {
  // Layout
  columnCount?: number;            // fixed N
  columnWidth?: number;            // responsive (default 200)
  maxColumnCount?: number;         // upper bound when columnWidth is used
  gap?: number | { row: number; column: number };  // default 12
  linear?: boolean;                // round-robin instead of shortest-column

  // Measurement
  itemHeight?: number;             // estimate for un-measured items (default 300)
  defaultWidth?: number;           // SSR fallback width
  defaultHeight?: number;          // SSR fallback height
  overscan?: number;               // viewports above/below to render (default 2)

  // Perf
  scrollFps?: number;              // scroll listener throttle (default 12)

  // UI
  fallback?: React.ReactNode;      // first-paint placeholder (auto-skeleton if omitted)

  // Standard div props
  className?: string;
  style?: React.CSSProperties;
  asChild?: boolean;
}
```

## When *not* to use this

- **You need scrollable-container masonry** (modal, sidebar, side-by-side panes). This component virtualises against `window`. Use a CSS `column-count` grid or a different lib.
- **You have ≤ 30 items.** Virtualisation overhead isn't worth it — a plain CSS multi-column layout is simpler and SSR-friendly:
  ```tsx
  <div className="columns-3 gap-3 [&>*]:break-inside-avoid">
    {items.map((it) => <Card key={it.id}>…</Card>)}
  </div>
  ```
- **You need drag-and-drop reordering.** Not supported. Pair with `@dnd-kit` on top of an unvirtualised grid instead.
