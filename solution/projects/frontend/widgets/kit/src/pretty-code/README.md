# PrettyCode

A syntax-highlighted listing: Prism, a header with the language and a copy
button, wrapping lines, and the host's light or dark theme. One component for
every code surface (widget-code's markdown and diff, the chat's `Response`,
chat-dev's request and response panels).

## Structure

```
pretty-code/
├── pretty-code.tsx       # PrettyCode (memo) + PrettyCodeProps / PrettyCodeLabels
├── code-panel-header.tsx # language label + copy / expand buttons
├── languages.ts          # one alias table: fence name -> Prism grammar + label
├── prism-languages.ts    # loads bash, ruby, java, php on first render
├── lazy.tsx              # LazyPrettyCode
└── index.ts              # the public surface
```

## Usage

```tsx
import { PrettyCode } from '@djangocfg/widget-kit/pretty-code';
import { LazyPrettyCode } from '@djangocfg/widget-kit/pretty-code/lazy';

<PrettyCode data={source} language="typescript" />
<PrettyCode data={`const x = 1`} language="ts" inline />
<PrettyCode data={longBlob} language="json" maxLines={50} />
<PrettyCode data={src} language="bash" variant="plain" />
<PrettyCode data={partial} language="go" isCompact pending />   {/* a fence still arriving */}
```

## Props

| Prop | Type | Default | Description |
|---|---|---|---|
| `data` | `string \| object` | required | The source. An object is `JSON.stringify`d; a cycle shows its `String()` rather than throwing. |
| `language` | `string` | required | A fence name. Aliases resolve; an unknown name renders as plain text. |
| `mode` | `'dark' \| 'light'` | host theme | Pins the palette. Default follows the resolved theme (light: GitHub palette, dark: vsDark). |
| `inline` | `boolean` | `false` | An inline `<code>` chip. |
| `variant` | `'card' \| 'plain'` | `'card'` | `plain` drops the surface and header, for a host that owns the chrome. |
| `isCompact` | `boolean` | `false` | 12px type and tighter padding, for prose. |
| `maxLines` | `number` | none | Scrolls past this many lines (keyboard-reachable `region`). |
| `onExpand` | `() => void` | none | Expand button, shown only while height-capped. |
| `customBg` | `string` | none | A class that replaces the `--code` surface. |
| `pending` | `boolean` | `false` | The source is still arriving: an empty body keeps its header and shows no "no content" line. |
| `labels` | `Partial<PrettyCodeLabels>` | i18n | `copyCode`, `noContent`, `expand`. Default from `@djangocfg/i18n`. |
| `className` | `string` | none | Extra classes on the wrapper. |

The surface is the ui-core `--code` token, borderless. Lines wrap; they do not
scroll sideways.

Needs `@djangocfg/ui-core` and `@djangocfg/i18n` in the host.
