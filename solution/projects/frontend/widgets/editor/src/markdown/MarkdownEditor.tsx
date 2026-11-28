'use client';

import { useEditor, EditorContent, type Editor } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Placeholder from '@tiptap/extension-placeholder';
import Mention from '@tiptap/extension-mention';
import { Markdown } from '@tiptap/markdown';
import type { AnyExtension } from '@tiptap/core';
import { forwardRef, useEffect, useImperativeHandle, useMemo, useRef } from 'react';
import { useHotkey } from '@djangocfg/ui-core/hooks';
import {
  Bold, Italic, Strikethrough, Heading1, Heading2, Heading3,
  List, ListOrdered, Quote, Minus, Code, type LucideIcon,
} from 'lucide-react';
import { createMentionSuggestion } from './createMentionSuggestion';
import { mentionPresets } from './mentionPresets';
import { SlashCommandNode } from './slash/SlashCommandNode';
import { syncLeadingSlashNode } from './slash/syncSlashNode';
import type { SlashCommandInfo } from './slash/types';
import { SubmitOnEnter } from './submitOnEnter';
import { ChipNode } from './chip/ChipNode';
import { syncChips } from './chip/syncChips';
import type { MentionAttrs, MentionConfig } from './types';
import './styles.css';

// ── Helpers ──

/**
 * Whitelist of URL schemes the autolinker is allowed to turn into a
 * link. We deliberately keep this to real, clickable transports.
 */
const AUTO_LINK_PROTOCOL = /^(?:https?|ftp|mailto|file):/i;

/**
 * Decide whether an autolink candidate should actually become a link.
 *
 * StarterKit's bundled `Link` extension ships with a permissive default
 * `shouldAutoLink` that links any token whose "hostname" contains a dot
 * with a plausible TLD. That over-eagerly turns *bare file paths and
 * dotted filenames* into `http://…` links — e.g. typing a local path
 * like `…/positioning/manifest.md` linkifies `manifest.md` as the
 * Moldova (`.md`) domain, and pasted prose around a dotted token can be
 * swallowed into one anchor. None of that is wanted in a chat composer.
 *
 * We instead require an explicit, known protocol (`http`, `https`,
 * `ftp`, `mailto`, `file`) or a `www.`-prefixed host. linkifyjs has
 * already split the candidate on whitespace, so the match is inherently
 * bounded to a single token — a path like `/a/b/file.md` is never a
 * `*://` URL and never a `www.` host, so it stays plain text, and any
 * Unicode/Cyrillic words after a real URL remain plain text too.
 */
function shouldAutoLinkUrl(url: string): boolean {
  if (AUTO_LINK_PROTOCOL.test(url)) return true;
  // Bare `www.host…` (no scheme) — linkify prepends the default
  // protocol; allow it since it's an unambiguous web address, not a
  // local path.
  if (/^www\.[^\s/$.?#].[^\s]*$/i.test(url)) return true;
  return false;
}

interface MarkdownManager {
  serialize: (json: Record<string, unknown>) => string;
}

/**
 * Serialize the editor document to a markdown string.
 *
 * `@tiptap/markdown` v3 augments the `Editor` with a `getMarkdown()`
 * method; we use it when present and fall back to the storage manager
 * (and ultimately `getText()`) so the editor still produces *something*
 * if the extension shape ever drifts.
 */
function getMarkdown(editor: Editor): string {
  const withMd = editor as Editor & { getMarkdown?: () => string };
  if (typeof withMd.getMarkdown === 'function') return withMd.getMarkdown();
  const storage = editor.storage.markdown as { manager?: MarkdownManager } | undefined;
  if (!storage?.manager) return editor.getText();
  return storage.manager.serialize(editor.getJSON());
}

function extractMentionIds(editor: Editor): string[] {
  const ids: string[] = [];
  editor.state.doc.descendants((node) => {
    if (node.type.name === 'mention' && node.attrs.id) {
      ids.push(node.attrs.id as string);
    }
  });
  return [...new Set(ids)];
}

// ── Types ──

export interface MarkdownEditorProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  minHeight?: number;
  className?: string;
  disabled?: boolean;
  showToolbar?: boolean;
  /**
   * Drop the editor's own border / background / focus ring. Use when
   * the editor is embedded inside a host surface that already draws
   * the frame (e.g. the chat composer's textarea slot) — avoids a
   * double border.
   */
  unstyled?: boolean;
  /**
   * `@`-mention autocomplete config.
   *
   * IMPORTANT: Tiptap's `useEditor` initialises the editor exactly once.
   * The `Mention` extension is only registered when `mentions` is truthy
   * on the FIRST render — handing in a real config later (e.g. after an
   * async items fetch) silently does nothing, and typing `@` will not
   * open the popover.
   *
   * If you want mentions even with async-loaded items, pass
   * `{ items: [] }` from the very first render and update the array
   * when data arrives. Either keep the `MentionConfig` object identity
   * stable across renders and mutate `items` in place (the suggestion
   * plugin captures the config by closure and reads `items` on each
   * query), or accept that swapping the whole object reference is a
   * no-op for the live editor.
   */
  mentions?: MentionConfig;
  /**
   * Slash-command verb list. When set, the editor registers a
   * `SlashCommandNode` extension and replaces a leading `/verb` (whose
   * verb is in this list) in the document with an atomic chip — the
   * TipTap analogue of the plain `<SlashHighlightTextarea>` mirror.
   *
   * Like `mentions`, this is captured by `useEditor` exactly once on
   * first render. To register slash commands at all, pass `[]` from
   * the very first render and mutate / swap as needed. The conversion
   * effect re-reads the list on every value sync (it lives in a ref),
   * so verbs added later are recognised next time the buffer is set.
   *
   * Lives in `@djangocfg/widget-editor/markdown` (not chat) so the
   * editor stays a leaf dependency. Structurally compatible with the
   * chat package's `SlashCommand[]` — pass either directly.
   */
  slashCommands?: readonly SlashCommandInfo[];
  /**
   * Render absolute LOCAL file paths typed/pasted into the editor as
   * compact, atomic file chips (icon + VSCode-style middle-ellipsis label,
   * full path on hover) — Cursor/Finder style. Backed by an inline atom
   * NODE (`editorChip`, `kind: 'path'`), NOT a decoration: the chip owns
   * its rendering so a long path collapses to ONE line (`…/dev/Map/index.ts`)
   * instead of wrapping. The node serialises back to the RAW path, so caret
   * (whole-chip delete), copy, and the submitted markdown all keep the
   * literal `…/manifest.md`. Detection is conservative (absolute Unix /
   * macOS / `~` / Windows-drive / UNC / `file://` only — never bare
   * relative tokens or web URLs).
   *
   * Defaults to ON (the chat composer wants it). Pass `false` for editors
   * that should leave paths as plain text. Like `mentions`/`slashCommands`
   * this is captured by `useEditor` on first render — flipping it after
   * mount won't add/remove the extension on the live instance.
   */
  filePathChips?: boolean;
  /**
   * Render web URLs typed/pasted into the editor as compact, atomic URL
   * chips (favicon — degrading to a globe glyph — + domain and a
   * middle-ellipsis of the path, e.g. `github.com/…/README.md`, full URL on
   * hover). Clickable (opens in a new tab, `rel=noopener`). Same atom NODE
   * as the file-path chip (`editorChip`, `kind: 'url'`); it REPLACES the
   * plain blue underlined link look and serialises back to the RAW URL so
   * copy / submit / markdown keep the literal address. Uses the same
   * autolink whitelist as the editor (`http`/`https`/`ftp`/`mailto`/`file`
   * + bare `www.`).
   *
   * Defaults to ON. Captured on first render like `filePathChips`.
   */
  urlChips?: boolean;
  /** Called when mentioned IDs change */
  onMentionIdsChange?: (ids: string[]) => void;
  /**
   * Called when the user presses Enter (without Shift, no IME
   * composition, no mention popover open). When set, Enter submits
   * and Shift+Enter inserts a newline — ChatGPT / Telegram chat
   * behaviour. When omitted, Enter behaves as Tiptap default
   * (HardBreak).
   *
   * Implementation lives in `submitOnEnter.ts` — it's a Tiptap
   * keymap extension, NOT a React wrapper handler. Wrapper-level
   * onKeyDown fires AFTER ProseMirror's keymap commits HardBreak in
   * the same tick; routing through the extension lets us intercept
   * before HardBreak runs.
   *
   * Return value (optional): truthy / undefined = consume the key
   * (default). Return `false` from onSubmit to let Tiptap fall
   * through to HardBreak — useful for guards like "don't submit an
   * empty draft".
   */
  onSubmit?: () => boolean | void;
  /**
   * Focus the editor on mount. Pair with `key={file}` upstream when the
   *  host wants a fresh focus per file change (inspector / editor tab).
   */
  autoFocus?: boolean;
  /**
   * Called when the user presses Cmd/Ctrl+S inside the editor. Receives
   * the current markdown. The browser's "save page" default is suppressed
   *  only when this handler is supplied — otherwise Cmd+S falls through.
   */
  onSave?: (markdown: string) => void;
}

/**
 * Imperative handle exposed via `ref`. Shaped for
 * `@djangocfg/widget-forms/composer-registry` so consumers can forward it
 * straight into `useRegisterComposer({ focus, moveCursorToEnd })` — that's what
 * makes voice dictation (`VoiceComposerSlot`) push live text into a TipTap
 * composer.
 */
export interface MarkdownEditorHandle {
  /** Move keyboard focus into the editor. */
  focus: () => void;
  /** Place the caret at the end of the document (and focus). */
  moveCursorToEnd: () => void;
  /** Escape hatch — the underlying TipTap `Editor` instance. */
  getEditor: () => Editor | null;
}

// ── Component ──

export const MarkdownEditor = forwardRef<MarkdownEditorHandle, MarkdownEditorProps>(function MarkdownEditor(
  {
    value,
    onChange,
    placeholder = 'Write markdown...',
    minHeight = 120,
    className = '',
    disabled = false,
    showToolbar = true,
    unstyled = false,
    mentions,
    slashCommands,
    filePathChips = true,
    urlChips = true,
    onMentionIdsChange,
    onSubmit,
    autoFocus = false,
    onSave,
  },
  ref,
) {
  // Keep the latest onSubmit in a ref so the Tiptap extension's
  // keymap closure always calls the freshest handler — Tiptap's
  // useEditor initialises extensions ONCE on first render. Without
  // the ref the extension would call a stale onSubmit (e.g. one
  // that references an outdated `value`).
  const onSubmitRef = useRef(onSubmit);
  onSubmitRef.current = onSubmit;
  const isExternalUpdate = useRef(false);

  // Slash list lives in a ref so verbs added at runtime (e.g. context-
  // aware commands registered after a first reply) are still recognised
  // by the post-`setContent` conversion pass. The editor extension itself
  // is registered once on mount — that is intentional and matches how
  // `mentions` works (Tiptap's `useEditor` captures extensions once).
  const slashCommandsRef = useRef<readonly SlashCommandInfo[]>(
    slashCommands ?? [],
  );
  slashCommandsRef.current = slashCommands ?? [];
  const slashEnabledOnMountRef = useRef<boolean>(slashCommands !== undefined);
  // File-path / URL chips: captured once on mount (the ChipNode extension is
  // installed on first render, like mentions/slash). Both default ON. Kept
  // in refs so the post-`setContent` `syncChips` pass reads the right flags.
  const filePathChipsOnMountRef = useRef<boolean>(filePathChips);
  const urlChipsOnMountRef = useRef<boolean>(urlChips);
  const slashWarnedRef = useRef(false);
  if (
    process.env.NODE_ENV !== 'production' &&
    !slashEnabledOnMountRef.current &&
    slashCommands !== undefined &&
    !slashWarnedRef.current
  ) {
    slashWarnedRef.current = true;
    console.warn(
      '[MarkdownEditor] `slashCommands` flipped from undefined to a list ' +
        'after mount. Tiptap only installs the SlashCommandNode extension ' +
        'on first render — the in-editor chip will NOT appear for this ' +
        'editor instance. Pass `[]` from the very first render and mutate ' +
        'the array in place (or swap references) so the conversion effect ' +
        'sees the new verbs.',
    );
  }

  // ── Dev-mode trap detector ──
  // Tiptap initialises the editor once with the extensions array from
  // first render. If `mentions` is undefined on mount and becomes
  // truthy later, the Mention extension is never installed and the
  // user-visible @-trigger silently does nothing. Catch this early so
  // future consumers don't spend hours debugging why @ does nothing.
  const initialMentionsDefinedRef = useRef<boolean>(mentions !== undefined);
  const warnedRef = useRef(false);
  if (
    process.env.NODE_ENV !== 'production' &&
    !initialMentionsDefinedRef.current &&
    mentions !== undefined &&
    !warnedRef.current
  ) {
    warnedRef.current = true;
    console.warn(
      '[MarkdownEditor] `mentions` flipped from undefined to a config ' +
        'after mount. Tiptap only installs the Mention extension on first ' +
        'render — the @-popover will NOT work for this editor instance. ' +
        'Pass `{ items: [] }` from the very first render and mutate `.items` ' +
        'in place instead.',
    );
  }

  const extensions = useMemo(() => {
    const exts: AnyExtension[] = [
      StarterKit.configure({
        heading: { levels: [1, 2, 3] },
        // Constrain the bundled Link extension's autolinker. The default
        // links bare dotted tokens (e.g. a file path's `manifest.md`)
        // and can over-capture pasted prose; we only auto-link real
        // URLs (explicit scheme or `www.`). `defaultProtocol: 'https'`
        // is the modern default for the rare schemeless `www.` case.
        //
        // When `urlChips` is ON the ChipNode OWNS URL rendering (a chip,
        // not a blue underline), so we turn OFF the link autolinker to
        // avoid the two fighting over the same token. Markdown `[text](url)`
        // links typed deliberately still render via the link mark — only
        // the implicit autolink of a bare URL is suppressed.
        link: {
          defaultProtocol: 'https',
          autolink: !urlChipsOnMountRef.current,
          shouldAutoLink: shouldAutoLinkUrl,
        },
      }),
      Placeholder.configure({ placeholder }),
      Markdown,
      // SubmitOnEnter — when the consumer wired an onSubmit, intercept
      // Enter at the keymap level (before StarterKit's HardBreak).
      // The extension calls through `onSubmitRef.current` so handler
      // identity changes don't require an editor rebuild. See
      // submitOnEnter.ts for the keymap-vs-wrapper-handler rationale.
      SubmitOnEnter.configure({
        onSubmit: () => {
          const h = onSubmitRef.current;
          if (!h) return false; // no handler → let Tiptap insert HardBreak
          return h();
        },
      }),
    ];

    // SlashCommandNode — TipTap atom that paints the `/verb` chip.
    // Registered whenever `slashCommands` was defined on first render
    // (the empty array still counts as "I want this feature"). The
    // node has no suggestion plugin of its own — the chat composer's
    // floating menu drives selection and the editor only needs to
    // know how to render + serialize the atom.
    if (slashEnabledOnMountRef.current) {
      exts.push(SlashCommandNode);
    }

    // ChipNode — a single inline ATOM node that renders BOTH file-path
    // chips (`kind: 'path'`) and URL chips (`kind: 'url'`) with a
    // VSCode-style middle-ellipsis label, and serialises back to the raw
    // path / URL. Registered whenever either chip feature is on (the node's
    // input/paste rules are gated per-kind via `enablePaths`/`enableUrls`).
    // Replaces the old FilePathChipExtension decoration — a node owns its
    // rendering, so a long path collapses to ONE line instead of wrapping.
    if (filePathChipsOnMountRef.current || urlChipsOnMountRef.current) {
      exts.push(
        ChipNode.configure({
          enablePaths: filePathChipsOnMountRef.current,
          enableUrls: urlChipsOnMountRef.current,
        }),
      );
    }

    if (mentions) {
      // ── Why .extend() with renderMarkdown ──
      //
      // Tiptap's `Mention` extension ships a default markdown serializer
      // (via `createInlineMarkdownSpec`, see @tiptap/extension-mention)
      // that emits a shortcode like `[@ id="..." label="..."]`. That's
      // round-trippable but useless for most consumers: a chat composer
      // feeding an LLM wants `@<label>`, a deep-linking app wants a
      // markdown link, etc.
      //
      // `renderText` only affects `editor.getText()` and the rendered
      // node — it does NOT influence `@tiptap/markdown`'s serializer.
      // The serializer reads `renderMarkdown` off the extension config
      // (see MarkdownManager.registerExtension → getExtensionField).
      // Overriding it via `.extend({ renderMarkdown })` replaces the
      // shortcode output with whatever the consumer supplied (or the
      // `plainAt` default — see ./mentionPresets.ts).
      //
      // Renderer-choice capture: useEditor only initialises once, so the
      // chosen renderer is captured by closure on first render. This is
      // intentional — swapping renderers per render would mean tearing
      // the editor down anyway, which we don't do for any other prop.
      //
      // Round-trip note: we intentionally do NOT also override
      // `parseMarkdown` / `markdownTokenizer`. Once a mention is
      // serialized, parsing it back would need the original mention
      // items list to look up the id, which we don't have at parse time.
      // Mentions are write-only by design here — `setContent(value)`
      // after submit gets back a plain string, which is fine for the
      // chat use case.
      const renderMarkdown = mentions.renderMarkdown ?? mentionPresets.plainAt;
      exts.push(
        Mention.extend({
          renderMarkdown(node) {
            const raw = node.attrs as { label?: string | null; id?: string | null };
            const attrs: MentionAttrs = {
              id: raw?.id ?? '',
              label: raw?.label ?? '',
            };
            // Defensive: if both are empty (shouldn't happen for a real
            // mention node, but `setContent` of malformed data could),
            // emit nothing rather than a stray "@" or invalid link.
            if (!attrs.id && !attrs.label) return '';
            return renderMarkdown(attrs);
          },
        }).configure({
          HTMLAttributes: { class: 'markdown-mention' },
          suggestion: createMentionSuggestion(mentions),
          renderText: ({ node }) => `@${node.attrs.label}`,
        }),
      );
    }

    return exts;
  }, [placeholder, mentions]);

  const editor = useEditor({
    immediatelyRender: false,
    editable: !disabled,
    extensions,
    content: value,
    // `value` is a markdown string — without this Tiptap treats the
    // content as JSON and renders `# Hello` literally instead of an <h1>.
    contentType: 'markdown',
    onUpdate: ({ editor }) => {
      if (isExternalUpdate.current) return;
      // Promote a freshly-typed `/verb ` text run into a chip so users
      // who type the command without going through the menu still see
      // the highlight — matches the plain mirror's behaviour where
      // `extractSlashToken` works for any leading slash. The helper is
      // idempotent and a no-op when no leading text-slash exists.
      if (slashEnabledOnMountRef.current) {
        const replaced = syncLeadingSlashNode(editor, slashCommandsRef.current);
        if (replaced) {
          // The chain() above triggers an extra onUpdate. The string
          // serialisation is unchanged (atom flattens to its token via
          // `renderText`), so we still want the outer onChange to fire
          // with the canonical value. Falling through is fine.
        }
      }
      onChange(getMarkdown(editor));

      if (onMentionIdsChange) {
        onMentionIdsChange(extractMentionIds(editor));
      }
    },
    editorProps: {
      attributes: {
        // 15px matches the `.ProseMirror` typographic baseline in
        // styles.css — a comfortable chat-composer body size. Do NOT
        // shrink to `text-sm` here: that 14px override made the composer
        // input read too small against the rest of the chat surface.
        class: 'markdown-editor-content focus:outline-none text-[15px]',
        style: `min-height: ${minHeight}px`,
      },
      handleDOMEvents: {
        // FILE drops must NOT be consumed by ProseMirror. PM's built-in
        // `editHandlers.drop` calls `event.preventDefault()` on the editor
        // surface (prosemirror-view: handleDrop), which swallows a file
        // drop before it can bubble to the host wrapper's `onDrop` (the
        // chat composer's attach pipeline).
        //
        // PM's dispatch (prosemirror-view `dispatchEvent`) runs the
        // built-in handler ONLY when the custom handler returns a falsy
        // value AND did not `preventDefault`. So to let a file drop reach
        // the composer we must:
        //   • return `true`  → tells PM "handled", it SKIPS its built-in
        //                       drop, so it never preventDefaults; the
        //                       native event keeps bubbling to React onDrop.
        //   • NOT preventDefault here (that would also block the bubble
        //     target from acting, and PM treats defaultPrevented as
        //     "handled" too — same skip, but we keep it explicit).
        // For text / node drops (no `dataTransfer.files`) return `false`
        // so PM's normal in-editor drop handling runs unchanged.
        drop: (_view, event) => {
          const dt = (event as DragEvent).dataTransfer;
          if (dt && dt.files && dt.files.length > 0) {
            // Hands-off: skip PM's drop, let it bubble to composer.onDrop.
            return true;
          }
          return false;
        },
      },
    },
  });

  // Sync external `value` → editor. `setContent` is given `contentType:
  // 'markdown'` so the string is parsed (not treated as JSON), and
  // `emitUpdate: false` so it does NOT re-fire `onUpdate` (which would
  // loop back into `onChange`). `isExternalUpdate` stays as a guard.
  useEffect(() => {
    if (!editor) return;
    const current = getMarkdown(editor);
    if (current !== value) {
      // `setContent` replaces the ProseMirror document and therefore creates a
      // fresh selection. In a controlled chat editor an unrelated parent
      // render can arrive while the user is typing; without preserving this
      // selection Chromium may release focus to <body> or place the caret at
      // document start. External content still wins, but it must never erase
      // the user's active editing position.
      const hadFocus = editor.isFocused;
      const previousSelection = editor.state.selection;
      isExternalUpdate.current = true;
      editor.commands.setContent(value, { contentType: 'markdown', emitUpdate: false });
      // After the new content is written, convert a leading `/verb` text
      // run into a `SlashCommandNode` atom so the chip appears. The
      // helper is a no-op when (a) slash commands are not enabled,
      // (b) the buffer doesn't start with a known verb, or (c) the
      // document already begins with the atom. `emitUpdate: false` on
      // setContent + `isExternalUpdate.current` still being `true`
      // suppresses the onUpdate -> onChange feedback loop the chain()
      // call would otherwise trigger.
      if (slashEnabledOnMountRef.current) {
        syncLeadingSlashNode(editor, slashCommandsRef.current);
      }
      // Convert any bare path / URL text in the freshly-parsed markdown into
      // chip atoms. Input/paste rules handle live typing; this covers
      // content that arrived via the controlled `value` (parsed straight to
      // plain text). The chips serialise back to the raw string, so the next
      // `getMarkdown(editor)` still equals `value` — no feedback loop.
      if (filePathChipsOnMountRef.current || urlChipsOnMountRef.current) {
        syncChips(editor, {
          paths: filePathChipsOnMountRef.current,
          urls: urlChipsOnMountRef.current,
        });
      }
      isExternalUpdate.current = false;

      if (hadFocus) {
        // SetContent / chip normalization can shorten the document. Clamp the
        // old range to the new valid bounds, then restore it after focusing so
        // both a collapsed caret and a text selection remain where the user
        // left them. We intentionally do not focus an editor that was not
        // active — a background update must not steal focus from another UI.
        const maxPosition = editor.state.doc.content.size;
        const from = Math.max(1, Math.min(previousSelection.from, maxPosition));
        const to = Math.max(1, Math.min(previousSelection.to, maxPosition));
        editor.chain().focus().setTextSelection({ from, to }).run();
      }
    }
  }, [value, editor]);

  // Keep editability in sync with the `disabled` prop. `useEditor` only
  // reads `editable` on init, so toggling `disabled` later is otherwise
  // a no-op.
  useEffect(() => {
    editor?.setEditable(!disabled);
  }, [editor, disabled]);

  // Declarative autoFocus — runs once the editor instance exists. Hosts
  // that want per-file focus reset should pair this with `key={path}`.
  useEffect(() => {
    if (!autoFocus || !editor) return;
    editor.commands.focus('end');
  }, [autoFocus, editor]);

  // Cmd/Ctrl+S → save. Uses the shared `useHotkey` (inInput=true by
  // default for modifier combos). Guarded to fire only when focus is
  // inside this editor's ProseMirror DOM, so multiple sibling editors
  // don't all fire on one chord.
  const onSaveRef = useRef(onSave);
  onSaveRef.current = onSave;
  useHotkey(
    'mod+s',
    () => {
      const h = onSaveRef.current;
      if (!h || !editor) return;
      const dom = editor.view.dom;
      const active = document.activeElement;
      if (!active || !dom.contains(active)) return;
      h(getMarkdown(editor));
    },
    { enabled: !!editor && !!onSave },
  );

  // Imperative API for hosts that drive the editor without owning a
  // TipTap ref directly — chat composer registration, voice slot,
  // focus-on-stream-end.
  useImperativeHandle(
    ref,
    (): MarkdownEditorHandle => ({
      focus: () => {
        editor?.commands.focus();
      },
      moveCursorToEnd: () => {
        editor?.commands.focus('end');
      },
      getEditor: () => editor ?? null,
    }),
    [editor],
  );

  // `unstyled` drops the editor's own frame (border / bg / focus ring)
  // so it can sit inside a host surface that already draws one.
  const chromeClass = unstyled
    ? 'markdown-editor--unstyled'
    : 'rounded-md border border-input bg-background';
  const wrapperClass = `markdown-editor ${chromeClass} ${disabled ? 'opacity-60' : ''} ${className}`.trim();

  // Inner content padding.
  //
  // Standalone editor: comfy `px-3 py-2` frame.
  //
  // Unstyled (embedded in the chat composer surface): the host owns the
  // OUTER frame, but the editor text still needs a small, EVEN inset so
  // it doesn't sit flush in the corner. We give it a balanced horizontal +
  // top inset and a DELIBERATELY tighter bottom (`pb-px`): a symmetric
  // `py-2` would stack a second 8px gap under the single caret line and
  // read as a phantom empty line (the bug this replaces). `pt-1.5 pb-px`
  // breathes at the top without re-introducing the bottom gap; `px-2`
  // keeps left == right so the caret isn't jammed against the edge.
  const contentPad = unstyled ? 'px-2 pt-1.5 pb-px' : 'px-3 py-2';

  return (
    <div className={wrapperClass}>
      {showToolbar && editor && <MarkdownToolbar editor={editor} />}
      <div className={contentPad}>
        <EditorContent editor={editor} />
      </div>
    </div>
  );
});

// ── Toolbar ──

interface ToolbarItem {
  icon: LucideIcon;
  action: () => void;
  active: boolean;
  title: string;
}

function MarkdownToolbar({ editor }: { editor: Editor }) {
  const items = useMemo<(ToolbarItem | null)[]>(() => [
    { icon: Bold, title: 'Bold', action: () => editor.chain().focus().toggleBold().run(), active: editor.isActive('bold') },
    { icon: Italic, title: 'Italic', action: () => editor.chain().focus().toggleItalic().run(), active: editor.isActive('italic') },
    { icon: Strikethrough, title: 'Strike', action: () => editor.chain().focus().toggleStrike().run(), active: editor.isActive('strike') },
    { icon: Code, title: 'Code', action: () => editor.chain().focus().toggleCode().run(), active: editor.isActive('code') },
    null,
    { icon: Heading1, title: 'H1', action: () => editor.chain().focus().toggleHeading({ level: 1 }).run(), active: editor.isActive('heading', { level: 1 }) },
    { icon: Heading2, title: 'H2', action: () => editor.chain().focus().toggleHeading({ level: 2 }).run(), active: editor.isActive('heading', { level: 2 }) },
    { icon: Heading3, title: 'H3', action: () => editor.chain().focus().toggleHeading({ level: 3 }).run(), active: editor.isActive('heading', { level: 3 }) },
    null,
    { icon: List, title: 'Bullet list', action: () => editor.chain().focus().toggleBulletList().run(), active: editor.isActive('bulletList') },
    { icon: ListOrdered, title: 'Ordered list', action: () => editor.chain().focus().toggleOrderedList().run(), active: editor.isActive('orderedList') },
    { icon: Quote, title: 'Quote', action: () => editor.chain().focus().toggleBlockquote().run(), active: editor.isActive('blockquote') },
    { icon: Minus, title: 'Divider', action: () => editor.chain().focus().setHorizontalRule().run(), active: false },
  ], [editor]);

  return (
    <div
      className="flex items-center gap-0.5 px-2 py-1.5 border-b border-border"
      role="toolbar"
      aria-label="Text formatting"
    >
      {items.map((item, i) => {
        if (!item) {
          return <div key={i} className="w-px h-4 bg-border mx-1" aria-hidden="true" />;
        }
        const Icon = item.icon;
        const btnClass = `markdown-toolbar-btn ${item.active ? 'active' : ''}`;
        return (
          <button
            key={i}
            type="button"
            // Prevent the button from stealing focus from the editor on
            // mousedown — keeps the selection intact so the formatting
            // command applies to the user's current selection.
            onMouseDown={(e) => e.preventDefault()}
            onClick={item.action}
            title={item.title}
            aria-label={item.title}
            aria-pressed={item.active}
            className={btnClass}
          >
            <Icon style={{ width: 14, height: 14 }} aria-hidden="true" />
          </button>
        );
      })}
    </div>
  );
}
