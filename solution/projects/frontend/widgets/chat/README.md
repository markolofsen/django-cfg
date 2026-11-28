# @djangocfg/widget-chat

A chat surface for React: transcript, composer, tool calls, streaming markdown. It also carries the site assistant (`./assistant`) and the page tooling that lets a chat see and act on the page. Transport-agnostic: the host supplies an adapter, the package supplies everything a chat looks like.

```bash
pnpm add @djangocfg/widget-chat @djangocfg/ui-core
```

```css
@import "@djangocfg/widget-chat/styles";
```

```tsx
import { Chat } from '@djangocfg/widget-chat';

<Chat adapter={myAdapter} renderers={myRenderers} capabilities={{ tools, voice }} body={{ kind: 'packaged' }} />
```

A chat needs an adapter and a renderer per part type it draws: [getting started](@docs/getting-started.md) has the smallest working one.

Every capability is optional and absent means absent, never stubbed. `<Chat>` has seven props, and a new feature is a capability, a part type or a slot, never a prop ([concepts](@docs/concepts.md)). A file belongs in this package when a second product would have to write it again, unchanged.

## Docs

[`@docs/`](@docs/README.md) is organised by the reader's question:

| I want to | Start at |
|---|---|
| mount a chat | [getting started](@docs/getting-started.md), [concepts](@docs/concepts.md), [capabilities](@docs/capabilities.md), [subpaths](@docs/subpaths.md) |
| change how it behaves | [composer](@docs/composer.md), [attachments](@docs/attachments.md), [blocks](@docs/blocks.md), [media](@docs/media.md), [run block](@docs/run-block.md), [room](@docs/room.md), [phones](@docs/phones.md) |
| add a site assistant | [assistant](@docs/assistant.md) |
| let the chat see the page | [page tooling](@docs/page-tooling.md) |
| restyle, translate, test | [styling](@docs/styling.md), [i18n](@docs/i18n.md), [testing](@docs/testing.md) |

[`CLAUDE.md`](CLAUDE.md) answers a different question: what is easy to break.

## Verify

```bash
pnpm --filter @djangocfg/widget-chat check-types test
```
