# chips

Surface-agnostic presentational "chips" — compact inline pills that render a
URL or a file path with a favicon/icon + middle-ellipsis label. They match the
TipTap composer's `editor-chip` look (see
[`forms/MarkdownEditor/chip/ChipNode.ts`](../../tools/forms/MarkdownEditor/chip/ChipNode.ts))
but are plain React, so the same visual is reusable on any surface — composer,
chat bubble, link lists.

Internal module (`src/common/chips/`) — consumed by other tools via relative
import; not a package subpath export:

```tsx
import { UrlChip, FilePathChip } from '../../common/chips';
```

## `UrlChip`

A compact, clickable URL chip (Chrome-omnibox style): a favicon + the domain
with a middle-ellipsised path (`github.com/wailsapp/…/README.md`), monospace,
with the full href on `title` hover. Renders an `<a target="_blank"
rel="noopener noreferrer">`, so it opens in a new tab.

- **Favicon fallback.** The favicon `<img>` swaps to a lucide `Globe` glyph on
  load error (offline / blocked / unknown host) — and also when the host is
  unparseable (empty favicon URL) — so the chip never shows a broken image.
- **Presentational + self-contained.** It imports only the pure URL detector
  helpers from [`forms/MarkdownEditor/url/detect`](../../tools/forms/MarkdownEditor/url/detect.ts)
  — no TipTap / ProseMirror — so it can render a known URL anywhere:
  `splitUrl` (host/domain/path split), `truncateUrlLabel` (the
  middle-ellipsis label), and `faviconUrl` (Google S2 favicon).

### Props (`UrlChipProps`)

| Prop | Type | Default | Description |
|---|---|---|---|
| `href` | `string` | required | The full, navigable href (`https://…`). |
| `maxChars` | `number` | `40` | Approximate max chars for the truncated label. The domain is always kept in full; only the path's middle collapses. |
| `className` | `string` | — | Extra classes merged onto the chip anchor. |

```tsx
<UrlChip href="https://github.com/wailsapp/wails/blob/main/v3/README.md" />
// → 🟣 github.com/…/README.md
```

## `FilePathChip`

Re-exported (with its `FilePathChipProps` type) from the editor's standalone
path chip,
[`forms/MarkdownEditor/filePath/FilePathChip.tsx`](../../tools/forms/MarkdownEditor/filePath/FilePathChip.tsx).
It's already presentational and dependency-light, so this module re-exports it
rather than duplicating it — `UrlChip` and `FilePathChip` then live behind one
import.

## Where these are reused

- **Chat markdown bubble.** `UrlChip` is what
  [`MarkdownMessage`'s `urlChipRule`](../../tools/dev/code/MarkdownMessage/README.md)
  renders for a bare URL when the host opts in via `ChatConfig.linkChips`.
- **Composer.** The TipTap composer renders its **own** DOM chip via `ChipNode`
  (a single inline atom node, `kind: 'url'`), not this React component — but the
  two are built to match pixel-for-pixel using the same semantic tokens, so a
  URL reads identically whether it's being typed in the composer or sitting in a
  rendered bubble.

This shared look is the point: the same URL is one consistent chip across every
surface.
