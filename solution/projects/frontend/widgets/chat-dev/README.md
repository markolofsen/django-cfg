# @djangocfg/widget-chat-dev

Developer data on screen: an OpenAPI schema with a request playground, one HTTP
exchange, a log stream, an environment and an API reference table. They were the
viewer half of `widget-agent`; the page tooling that shared that package is now
part of [`@djangocfg/widget-chat`](../chat/README.md).

## Install

```bash
pnpm add @djangocfg/widget-chat-dev
```

Peers: `react` 19, `react-dom` 19, `@djangocfg/ui-core`, `@djangocfg/api`,
`lucide-react`, `zustand`.

## Import a subpath

There is no viewer in the root barrel (it holds the HTTP tone helpers only); each
viewer is its own subpath, so a host pays only for what it mounts.

| Subpath | What it is |
|---|---|
| `./openapi` | `OpenapiViewer`, lazy: a schema browser with a request playground |
| `./request-viewer` | one HTTP exchange, headers and bodies |
| `./api-ref-table` | endpoints as a table |
| `./log-viewer` | virtualised log stream, lazy |
| `./log-viewer/full` | the same, eager |
| `./env-table` | environment variables, with the values masked |

```tsx
import { LazyOpenapiViewer } from '@djangocfg/widget-chat-dev/openapi';
```

Each folder carries its own `README.md` with props and an example; stories are
beside the code, titled `Widgets/Chat Dev/…`.

## Testing

```bash
pnpm --filter @djangocfg/widget-chat-dev check-types test
```

There are no unit tests: the viewers are composition over `ui-core`, and what is
worth asserting about them is what a story shows.
