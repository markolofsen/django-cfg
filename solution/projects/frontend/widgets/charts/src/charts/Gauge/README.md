# Gauge

Accessible SVG meter (`role="meter"`) with composable parts: `Gauge` (root + context), `GaugeIndicator` (svg), `GaugeTrack`, `GaugeRange`, `GaugeValueText`, `GaugeLabel`. `GaugeCombined` is the all-in-one shorthand. Track / range colors come from Tailwind semantic tokens (`text-muted-foreground/20`, `text-primary`) — no Canvas, no `useThemePalette` hooks needed.

```tsx
import {
  Gauge,
  GaugeIndicator,
  GaugeTrack,
  GaugeRange,
  GaugeValueText,
} from '@djangocfg/ui-tools/gauge';

<Gauge value={72} size={140} thickness={10} startAngle={-120} endAngle={120}>
  <GaugeIndicator>
    <GaugeTrack />
    <GaugeRange />
  </GaugeIndicator>
  <GaugeValueText />
</Gauge>
```

## `<Gauge>` props

| Prop | Type | Default | Description |
|---|---|---|---|
| `value` | `number \| null` | `null` | Current value. `null` / `undefined` → indeterminate state. Out-of-range values are clamped. |
| `min` | `number` | `0` | Lower bound. |
| `max` | `number` | `100` | Upper bound. Must be `> min`; otherwise auto-bumped. |
| `size` | `number` | `120` | Outer size in px. |
| `thickness` | `number` | `8` | Arc stroke width. Must be `< size`. |
| `startAngle` | `number` | `0` | Arc start in degrees (12 o'clock = 0). |
| `endAngle` | `number` | `360` | Arc end in degrees. `|end - start| >= 360` renders a full ring. |
| `getValueText` | `(value, min, max) => string` | percentage `0–100` | Override the text rendered inside `GaugeValueText` and announced via `aria-valuetext`. |
| `asChild` | `boolean` | `false` | Render-as via Radix `Slot`. |

## Notes

- All sub-parts (`GaugeIndicator`, `GaugeTrack`, `GaugeRange`, `GaugeValueText`, `GaugeLabel`) **must** be rendered under a `<Gauge>` — they throw without the context.
- Override colors by passing `className` to `GaugeTrack` / `GaugeRange` (they use `currentColor`, so any `text-*` token works).
- State is exposed via `data-state="indeterminate" | "loading" | "complete"` on every part for custom styling.

---

Adapted from jalcoui (MIT).
