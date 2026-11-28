# RequestViewer

HTTP request inspector. Tabs for headers / body / timing. Method + status pills routed through `lib/http` (`statusColor`, `methodColor`) so colors match OpenapiViewer.

The viewer never fetches — pass an already-executed `NetworkRequest`.

```tsx
import { RequestViewer } from '@djangocfg/widget-chat-dev/request-viewer';

<RequestViewer
  request={{
    method: 'POST',
    url: 'https://api.example.com/v1/users',
    status: 201,
    requestHeaders: [{ name: 'Content-Type', value: 'application/json' }],
    responseBody: '{"id":"u_42"}',
    duration: 142,
  }}
/>
```

## Props

| Prop | Type | Default | Description |
|---|---|---|---|
| `request` | `NetworkRequest` | — | Captured request: `method`, `url`, `status`, headers, body, timing, etc. |
| `defaultTab` | `'headers' \| 'body' \| 'timing'` | `'headers'` | Initial active tab. |

Storybook: `apps/storybook/stories/ui-tools/dev/RequestViewer.stories.tsx`

---

Adapted from jalcoui (MIT).
