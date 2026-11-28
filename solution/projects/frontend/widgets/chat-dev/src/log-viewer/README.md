# LogViewer

Virtualized log stream viewer. Level filter, free-text search, ANSI escape parsing, copy. Tested on 10k+ entries. Level colors route to semantic tokens (`destructive` / `warning` / `info` / `debug` / `muted`).

```tsx
import { LogViewer } from '@djangocfg/widget-chat-dev/log-viewer';

<LogViewer
  entries={[
    { level: 'info',  message: 'Server listening on :3000', timestamp: '2025-01-12T10:00:00Z' },
    { level: 'error', message: '\x1b[31mDatabase connection failed\x1b[0m' },
  ]}
/>
```

## Props

| Prop | Type | Default | Description |
|---|---|---|---|
| `entries` | `LogEntry[]` | — | Each entry: `{ level, message, timestamp? }`. `message` may contain ANSI escapes. |
| `defaultLevel` | `LogLevel \| 'all'` | `'all'` | Initial level filter. |
| `defaultSearch` | `string` | `''` | Initial search term. |
| `showTimestamps` | `boolean` | `true` | Render the timestamp column. |
| `maxHeight` | `number \| string` | `400` | Viewport height. |

Storybook: `apps/storybook/stories/ui-tools/dev/LogViewer.stories.tsx`

---

Adapted from jalcoui (MIT).
