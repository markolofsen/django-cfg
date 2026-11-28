# MarkdownMessage

Chat-tuned, read-only markdown renderer. Drop-in for any chat bubble — assistant or user.

```tsx
import { MarkdownMessage } from '@djangocfg/widget-code/markdown-message';

<MarkdownMessage content={text} isUser={false} />
```

## What it gives you

| Feature | Source |
|---|---|
| GitHub Flavored Markdown — tables, strikethrough, autolinks, task lists | `remark-gfm` |
| Single `\n` becomes a hard line break (chat convention) | `remark-breaks` |
| Smart typography — `"…"` → `"…"`, `--` → `—`, `...` → `…` | `remark-smartypants` |
| Emoji shortcodes — `:rocket:` → 🚀 | `remark-emoji` |
| External links auto-tagged with `target="_blank" rel="noopener noreferrer"` | `rehype-external-links` |
| Inline HTML, parsed and sanitized (XSS-safe) | `rehype-raw` + `rehype-sanitize` |
| Syntax-highlighted code fences with copy button | `<PrettyCode>` |
| Mermaid diagrams (` ```mermaid ` fence) with click-to-fullscreen | `<Mermaid>` |
| Custom URL schemes via declarative `linkRules` | `./linkRules.ts` |
| Opt-in URL chips (bare URLs → favicon + middle-ellipsis chip) | `urlChipRule` · `./builtinRules.tsx` |
| Plain-text fast path — short messages skip the markdown pipeline | `./plainText.ts` |
| Optional collapsible "Read more" for long replies | `useCollapsibleContent` |
| Hover-revealed copy action under the bubble (separate `<ActionRow>` export) | `<CopyButton>` (ui-core) |
| User vs assistant palette via `isUser` flag | semantic theme tokens |

## Why these plugins

Chat bubbles aren't documents. We picked plugins that fix the gap between CommonMark
and how people actually type in chats:

- **`remark-breaks`** — CommonMark collapses single newlines into spaces. LLMs and
  users routinely write joke punchlines, poems, and dialogue separated by single
  newlines. Without this, "— Доктор, я общаюсь только через мессенджер.\n— Что жена
  говорит?" renders as one run-on line. ChatGPT, Slack, Discord, Linear all do this.
- **`remark-smartypants`** — Cheap "humanized" polish: ASCII quotes become typographic
  quotes, double-dash becomes em-dash, three dots become an ellipsis. Same rule as
  Medium / Substack. Applied before emoji so quotes around shortcodes still curl.
- **`remark-emoji`** — Shortcode → Unicode (`:tada:` → 🎉). Already-Unicode emoji
  pass through untouched.
- **`rehype-external-links`** — One pass at the end tags every `<a>` that survived
  sanitize. Replaces ad-hoc `target=_blank` checks in the `a` renderer; works for
  custom `linkRules`-supplied anchors too.

Plugin order in `MarkdownMessage.tsx` is load-bearing — see the inline comment.

## Plain-text fast path

`MarkdownMessage` looks at the content and decides:

- **Short, single-paragraph, no markdown markers** → render as flat
  `<div whitespace-pre-wrap>`. Cheaper, preserves newlines verbatim, doesn't
  parse `*stars*` or `#hash` that the user happened to type.
- **Anything else** → full ReactMarkdown pipeline.

Override with `plainText={true | false}` if you know better than the heuristic
(common case: user-typed bubbles always pass `plainText` so their `*` stays as `*`).

## Custom URL schemes (`linkRules`)

`linkRules` is the supported way to plug in app-specific URL handlers (`cmdop://`,
`obsidian://`, custom file links, mention chips). Each rule:

- declares its `protocols` (whitelisted into the sanitizer);
- optionally `preprocess`es the source string;
- `match`es an href and `render`s a custom node.

```tsx
const rules: LinkRule[] = [
  {
    name: 'cmdop-machine-mention',
    protocols: ['cmdop'],
    match: (href) => href.startsWith('cmdop://machine/'),
    render: ({ href, children }) => <MentionChip id={href} label={children} />,
  },
];

<MarkdownMessage content="Talk to [Server-A](cmdop://machine/abc-123)" linkRules={rules} />
```

The plain `a` renderer keeps its palette and typography; `linkRules` only fires
when both the `protocols` and the `match` predicate accept the href. See
`linkRules.ts` for the sanitize-extension logic.

### Built-in `urlChipRule` (URL chips)

`urlChipRule` (exported from `./builtinRules`) is a shipped, **opt-in** `LinkRule`
that renders a URL as a compact `<UrlChip>` — favicon + domain + middle-ellipsis
path (`github.com/…/README.md`), the same chip the chat composer shows while you
type a URL. It is not applied automatically; a host appends it to its own
`linkRules`:

```tsx
import { MarkdownMessage, urlChipRule } from '@djangocfg/widget-code/markdown-message';

<MarkdownMessage content={text} linkRules={[urlChipRule]} />
```

In the Chat tool this is wired by `ChatConfig.linkChips` (off by default); when
on, `MessageBubble` passes `linkRules={[urlChipRule]}`.

Behaviour:

- **Bare URLs only.** It chips a link whose rendered label *is* the href (a
  plain autolink, trailing-slash difference tolerated). A `[labeled](url)` link
  keeps the author's text and renders as a normal styled link — the rule falls
  back to an `<a>` using the chat `ANCHOR` tokens so it stays colored +
  underlined, not stripped to plain text.
- **Scope is `http(s)` only** (`match: /^https?:\/\//i`). `mailto:` / custom
  schemes (`cmdop://`, …) are left to other rules, so it needs no `protocols`
  whitelist.
- **`www.` host promotion.** Its `preprocess` hook rewrites bare `www.host…`
  tokens to `https://www.host…` before parsing — GFM only autolinks tokens with
  a scheme, so without this a bare `www.` host would reach neither the rule nor
  the default anchor and render as plain text. The promotion is boundary-guarded
  so it never double-prefixes an already-schemed URL.

`UrlChip` itself is the surface-agnostic chip in `src/common/chips` — see
[`common/chips/README.md`](../../../../common/chips/README.md).

## Copy action (`<ChatMessageRow>` + `<ActionRow>`)

Two pieces, two responsibilities:

- **`<ActionRow>`** — dumb leaf. Knows the side (`isUser`) and the
  text to copy (`value`). Owner controls visibility via `visible`.
- **`<ChatMessageRow>`** — opinionated wrapper. Owns the bubble +
  action-row layout, hover state with a 250 ms close delay, touch
  fallback, focus management, and absolute positioning for the row
  so a hidden row never claims vertical space.

The split exists because:

1. `MarkdownMessage` doesn't know whether it lives in a saturated
   `bg-primary` bubble or a neutral card — putting the copy icon
   inside would force it to fight the bubble's palette.
2. CSS-only `group-hover` bridges flicker when the cursor crosses
   the gap between the bubble and the (initially-invisible) row.
   State + a small close timeout is the same pattern Radix Tooltip
   uses for the same reason.

```tsx
import { MarkdownMessage, ChatMessageRow, ActionRow } from '@djangocfg/widget-code/markdown-message';

function ChatBubble({ role, content }) {
  const isUser = role === 'user';
  return (
    <ChatMessageRow
      isUser={isUser}
      actions={(visible) => (
        <ActionRow value={content} isUser={isUser} visible={visible} />
      )}
    >
      <div
        className={
          isUser
            ? 'bg-primary text-primary-foreground rounded-xl px-3 py-2'
            : 'bg-card border border-border rounded-xl px-3 py-2'
        }
      >
        <MarkdownMessage content={content} isUser={isUser} plainText={isUser} />
      </div>
    </ChatMessageRow>
  );
}
```

Behaviour:

- **Desktop:** hidden until you hover anywhere over the row (bubble
  or its action area). 250 ms close delay so cursor travel from
  bubble to button never flickers. Fades over 150 ms.
- **Touch (`@media (hover: none), (pointer: coarse)`):** always
  visible at full opacity, in-flow under the bubble (so it claims
  honest layout space — touch users have no hover, the affordance
  must always be reachable).
- **Keyboard:** `focus-within` opens the row, `blur` outside the row
  schedules the same close timeout.
- **Side:** the row sits on the same side as the bubble (`isUser`
  flips alignment); the icon itself is never mirrored.

Pass the original `content` string to `ActionRow.value` so collapsed
bubbles still copy the full text, not the truncated `displayContent`.

The `actions` prop is a render-prop (`(visible, isUser) => ReactNode`)
so it's already future-proof for richer rows like
`[Copy] [Like] [Regenerate]`.

## Files

| File | Purpose |
|---|---|
| `MarkdownMessage.tsx` | Main component — composes plugins, runs heuristic, renders |
| `components.tsx` | The `Components` map — typography, lists, table, code, blockquote, hr |
| `CodeBlock.tsx` | Code-fence renderer (`PrettyCode`) + plain `<pre>` fallback |
| `linkRules.ts` | Declarative custom-URL primitive — schema & helpers |
| `builtinRules.tsx` | Shipped opt-in rules — `urlChipRule` (bare URL → `<UrlChip>`) |
| `plainText.ts` | `looksLikePlainProse` heuristic + `extractTextFromChildren` utility |
| `sanitize.ts` | Extended rehype-sanitize schema + `urlTransform` builder |
| `CollapseToggle.tsx` | "Read more / Show less" affordance for long replies |
| `ActionRow.tsx` | Dumb action row (copy button); owner toggles `visible` |
| `ChatMessageRow.tsx` | Bubble + action-row wrapper with hover state and touch fallback |
| `MarkdownMessage.story.tsx` | Storybook — kitchen sink, link rules, mermaid, soft breaks, plugin sampler |

## Stories

Open the storybook and look at:

- `Markdown Message / Link Rules` — declarative `linkRules` API in three modes.
- `Markdown Message / Chat Bubbles` — plain-text fast path vs heuristic vs long reply.
- `Markdown Message / Soft Line Breaks` — the `remark-breaks` regression case (joke,
  poem, dialogue).
- `Markdown Message / Chat Plugins` — emoji shortcodes, smart typography, external
  link tagging, in one bubble.
- `Markdown Message / Kitchen Sink` — every block element together, used to spot
  spacing regressions at a glance.
- `Markdown Message / Mermaid Diagrams` — flowchart + sequence diagram in a bubble.
- `Markdown Message / Copy Actions` — hover-revealed copy button on user and assistant bubbles.
