# Sparkline

Compact inline trend chart (line / area / bar). Resolves stroke + fill via `useThemeColor(color)` — semantic tokens only, no raw scales.

```tsx
import { Sparkline } from '@djangocfg/ui-tools/sparkline';

<Sparkline data={[3, 5, 4, 7, 9, 8, 12]} variant="area" color="success" />
```

## Props

| Prop | Type | Default | Description |
|---|---|---|---|
| `data` | `SparklineDatum[]` | — | `number` or `{ value, label? }`. Empty array renders nothing. |
| `variant` | `'line' \| 'area' \| 'bar'` | `'line'` | Visual style. |
| `color` | `'primary' \| 'success' \| 'warning' \| 'destructive' \| 'info'` | `'primary'` | Semantic theme color. |
| `width` | `number` | `120` | SVG width. |
| `height` | `number` | `32` | SVG height. |
| `strokeWidth` | `number` | `1.5` | Line stroke (ignored for `bar`). |
| `showEndpoint` | `boolean` | `true` | Filled dot at latest point. |
| `showBaseline` | `boolean` | `false` | Dashed average line. |
| `ariaLabel` | `string` | — | Accessible label. |

Storybook: `apps/storybook/stories/ui-tools/visual/Sparkline.stories.tsx`

---

Adapted from jalcoui (MIT).
