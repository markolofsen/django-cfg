# ActivityGraph

GitHub-style contribution heatmap. Maps daily counts to opacity stops of the active theme `primary` color via `useThemeColor` + `useResizeObserver`.

```tsx
import { ActivityGraph } from '@djangocfg/ui-tools/activity-graph';

<ActivityGraph
  data={[{ date: '2025-01-12', count: 4 }, { date: '2025-01-13', count: 0 }]}
  weeks={52}
/>
```

## Props

| Prop | Type | Default | Description |
|---|---|---|---|
| `data` | `ActivityEntry[]` | — | Daily entries `{ date, count }`. Duplicate dates are summed. |
| `weeks` | `number` | `52` | Trailing week count. |
| `blockSize` | `number` | auto | Cell size in px. When omitted, auto-fits the container. |
| `blockRadius` | `number` | `2` | Cell border-radius in px. |
| `intensityOpacity` | `[number,number,number,number,number]` | `[0.08, 0.18, 0.35, 0.6, 0.95]` | Opacity stops applied to the theme `primary` color (intensity 0–4). |

Storybook: `apps/storybook/stories/ui-tools/visual/ActivityGraph.stories.tsx`

---

Adapted from jalcoui (MIT).
