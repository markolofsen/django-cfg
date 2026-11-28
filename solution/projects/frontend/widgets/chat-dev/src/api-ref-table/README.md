# ApiRefTable

Reference table for component props / function parameters. Per-token type colorization, optional default column, click-to-expand description + long-form type.

```tsx
import { ApiRefTable } from '@djangocfg/widget-chat-dev/api-ref-table';

<ApiRefTable
  title="ButtonProps"
  props={[
    { name: 'variant', type: "'solid' | 'outline'", defaultValue: "'solid'", description: 'Visual variant.' },
    { name: 'onClick', type: '(e: MouseEvent) => void', required: true },
  ]}
/>
```

## Props

| Prop | Type | Default | Description |
|---|---|---|---|
| `props` | `ApiProp[]` | — | Rows. Each row: `{ name, type, required?, defaultValue?, description?, fullType? }`. |
| `title` | `string` | — | Heading above the column strip. |
| `nameLabel` | `string` | `'Prop'` | Leftmost column header (e.g. `'Param'`, `'Field'`). |
| `showDefaults` | `boolean` | auto | Render the `Default` column. Auto when any row has `defaultValue`. |
| `emptyMessage` | `string` | `'No parameters.'` | Empty state. |

Storybook: `apps/storybook/stories/ui-tools/dev/ApiRefTable.stories.tsx`

---

Adapted from jalcoui (MIT).
