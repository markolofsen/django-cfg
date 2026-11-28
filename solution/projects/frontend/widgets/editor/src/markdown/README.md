# MarkdownEditor

WYSIWYG markdown editor based on Tiptap. Renders markdown visually (headings, lists, blockquotes) while editing, serializes to markdown string.

## Features

- Visual headings (H1, H2, H3) with proper sizing
- Bold, italic, strikethrough, inline code
- Bullet and ordered lists
- Blockquotes with left border
- Horizontal rules
- Toolbar with icon buttons
- `@`-mentions with auto-flipping popup (`@floating-ui/dom`)
- Customizable markdown serialization for mentions (six built-in presets)
- File-path chips and URL chips — atomic inline nodes with VSCode-style
  middle-ellipsis truncation (see [File-path & URL chips](#file-path--url-chips))
- Markdown input/output (stored as plain markdown string)
- SSR-safe (`immediatelyRender: false`)

## Quick Start

```tsx
import { MarkdownEditor } from '@djangocfg/ui-tools/markdown-editor';

function MyComponent() {
  const [bio, setBio] = useState('# Hello\n\nThis is **markdown**.');

  return (
    <MarkdownEditor
      value={bio}
      onChange={setBio}
      placeholder="Write something..."
    />
  );
}
```

## CSS

Two ways to load styles, depending on your build:

```ts
// Tailwind-based apps — pulls in source utilities so Tailwind's JIT picks them up.
import '@djangocfg/ui-tools/styles';

// Plain Vite / webpack / CRA — pre-compiled CSS, no Tailwind required.
import '@djangocfg/ui-tools/dist.css';
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `value` | `string` | — | Markdown string |
| `onChange` | `(value: string) => void` | — | Called on every change |
| `placeholder` | `string` | `'Write markdown...'` | Placeholder text |
| `minHeight` | `number` | `120` | Min height in px |
| `className` | `string` | — | Additional CSS class |
| `disabled` | `boolean` | `false` | Read-only mode |
| `showToolbar` | `boolean` | `true` | Show formatting toolbar |
| `mentions` | `MentionConfig` | — | `@`-mention autocomplete config |
| `filePathChips` | `boolean` | `true` | Render absolute local file paths as atomic chips — see [File-path & URL chips](#file-path--url-chips) |
| `urlChips` | `boolean` | `true` | Render web URLs as atomic, clickable chips — see [File-path & URL chips](#file-path--url-chips) |
| `onMentionIdsChange` | `(ids: string[]) => void` | — | Called when mentioned IDs change |
| `onSubmit` | `() => boolean \| void` | — | Enter handler — when set, Enter submits and Shift+Enter inserts a newline (ChatGPT / Telegram chat behaviour). Return `false` to fall back to default HardBreak. See [Submit on Enter](#submit-on-enter) below. |

### `MentionConfig` fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `items` | `MentionItem[]` | required | Available mention items (`id`, `label`, optional `description`, `thumbnail`) |
| `trigger` | `string` | `'@'` | Trigger character |
| `maxItems` | `number` | `5` | Max items shown in dropdown |
| `renderMarkdown` | `MentionMarkdownRenderer` | `mentionPresets.plainAt` | Serializes a mention to markdown — see below |

## Mentions

```tsx
<MarkdownEditor
  value={text}
  onChange={setText}
  mentions={{
    items: [
      { id: '1', label: 'Alice', thumbnail: '/alice.jpg' },
      { id: '2', label: 'Bob', description: 'Antagonist' },
    ],
  }}
  onMentionIdsChange={(ids) => console.log('Mentioned:', ids)}
/>
```

Type `@` to trigger autocomplete. Mentions render as inline chips. The popup auto-flips above the trigger when there isn't enough room below, and tracks scroll/resize via `autoUpdate` — viewport-aware out of the box.

> Heads-up: Tiptap initialises the editor exactly once. If `mentions` is `undefined` on first render and becomes truthy later, the extension is never installed. Pass `{ items: [] }` from the start and mutate `.items` in place if items load async.

## Mention serialization

By default Tiptap's `Mention` extension emits a useless shortcode like `[@ id="..." label="..."]` into markdown. `MarkdownEditor` overrides that with the renderer from `MentionConfig.renderMarkdown` (defaults to `mentionPresets.plainAt`, which yields `@<label>`).

Six presets are exported from `@djangocfg/ui-tools`:

```tsx
import { MarkdownEditor, mentionPresets } from '@djangocfg/ui-tools/markdown-editor';

<MarkdownEditor
  value={text}
  onChange={setText}
  mentions={{
    items,
    renderMarkdown: mentionPresets.customUri('cmdop', 'machine'),
  }}
/>
```

| Preset | Output for `{ label: 'Vps-audi', id: 'uuid' }` |
|--------|-------------------------------------------------|
| `plainAt` *(default)* | `@Vps-audi` |
| `plainLabel` | `Vps-audi` |
| `markdownLink(baseUrl)` | `[@Vps-audi](baseUrl/uuid)` |
| `customUri(scheme, kind)` | `@[Vps-audi](scheme://kind/uuid)` |
| `slackStyle` | `<@uuid>` |
| `htmlSpan(className?)` | `<span class="mention" data-mention-id="uuid">@Vps-audi</span>` |

Pick by use case:

- **`plainAt`** — chat composers feeding an LLM that reads `@<label>` natively.
- **`customUri`** — chat that also wants machine-readable IDs in `href` for downstream parsing (e.g. `@[Vps-audi](cmdop://machine/uuid)`).
- **`markdownLink`** — clickable mentions linking to a profile / detail page.
- **`slackStyle`** — interop with Slack-like backends that resolve `<@id>` server-side.
- **`htmlSpan`** — markdown consumers that allow inline HTML and want chip styling baked in.
- **`plainLabel`** — bare display string (no `@`), e.g. for `/`-commands or non-mention triggers.

### Custom renderer

The signature is just `(attrs: MentionAttrs) => string`:

```tsx
import type { MentionMarkdownRenderer } from '@djangocfg/ui-tools/markdown-editor';

const renderMention: MentionMarkdownRenderer = ({ id, label }) =>
  `{{user:${id}|${label}}}`;

<MarkdownEditor mentions={{ items, renderMarkdown: renderMention }} ... />
```

Either `id` or `label` may be empty strings if upstream config didn't populate them — fall back accordingly. Returning `''` drops the mention from the output.

> Mentions are write-only: the markdown isn't parsed back into mention nodes on `setContent`. After submit/reset, the editor receives a plain string — fine for chat composers.

## File-path & URL chips

The editor turns absolute **local file paths** and **web URLs** into compact,
atomic inline chips — like VSCode / Cursor. Both default ON; gate them with
the `filePathChips` / `urlChips` props.

```tsx
<MarkdownEditor
  value={text}
  onChange={setText}
  filePathChips   // default true — paths → chips
  urlChips        // default true — URLs → chips
/>
```

### What you get

| | File-path chip (`kind: 'path'`) | URL chip (`kind: 'url'`) |
|---|---|---|
| Icon | VSCode file icon by extension (folder glyph for dirs) | favicon (Google S2) → globe glyph on error |
| Label | middle-ellipsis, basename kept — `…/dev/Map/index.ts` | domain + middle-ellipsis path — `github.com/…/README.md` |
| Tooltip | full path (`title`) | full URL (`title`) |
| Clickable | no | yes — opens in a new tab (`rel=noopener noreferrer`) |
| Detection | absolute Unix / macOS / `~` / Windows-drive / UNC / `file://` | `http`/`https`/`ftp`/`mailto`/`file` + bare `www.` |

### Why a node, not a decoration (the long-path fix)

The chip is an **atomic inline NODE** (`editorChip`), the same shape as the
`@`-mention and `/`-command chips — NOT a decoration. A decoration is an
overlay: it can style the raw text but can't replace it, so a long path
rendered in full and **wrapped to several lines**. A node owns its
rendering, so it shows the truncated label on **one line** while the full
string lives in the node's attribute.

A single node renders both kinds (a `kind` attribute switches path vs URL) —
one component, one set of styles, DRY.

### Text / markdown fidelity (the whole point)

Each chip **serialises back to the RAW string**. `renderText` and
`renderMarkdown` both emit the literal path / URL, so:

- copying a chip yields the raw path / URL,
- the submitted message and `getMarkdown()` contain the real string,
- never any chip markup.

A bare URL serialises as the bare URL; a file path as the literal path.

### Auto-conversion

- **Typing**: type a path / URL followed by a **space** and it becomes a
  chip (an input rule on the word boundary — punctuation inside the token
  like `.ts` is preserved because only whitespace triggers conversion).
- **Pasting**: a paste rule converts every detected path / URL in the
  pasted text, keeping the surrounding prose.
- **Initial `value`**: paths / URLs in the controlled markdown are
  converted after `setContent` (the same way leading `/`-commands are).
- **External controlled update while editing**: the editor preserves the
  current focused selection, clamped to the new document. A background parent
  render must never send the caret to document start or steal focus from
  another control.

### Caret / editing

Atomic nodes behave like a single character: arrow keys step over the whole
chip, and Backspace removes / reverts the whole chip at once (the raw text
is never partially lost) — VSCode-like.

### Standalone `<FilePathChip>`

The presentational React chip still exists for rendering a known path
**outside** the editor (a chat message, a file list). It's exported from
`@djangocfg/ui-tools/markdown-editor`:

```tsx
import { FilePathChip } from '@djangocfg/ui-tools/markdown-editor';

<FilePathChip path="/Users/me/dev/Map/index.ts" />
```

The pure detector / display helpers are exported too:
`findFilePaths`, `splitPath`, `truncatePathLabel` (paths) and
`findUrls`, `splitUrl`, `truncateUrlLabel`, `faviconUrl` (URLs).

## Submit on Enter

For chat composers you usually want **Enter = send**, **Shift+Enter = newline** — ChatGPT / Telegram / Slack behaviour. Pass an `onSubmit` and that's what you get:

```tsx
<MarkdownEditor
  value={text}
  onChange={setText}
  onSubmit={() => {
    if (!text.trim()) return false   // fall back to HardBreak
    void send(text)
    // returning undefined (or true) consumes the key — newline isn't inserted
  }}
/>
```

### How it works (and why a Tiptap extension, not a React onKeyDown)

The implementation lives in `submitOnEnter.ts` — a Tiptap `Extension` that registers a keyboard shortcut via `addKeyboardShortcuts`. It runs **inside ProseMirror's keymap pipeline at higher priority than StarterKit's HardBreak**, so we intercept Enter **before** the hard-break transaction is dispatched.

A naïve wrapper handler (`<div onKeyDownCapture={...}>` calling `preventDefault`) does NOT work reliably: ProseMirror's keymap is a plugin inside the editor, which fires its handler in the same event tick as the React capture phase but **commits the HardBreak transaction before React's stopPropagation gets a chance to matter**. The user sees a hard-break flash in, then the next Enter submits — the "first Enter inserts newline" bug we shipped before this extension landed.

### Behaviour details

| Key | Behaviour |
|---|---|
| `Enter` | Calls `onSubmit()`. Returns `true`/`undefined` ⇒ consume. Returns `false` ⇒ fall through to HardBreak. |
| `Shift+Enter` | Always inserts a newline. Bound to `() => false` so the chain falls through cleanly. |
| Mention popover open | Enter is given to the suggestion plugin (it picks the active item) — detected by querying `.markdown-mention-list`. |
| IME composition | Native browser composition events are not intercepted (Tiptap handles them upstream). |

The handler is captured via a ref inside `MarkdownEditor`, so swapping `onSubmit` between renders is safe — the latest closure always fires, no editor rebuild needed.

## Dependencies

All Tiptap packages and `@floating-ui/dom` are direct dependencies — no extra installs needed.
