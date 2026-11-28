import { useRef, useState } from 'react';
import type { Meta, StoryObj } from '@storybook/react-vite';
import {
  MarkdownEditor,
  mentionPresets,
  FilePathChip,
  type MarkdownEditorHandle,
  type MarkdownEditorProps,
  type MentionConfig,
  type MentionMarkdownRenderer,
} from './lazy';

// ── Fixtures ──

const SAMPLE = `# Hello, Markdown!

Type **bold**, *italic*, or \`inline code\`.

- Lists work too
- And [links](https://djangocfg.com)
`;

const LONG_CONTENT = `# Long Document

## Introduction

This is a longer document used to verify scrolling, sticky toolbar behaviour, and
overall density of the editor surface.

## Features

- Headings (H1–H3)
- **Bold**, *italic*, ~~strikethrough~~, \`inline code\`
- Ordered and unordered lists
- Blockquotes
- Links — [djangocfg](https://djangocfg.com)
- Horizontal rules

---

## Code

\`\`\`ts
export function greet(name: string) {
  return \`hello, \${name}\`;
}
\`\`\`

## Quote

> "The best way to predict the future is to invent it." — Alan Kay

## Checklist

1. Draft
2. Review
3. Ship

## Filler

${Array.from({ length: 12 }, (_, i) => `Paragraph ${i + 1}. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.`).join('\n\n')}
`;

const MENTION_ITEMS: MentionConfig = {
  items: [
    { id: '1', label: 'Alice', description: 'Protagonist', thumbnail: 'https://i.pravatar.cc/48?u=alice' },
    { id: '2', label: 'Bob', description: 'Antagonist', thumbnail: 'https://i.pravatar.cc/48?u=bob' },
    { id: '3', label: 'Charlie', description: 'Side character', thumbnail: 'https://i.pravatar.cc/48?u=charlie' },
    { id: '4', label: 'Diana', description: 'Narrator' },
    { id: '5', label: 'Eve', description: 'Mystery character' },
  ],
};

// ── Meta ──

// ── Host (Controls-driven) ──

interface HostProps extends Omit<MarkdownEditorProps, 'value' | 'onChange'> {
  initialContent?: string;
  mentions?: MentionConfig;
}

function Host({ initialContent = '', mentions, ...rest }: HostProps) {
  const [value, setValue] = useState(initialContent);
  return (
    <div className="w-[680px]">
      <MarkdownEditor {...rest} mentions={mentions} value={value} onChange={setValue} />
    </div>
  );
}

const meta = {
  title: 'Widgets/Editor/Editor',
  component: Host,
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component:
          'TipTap-based markdown editor. Supports headings, lists, marks, blockquotes, code, ' +
          'links, and an optional `@`-mention popover. The component is controlled — pass `value` ' +
          'and `onChange`. Use the `ref` (`MarkdownEditorHandle`) to focus or move the caret.',
      },
    },
  },
  argTypes: {
    placeholder: {
      control: 'text',
      table: { category: 'Content' },
    },
    minHeight: {
      control: { type: 'number', min: 40, max: 800, step: 20 },
      table: { category: 'Layout' },
    },
    disabled: {
      control: 'boolean',
      table: { category: 'Behaviour' },
    },
    showToolbar: {
      control: 'boolean',
      table: { category: 'Behaviour' },
    },
    className: { table: { disable: true } },
    mentions: { table: { disable: true } },
    onMentionIdsChange: { table: { disable: true } },
    onSubmit: { table: { disable: true } },
    initialContent: {
      control: 'text',
      table: { category: 'Content' },
    },
  },
} satisfies Meta<typeof Host>;

export default meta;

type Story = StoryObj<typeof meta>;

// ── Playground ──

export const Playground: Story = {
  args: {
    placeholder: 'Write markdown…',
    minHeight: 240,
    disabled: false,
    showToolbar: true,
  },
  render: ({ initialContent, ...args }) => (
    <Host initialContent={initialContent ?? SAMPLE} {...args} />
  ),
};

// ── Curated presets ──

export const Empty: Story = {
  render: () => <Host initialContent="" placeholder="Start typing…" />,
};

export const WithContent: Story = {
  render: () => <Host initialContent={SAMPLE} />,
};

export const ReadOnly: Story = {
  render: () => (
    <div className="w-[680px]">
      <MarkdownEditor value={SAMPLE} onChange={() => {}} disabled />
    </div>
  ),
};

export const NoToolbar: Story = {
  render: () => (
    <Host
      initialContent={'Plain text without toolbar.\n\nStill supports **markdown** shortcuts.'}
      showToolbar={false}
    />
  ),
};

export const Compact: Story = {
  render: () => (
    <div className="w-[420px]">
      <Host initialContent="Short note" minHeight={60} placeholder="Quick note…" />
    </div>
  ),
};

export const LongContent: Story = {
  render: () => (
    <div className="h-[520px] w-[680px] overflow-auto rounded-md border">
      <Host initialContent={LONG_CONTENT} minHeight={480} />
    </div>
  ),
};

// ── Mentions ──

function MentionsHost({
  initial,
  renderMarkdown,
}: {
  initial: string;
  renderMarkdown?: MentionMarkdownRenderer;
}) {
  const [value, setValue] = useState(initial);
  const [ids, setIds] = useState<string[]>([]);
  const mentions: MentionConfig = renderMarkdown
    ? { ...MENTION_ITEMS, renderMarkdown }
    : MENTION_ITEMS;

  return (
    <div className="grid w-[820px] gap-3" style={{ gridTemplateColumns: '1fr 1fr' }}>
      <div>
        <MarkdownEditor
          value={value}
          onChange={setValue}
          mentions={mentions}
          onMentionIdsChange={setIds}
          placeholder="Type @ to mention…"
          minHeight={200}
        />
        {ids.length > 0 && (
          <div className="mt-2 text-xs opacity-60">Mentioned IDs: {ids.join(', ')}</div>
        )}
      </div>
      <div>
        <div className="mb-1 text-[10px] uppercase tracking-wide opacity-50">
          Serialized markdown
        </div>
        <pre className="max-h-[260px] overflow-auto rounded-md border bg-muted/40 p-2 text-xs">
          {value}
        </pre>
      </div>
    </div>
  );
}

export const WithMentions: Story = {
  render: () => (
    <MentionsHost initial="Hello @Alice! Type @ to mention more characters." />
  ),
};

export const WithCustomUriPreset: Story = {
  name: 'Mentions / customUri preset',
  render: () => (
    <MentionsHost
      initial="Reference @Alice and @Bob — markdown carries deep-link URIs."
      renderMarkdown={mentionPresets.customUri('myapp', 'user')}
    />
  ),
};

export const WithMarkdownLinkPreset: Story = {
  name: 'Mentions / markdownLink preset',
  render: () => (
    <MentionsHost
      initial="Ping @Alice when ready, cc @Charlie."
      renderMarkdown={mentionPresets.markdownLink('https://example.com/u/')}
    />
  ),
};

export const WithCustomRenderer: Story = {
  name: 'Mentions / custom renderer',
  render: () => (
    <MentionsHost
      initial="Tag @Alice and @Bob to assign the task."
      renderMarkdown={({ id, label }) => `{{user:${id}|${label || 'unknown'}}}`}
    />
  ),
};

// ── Imperative handle ──

export const ImperativeHandle: Story = {
  name: 'Ref / focus & moveCursorToEnd',
  render: () => {
    function HandleDemo() {
      const ref = useRef<MarkdownEditorHandle>(null);
      const [value, setValue] = useState(SAMPLE);
      return (
        <div className="w-[680px] space-y-2">
          <div className="flex gap-2">
            <button
              type="button"
              className="rounded-md border px-3 py-1 text-xs"
              onClick={() => ref.current?.focus()}
            >
              focus()
            </button>
            <button
              type="button"
              className="rounded-md border px-3 py-1 text-xs"
              onClick={() => ref.current?.moveCursorToEnd()}
            >
              moveCursorToEnd()
            </button>
          </div>
          <MarkdownEditor ref={ref} value={value} onChange={setValue} minHeight={200} />
        </div>
      );
    }
    return <HandleDemo />;
  },
};

// ── File-path chips ──

const FILE_PATH_REPRO =
  'прочти манифест /Users/example/workspace/projects/cmdop/@docs/positioning/manifest.md интересно твоё мнение';

const LONG_PATH =
  '/Users/example/workspace/projects/djangocfg/projects/solution/frontend/packages/ui-tools/src/tools/dev/Map/index.ts';

const FILE_PATH_MIX = [
  'Repro: ' + FILE_PATH_REPRO,
  '',
  'Long path (was wrapping): ' + LONG_PATH,
  '',
  'Windows: C:\\Users\\me\\notes.md',
  'UNC: \\\\srv\\share\\report.xlsx',
  'Home: ~/dev/app/src/index.ts',
  'URI: file:///etc/hosts',
  'Folder: /Users/me/workspace/positioning',
  '',
  'Prose stays plain: a / b stays text.',
].join('\n');

/**
 * Host that shows the editor side-by-side with the serialized markdown so
 * you can confirm chips round-trip to the RAW path / URL on copy / submit.
 */
function ChipRoundTripHost({
  initial,
  filePathChips,
  urlChips,
  minHeight = 220,
}: {
  initial: string;
  filePathChips?: boolean;
  urlChips?: boolean;
  minHeight?: number;
}) {
  const [value, setValue] = useState(initial);
  return (
    <div className="grid w-[860px] gap-3" style={{ gridTemplateColumns: '1fr 1fr' }}>
      <MarkdownEditor
        value={value}
        onChange={setValue}
        minHeight={minHeight}
        filePathChips={filePathChips}
        urlChips={urlChips}
      />
      <div>
        <div className="mb-1 text-[10px] uppercase tracking-wide opacity-50">
          getMarkdown() output (raw path / URL — never chip markup)
        </div>
        <pre className="max-h-[280px] overflow-auto rounded-md border bg-muted/40 p-2 text-xs whitespace-pre-wrap break-all">
          {value}
        </pre>
      </div>
    </div>
  );
}

export const FilePathChips: Story = {
  name: 'File paths / chips (atomic node)',
  render: () => (
    <div className="space-y-2">
      <p className="w-[860px] text-xs opacity-60">
        Absolute local paths render as compact, atomic chips (icon +
        VSCode-style middle-ellipsis label, full path on hover). The chip is a
        NODE that owns its rendering, so a long path collapses to ONE line
        instead of wrapping. Copy / submit / <code>getMarkdown()</code> keep
        the raw path — see the panel on the right. Type a path + space to
        watch it become a chip.
      </p>
      <ChipRoundTripHost initial={FILE_PATH_MIX} minHeight={300} />
    </div>
  ),
};

// ── URL chips ──

const URL_MIX = [
  'Repo: https://github.com/wailsapp/wails/blob/main/v3/README.md',
  '',
  'Docs: https://djangocfg.com/docs/getting-started',
  'Bare host: www.example.com/path/to/page',
  'Mail: mailto:hello@djangocfg.com',
  '',
  'Type a long URL + space to watch it become a chip.',
].join('\n');

export const UrlChips: Story = {
  name: 'URLs / chips (atomic node)',
  render: () => (
    <div className="space-y-2">
      <p className="w-[860px] text-xs opacity-60">
        URLs render as compact, clickable chips (favicon — degrading to a
        globe glyph — + domain and a middle-ellipsis of the path, e.g.{' '}
        <code>github.com/…/README.md</code>; full URL on hover). Replaces the
        plain blue underlined link. Copy / submit keep the raw URL — see the
        panel on the right.
      </p>
      <ChipRoundTripHost initial={URL_MIX} minHeight={260} />
    </div>
  ),
};

export const UrlChipsOff: Story = {
  name: 'URLs / disabled (urlChips=false)',
  render: () => (
    <ChipRoundTripHost
      initial={'Plain link stays a markdown link: https://djangocfg.com/docs'}
      urlChips={false}
      minHeight={140}
    />
  ),
};

export const FilePathChipsOff: Story = {
  name: 'File paths / disabled (filePathChips=false)',
  render: () => {
    function Off() {
      const [value, setValue] = useState(FILE_PATH_REPRO);
      return (
        <div className="w-[680px]">
          <MarkdownEditor
            value={value}
            onChange={setValue}
            filePathChips={false}
            minHeight={140}
          />
        </div>
      );
    }
    return <Off />;
  },
};

// ── Standalone chip (outside the editor) ──

export const StandaloneFilePathChip: Story = {
  name: 'File paths / standalone <FilePathChip>',
  render: () => (
    <div className="flex w-[520px] flex-col items-start gap-3">
      <p className="text-xs opacity-60">
        <code>&lt;FilePathChip&gt;</code> is presentational and works outside
        the editor — e.g. rendering a known path in a message.
      </p>
      <FilePathChip path="/Users/me/manifest.md" />
      <FilePathChip path="/Users/example/workspace/projects/cmdop/@docs/positioning/manifest.md" />
      <FilePathChip path={'C:\\Users\\me\\notes.md'} />
      <FilePathChip path="~/dev/app/src/index.ts" />
      <FilePathChip path="/Users/me/workspace/positioning" />
    </div>
  ),
};

// ── Submit on Enter (chat-style) ──

export const SubmitOnEnter: Story = {
  name: 'Behaviour / submit on Enter',
  render: () => {
    function ChatLike() {
      const [value, setValue] = useState('Press Enter to submit, Shift+Enter for newline.');
      const [log, setLog] = useState<string[]>([]);
      return (
        <div className="w-[680px] space-y-2">
          <MarkdownEditor
            value={value}
            onChange={setValue}
            minHeight={140}
            placeholder="Type a message…"
            onSubmit={() => {
              if (!value.trim()) return false; // let HardBreak fall through
              setLog((prev) => [...prev, value]);
              setValue('');
            }}
          />
          {log.length > 0 && (
            <div className="rounded-md border bg-muted/30 p-2 text-xs">
              <div className="mb-1 text-[10px] uppercase tracking-wide opacity-50">Submitted</div>
              <ul className="space-y-1">
                {log.map((m, i) => (
                  <li key={i} className="font-mono">
                    {m}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      );
    }
    return <ChatLike />;
  },
};
