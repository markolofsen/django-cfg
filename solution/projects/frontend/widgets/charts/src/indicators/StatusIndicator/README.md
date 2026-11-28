# StatusIndicator

Compact operational-status pill (dot + label). Maps `Status` → semantic `StatusTone` (success / warning / destructive / info / muted) via `STATUS_CONFIG`.

This component is the **golden sample** for the jalcoui port — it demonstrates all CONTRACT rules (semantic tokens, CVA variants, no nested providers, attribution).

```tsx
import { StatusIndicator } from '@djangocfg/ui-tools/status-indicator';

<StatusIndicator status="operational" />
<StatusIndicator status="degraded" size="lg" />
<StatusIndicator status="incident" label="Custom label" />
```

## Props

| Prop | Type | Default | Description |
|---|---|---|---|
| `status` | `Status` | — | `'operational' \| 'degraded' \| 'partial-outage' \| 'major-outage' \| 'maintenance' \| 'incident' \| 'unknown'`. |
| `tone` | `StatusTone` | from `STATUS_CONFIG` | Override the semantic tone. |
| `label` | `string` | from `STATUS_CONFIG` | Override the visible label. |
| `size` | `'sm' \| 'md' \| 'lg'` | `'md'` | Pill scale. |

Storybook: `apps/storybook/stories/ui-tools/visual/StatusIndicator.stories.tsx`

---

Adapted from jalcoui (MIT).
