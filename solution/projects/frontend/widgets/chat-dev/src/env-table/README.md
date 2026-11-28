# EnvTable

Environment-variable table with mask / reveal + copy. Per-row environment badge tinted via semantic tokens (`success` / `warning` / `info` / `muted`).

```tsx
import { EnvTable } from '@djangocfg/widget-chat-dev/env-table';

<EnvTable
  variables={[
    { key: 'DATABASE_URL', value: 'postgres://…', environment: 'production', required: true },
    { key: 'DEBUG', value: 'false', environment: 'development' },
  ]}
/>
```

## Props

| Prop | Type | Default | Description |
|---|---|---|---|
| `variables` | `EnvVariable[]` | — | Rows: `{ key, value, environment?, description?, required? }`. |
| `title` | `string` | — | Heading above the table. |
| `defaultRevealed` | `boolean` | `false` | Start with all values visible. |
| `emptyLabel` | `string` | `'No environment variables.'` | Empty state. |

Storybook: `apps/storybook/stories/ui-tools/dev/EnvTable.stories.tsx`

---

Adapted from jalcoui (MIT).
