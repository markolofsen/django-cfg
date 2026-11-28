import { useEffect, useRef, useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  NotionEditor,
  type NotionEditorHandle,
} from './lazy';
import type { LinkPreviewData, ResolveLinkPreview } from '../link-preview';

const SAMPLE = `# Welcome to NotionEditor

A **Notion-style** WYSIWYG editor backed by *TipTap v3* with a curated extension stack.

## Try these

- Type \`/\` on an empty line to open the slash menu.
- Select any text — a **bubble toolbar** appears (bold / italic / strike / code / highlight).
- Hover a block — the drag handle (⠿) shows up on the left so you can reorder.

### Lists

1. Numbered lists work
2. With auto-incrementing markers
3. And nested items

- Bullet lists too
- With **inline formatting**
- And \`inline code\`

### Tasks

- [ ] A pending task
- [x] A completed one
- [ ] Mix and match

### Quote

> Knowledge is power, but enthusiasm pulls the switch.
> — Ivern Ball

### Code

\`\`\`ts
function greet(name: string): string {
  return \`Hello, \${name}!\`;
}
\`\`\`

### Table

| Feature       | Status   |
| ------------- | -------- |
| Slash menu    | ✓ ready  |
| Bubble menu   | ✓ ready  |
| Drag handle   | ✓ ready  |
| Tables        | ✓ ready  |
| Code blocks   | ✓ ready  |

---

The editor serialises everything back to **GitHub-Flavoured Markdown** on every change.
`;

function Host(props: {
  initial?: string;
  disabled?: boolean;
  autoFocus?: boolean;
  minHeight?: number;
  placeholder?: string;
  showOutput?: boolean;
  resolveLinkPreview?: ResolveLinkPreview;
  /** When set, seed a bookmark card for this URL once the editor mounts. */
  seedBookmark?: string;
}) {
  const [value, setValue] = useState(props.initial ?? '');
  const ref = useRef<NotionEditorHandle>(null);

  // Seed a bookmark via the imperative editor command once it's ready. This
  // demonstrates the bookmark node without relying on a real paste — the same
  // node a bare-URL paste on an empty line produces.
  const seed = props.seedBookmark;
  useEffect(() => {
    if (!seed) return;
    let tries = 0;
    const id = window.setInterval(() => {
      const editor = ref.current?.getEditor();
      tries += 1;
      if (editor) {
        editor.chain().focus().setBookmark(seed).run();
        window.clearInterval(id);
      } else if (tries > 40) {
        window.clearInterval(id);
      }
    }, 50);
    return () => window.clearInterval(id);
  }, [seed]);

  return (
    <div className="grid w-full max-w-[1400px] grid-cols-1 gap-6 lg:grid-cols-[1fr_400px]">
      <div className="rounded-lg border border-border bg-card p-4">
        <NotionEditor
          ref={ref}
          value={value}
          onChange={setValue}
          disabled={props.disabled}
          autoFocus={props.autoFocus}
          minHeight={props.minHeight ?? 420}
          placeholder={props.placeholder}
          resolveLinkPreview={props.resolveLinkPreview}
          onSave={(md) => console.log('[onSave]', md)}
        />
      </div>
      {props.showOutput !== false ? (
        <div className="rounded-lg border border-border bg-muted/30 p-3">
          <div className="mb-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">
            Serialised markdown
          </div>
          <pre className="max-h-[420px] overflow-auto whitespace-pre-wrap break-words text-[12px] leading-relaxed font-mono">
            {value || '(empty)'}
          </pre>
        </div>
      ) : null}
    </div>
  );
}

// ── A fake link-preview resolver (stands in for the host's Wails/Go or
//    Next.js /api/unfurl fetcher), mirroring the chat LinkPreview story. ──
const LINK_FIXTURES: Record<string, LinkPreviewData> = {
  'https://github.com/wailsapp/wails': {
    url: 'https://github.com/wailsapp/wails',
    title: 'wailsapp/wails: Create beautiful applications using Go',
    description:
      'Build desktop applications using Go & Web Technologies. Wails bundles a ' +
      'Go binary with a native webview front-end.',
    image: 'https://picsum.photos/seed/wails-og/640/320',
    favicon: 'https://www.google.com/s2/favicons?domain=github.com&sz=64',
    siteName: 'GitHub',
  },
  'https://www.notion.so': {
    url: 'https://www.notion.so',
    title: 'Notion – The all-in-one workspace',
    description: 'Write, plan, share. With AI built in. Notion is the connected workspace.',
    favicon: 'https://www.google.com/s2/favicons?domain=notion.so&sz=64',
    siteName: 'Notion',
  },
};

/** Mock resolver — 500ms latency to show the card skeleton, then the fixture. */
const mockResolveLinkPreview: ResolveLinkPreview = (url) =>
  new Promise((resolve) => {
    setTimeout(() => resolve(LINK_FIXTURES[url] ?? { url }), 500);
  });

// An initial document that already contains a `/map` block (a fenced ```map
// JSON block). The MapNode's markdown tokenizer parses it back into a live
// map on load — proving the round-trip.
const MAP_DOC = `# Trip plan

Drop a map anywhere with **/map** — or paste a fenced \`map\` block:

\`\`\`map
{
  "center": { "lat": 48.8584, "lng": 2.2945 },
  "zoom": 13,
  "markers": [
    { "id": "m1", "lat": 48.8584, "lng": 2.2945, "label": "Eiffel Tower" },
    { "id": "m2", "lat": 48.8606, "lng": 2.3376, "label": "Louvre" }
  ]
}
\`\`\`

The map serialises back to the same fenced block on every change.
`;

const meta = {
  title: 'Widgets/Editor/NotionEditor',
  component: Host,
  tags: ['autodocs'],
  parameters: {
    layout: 'padded',
    docs: {
      description: {
        component:
          'Notion-style WYSIWYG markdown editor built on TipTap v3. Type `/` for the slash menu, select text for the bubble menu, hover any block to reveal the drag handle on the left.',
      },
    },
  },
} satisfies Meta<typeof Host>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
  name: 'Default (empty)',
  render: () => <Host showOutput />,
};

export const WithContent: Story = {
  name: 'With sample content',
  render: () => <Host initial={SAMPLE} showOutput />,
};

export const AutoFocus: Story = {
  name: 'Auto-focus on mount',
  render: () => (
    <Host initial="" autoFocus placeholder="Type / to open the slash menu…" showOutput />
  ),
};

export const ReadOnly: Story = {
  name: 'Read-only',
  render: () => <Host initial={SAMPLE} disabled showOutput={false} />,
};

export const Compact: Story = {
  name: 'Compact (240px min-height)',
  render: () => <Host minHeight={240} showOutput />,
};

/**
 * Bookmark (link-preview) block. Paste a BARE URL on an EMPTY line and it
 * becomes a link-preview card (Notion behaviour). A labelled link or a URL
 * pasted mid-text stays an inline link. The `resolveLinkPreview` host resolver
 * unfurls the URL into title/description/image; the node serialises back to
 * the raw URL (see the markdown panel). This story pre-seeds one card on
 * mount; try pasting `https://www.notion.so` on a fresh empty line too.
 */
export const Bookmark: Story = {
  name: 'Bookmark (paste a URL → card)',
  render: () => (
    <Host
      seedBookmark="https://github.com/wailsapp/wails"
      resolveLinkPreview={mockResolveLinkPreview}
      placeholder="Paste a bare URL on an empty line…"
      showOutput
    />
  ),
};

/**
 * Map block. Insert one via the slash menu (`/map`) — it drops a live map
 * seeded with a default center + marker. This story loads a document that
 * already contains a fenced ```` ```map ```` JSON block, which the MapNode's
 * markdown tokenizer parses into a live map on mount (round-trip proof).
 */
export const Map: Story = {
  name: 'Map (/map → map block)',
  render: () => <Host initial={MAP_DOC} showOutput />,
};

// A document with a DELIBERATELY BROKEN ```map block — malformed JSON (a
// trailing comma + a non-numeric coordinate). The MapNode tokenizer parses it
// without throwing and hands the node attrs that FAIL the schema, so the
// NodeView renders a `<BlockError>` card. The editor stays fully alive — type
// below the broken block to prove it. This is the "don't let a corrupted
// payload take down the editor" guarantee.
const BROKEN_MAP_DOC = `# Broken block recovery

This map block has corrupted JSON — it renders a safe error card, **not** a crash:

\`\`\`map
{
  "center": { "lat": "not-a-number", "lng": 2.2945 },
  "zoom": 13,
}
\`\`\`

The editor is still fully usable — try typing here. ✏️
`;

/**
 * Broken payload → `<BlockError>`. A malformed ```` ```map ```` JSON (a
 * non-numeric latitude) fails the shared Zod schema; the NodeView renders a
 * compact "Couldn't render this map" card instead of throwing. The editor
 * keeps working. Proves the validator safety net (phase 2).
 */
export const BrokenMap: Story = {
  name: 'Broken map block → BlockError',
  render: () => <Host initial={BROKEN_MAP_DOC} showOutput />,
};

/**
 * Editable map — drag a pin and watch the serialised ```` ```map ```` JSON in
 * the markdown panel update to the new coordinates. Use the on-map controls
 * (top-left) to ADD a pin (click the map to place) or REMOVE pins, and the
 * Layers chip (top-right) to switch the basemap — each writes back into the
 * markdown. This is the headline interaction (phase 3).
 */
export const EditableMap: Story = {
  name: 'Editable map (drag → markdown updates)',
  render: () => <Host initial={MAP_DOC} showOutput />,
};
