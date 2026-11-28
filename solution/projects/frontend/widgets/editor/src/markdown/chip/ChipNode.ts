/**
 * `ChipNode` — a single TipTap inline ATOM node that renders BOTH file-path
 * chips and URL chips, distinguished by a `kind` attribute. Replaces the old
 * `FilePathChipExtension` decoration approach.
 *
 * Why a node (not a decoration), and why VSCode-style middle-ellipsis:
 *
 *   The previous decoration was an OVERLAY — it could add a class + icon
 *   widget over the raw path text, but it could NOT replace the visible
 *   text. A long path therefore rendered in FULL and wrapped to several
 *   lines. An atomic inline node OWNS its rendering, so it can show a
 *   middle-ellipsised label (`…/dev/Map/index.ts`) on a single line while
 *   the FULL path lives only in the node's `path` attribute (and in copy /
 *   markdown output). This mirrors how `@tiptap/extension-mention` and the
 *   `SlashCommandNode` are atomic inline nodes that flatten back to plain
 *   text on serialise.
 *
 * Two kinds, one node (DRY):
 *
 *   - `kind: 'path'`  — attr `path`. Icon = `getFileIcon(base).svg` (folder
 *     glyph when `isDir`). Label = `truncatePathLabel(path)`. Serialises to
 *     the RAW `path` string.
 *   - `kind: 'url'`   — attr `href`. Icon = a favicon (Google S2) that
 *     degrades to a globe glyph on error. Label = domain + middle-ellipsis
 *     of the path (`github.com/…/README.md`). Clickable (opens in a new
 *     tab). Serialises to the RAW `href` string.
 *
 * Serialisation (the whole point — text/markdown fidelity):
 *
 *   `renderText` and `renderMarkdown` BOTH emit the literal raw path/href,
 *   so `editor.getText()`, copy, the submitted message, and `getMarkdown()`
 *   all contain the real string — NEVER chip markup. URLs serialise as a
 *   bare URL (the editor's autolinker re-links a bare URL on the next
 *   `setContent`, matching how the editor already treats pasted URLs).
 *
 * Auto-conversion:
 *
 *   An input rule fires when the user types a path/URL followed by a
 *   boundary (space / newline / punctuation) and replaces the matched range
 *   with a chip node. A paste rule does the same for pasted text. Both reuse
 *   the pure detectors (`findFilePaths`, `findUrls`) so detection never
 *   drifts from the standalone chip / autolinker.
 *
 * The node renders via a DOM `addNodeView` (no React mount) — robust, cheap,
 * and consistent with the React-free icon the old decoration used.
 */

import { Node, mergeAttributes, InputRule } from '@tiptap/core';
import type { JSONContent, MarkdownRendererHelpers, RenderContext } from '@tiptap/core';
import { Plugin, PluginKey, TextSelection } from '@tiptap/pm/state';
import { Fragment, Slice } from '@tiptap/pm/model';
import { findFilePaths, splitPath, truncatePathLabel } from '../filePath/detect';
import { findUrls, splitUrl, truncateUrlLabel, faviconUrl } from '../url/detect';
import { getFileIcon } from '@djangocfg/widget-data/file-icon/get-file-icon';

export type ChipKind = 'path' | 'url';

export interface ChipNodeOptions {
  /** Enable auto-conversion of typed/pasted file paths into `path` chips. */
  enablePaths: boolean;
  /** Enable auto-conversion of typed/pasted URLs into `url` chips. */
  enableUrls: boolean;
  HTMLAttributes: Record<string, unknown>;
}

const chipPasteKey = new PluginKey('editorChipPaste');

const FOLDER_SVG =
  '<svg viewBox="0 0 24 24" width="14" height="14" fill="none" ' +
  'stroke="currentColor" stroke-width="2" stroke-linecap="round" ' +
  'stroke-linejoin="round"><path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2' +
  'h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 ' +
  '2 0 0 0 2 2Z"/></svg>';

const GLOBE_SVG =
  '<svg viewBox="0 0 24 24" width="14" height="14" fill="none" ' +
  'stroke="currentColor" stroke-width="2" stroke-linecap="round" ' +
  'stroke-linejoin="round"><circle cx="12" cy="12" r="10"/>' +
  '<path d="M2 12h20"/>' +
  '<path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>';

/** Build the leading icon element for a path chip. */
function buildPathIcon(path: string): HTMLElement {
  const { base, isDir } = splitPath(path);
  const span = document.createElement('span');
  span.className = 'editor-chip__icon';
  span.setAttribute('aria-hidden', 'true');
  if (isDir) {
    span.classList.add('editor-chip__icon--folder');
    span.innerHTML = FOLDER_SVG;
  } else {
    span.innerHTML = getFileIcon(base).svg;
  }
  return span;
}

/** Build the leading icon element for a URL chip (favicon → globe fallback). */
function buildUrlIcon(href: string): HTMLElement {
  const span = document.createElement('span');
  span.className = 'editor-chip__icon editor-chip__icon--url';
  span.setAttribute('aria-hidden', 'true');

  const { host } = splitUrl(href);
  const favicon = faviconUrl(host);
  if (favicon) {
    const img = document.createElement('img');
    img.src = favicon;
    img.alt = '';
    img.width = 14;
    img.height = 14;
    img.className = 'editor-chip__favicon';
    // Degrade to the globe glyph if the favicon fails (offline / blocked /
    // unknown host) so the chip never shows a broken-image marker.
    img.addEventListener('error', () => {
      span.innerHTML = GLOBE_SVG;
      span.classList.add('editor-chip__icon--globe');
    });
    span.appendChild(img);
  } else {
    span.innerHTML = GLOBE_SVG;
    span.classList.add('editor-chip__icon--globe');
  }
  return span;
}

/** Build the full chip DOM for a node's attrs. */
function buildChipDom(kind: ChipKind, path: string, href: string): HTMLElement {
  const dom = document.createElement(kind === 'url' ? 'a' : 'span');
  dom.className = `editor-chip editor-chip--${kind}`;
  dom.setAttribute('data-type', 'editorChip');
  dom.setAttribute('data-kind', kind);
  dom.setAttribute('contenteditable', 'false');

  const labelSpan = document.createElement('span');
  labelSpan.className = 'editor-chip__label';

  if (kind === 'url') {
    const a = dom as HTMLAnchorElement;
    a.href = href;
    a.target = '_blank';
    a.rel = 'noopener noreferrer';
    a.title = href;
    a.setAttribute('data-href', href);
    a.appendChild(buildUrlIcon(href));
    labelSpan.textContent = truncateUrlLabel(href);
  } else {
    dom.title = path;
    dom.setAttribute('data-path', path);
    dom.appendChild(buildPathIcon(path));
    labelSpan.textContent = truncatePathLabel(path);
  }

  dom.appendChild(labelSpan);
  return dom;
}

/** Raw string a chip serialises to (text / markdown). */
function chipRawText(attrs: { kind?: ChipKind; path?: string | null; href?: string | null }): string {
  if (attrs.kind === 'url') return attrs.href ?? '';
  return attrs.path ?? '';
}

export const ChipNode = Node.create<ChipNodeOptions>({
  name: 'editorChip',
  group: 'inline',
  inline: true,
  atom: true,
  selectable: true,
  // Above plain text so paste rules don't try to re-parse our chip.
  priority: 101,

  addOptions() {
    return {
      enablePaths: true,
      enableUrls: true,
      HTMLAttributes: {},
    };
  },

  addAttributes() {
    return {
      kind: {
        default: 'path',
        parseHTML: (el) => el.getAttribute('data-kind') ?? 'path',
        renderHTML: (attrs) => ({ 'data-kind': (attrs.kind as string) || 'path' }),
      },
      path: {
        default: null,
        parseHTML: (el) => el.getAttribute('data-path'),
        renderHTML: (attrs) => (attrs.path ? { 'data-path': attrs.path as string } : {}),
      },
      href: {
        default: null,
        parseHTML: (el) => el.getAttribute('data-href'),
        renderHTML: (attrs) => (attrs.href ? { 'data-href': attrs.href as string } : {}),
      },
    };
  },

  parseHTML() {
    return [{ tag: 'a[data-type="editorChip"]' }, { tag: 'span[data-type="editorChip"]' }];
  },

  renderHTML({ node, HTMLAttributes }) {
    const kind = (node.attrs.kind as ChipKind) || 'path';
    const tag = kind === 'url' ? 'a' : 'span';
    const extra: Record<string, unknown> = {
      'data-type': 'editorChip',
      class: `editor-chip editor-chip--${kind}`,
    };
    if (kind === 'url' && node.attrs.href) {
      extra.href = node.attrs.href;
      extra.target = '_blank';
      extra.rel = 'noopener noreferrer';
    }
    return [
      tag,
      mergeAttributes(extra, this.options.HTMLAttributes, HTMLAttributes),
      chipRawText(node.attrs as { kind?: ChipKind; path?: string | null; href?: string | null }),
    ];
  },

  // DOM nodeview — renders the icon + middle-ellipsis label and owns the
  // visible text (that's what fixes the long-path wrap).
  addNodeView() {
    return ({ node }) => {
      const kind = (node.attrs.kind as ChipKind) || 'path';
      const dom = buildChipDom(
        kind,
        (node.attrs.path as string | null) ?? '',
        (node.attrs.href as string | null) ?? '',
      );
      return { dom };
    };
  },

  // `editor.getText()` + markdown text fallback read this — the chip
  // flattens to its raw path/href.
  renderText({ node }) {
    return chipRawText(node.attrs as { kind?: ChipKind; path?: string | null; href?: string | null });
  },

  // `@tiptap/markdown` reads this at registration time. Emit the bare raw
  // string (NOT a shortcode), so a round-trip through `getMarkdown()`
  // yields the literal path / URL.
  renderMarkdown(node: JSONContent, _helpers: MarkdownRendererHelpers, _ctx: RenderContext) {
    return chipRawText(node.attrs as { kind?: ChipKind; path?: string | null; href?: string | null });
  },

  addInputRules() {
    const type = this.type;
    const rules: InputRule[] = [];

    // The input rule fires when WHITESPACE is typed right after a path/URL
    // token. We detect on the token BEFORE the space and replace that slice
    // (keeping the space) with a chip node.
    //
    // ── Why we DON'T trust `match` / `range` from TipTap's `find` ──
    //
    // TipTap matches `rule.find` against `getTextContentFromNodes($from)`,
    // which — for an ATOM node like our chip — appends the node's *full*
    // `renderText` output (the raw URL/path string) to the text-before. So
    // once a chip exists, the text-before the cursor is e.g.
    // `http://localhost:6017/x` + whatever the user just typed, glued with
    // NO separator (the chip serialises without a trailing space).
    //
    // That breaks the rule two ways:
    //   1) `/(\S+)(\s)$/` re-matches the chip text fused to the next word
    //      (`http://localhost:6017/xпривет`) — still a valid URL — so the
    //      rule RE-FIRES on every word typed after a chip.
    //   2) `range.from = from - (match[0].length - text.length)` assumes
    //      each char of `match[0]` is one doc position, but the chip is a
    //      single atom position contributing ~20 chars. So `range.from`
    //      lands far to the LEFT of the real token and the replace range
    //      swallows the typed space (the reported `приветкакделаутебя` bug).
    //
    // Fix: ignore `match`/`range` entirely and recompute the token from the
    // REAL document — the contiguous text node that ends at the cursor.
    // That text node starts AFTER any preceding chip (chips are separate
    // sibling nodes), so chip text can never leak into the token.
    //
    // The boundary is WHITESPACE ONLY — deliberately NOT punctuation. Paths
    // and URLs legitimately contain `.` `/` `:` `-` etc., so a punctuation
    // boundary would fire mid-token (e.g. converting `…/Map/index` the
    // instant the `.` of `.ts` is typed). Punctuation-terminated tokens are
    // still handled on paste / `setContent` by the detectors' trailing-punct
    // trim; live typing only chips on a real word boundary.
    const makeRule = (
      detect: (token: string) => { start: number; end: number; attrs: Record<string, unknown> } | null,
    ) =>
      new InputRule({
        find: /(\S+)(\s)$/u,
        handler: ({ range, match, chain, state }) => {
          // The boundary whitespace the user just typed. CRUCIAL: TipTap's
          // `handleTextInput` fires BEFORE the char is inserted, so this
          // boundary is NOT yet in the document — it lives only in `match`.
          // We must therefore re-insert it ourselves below.
          const boundary = match[2] ?? '';
          // `range.to` is the real cursor (insertion point). Unlike `match`
          // it is a genuine doc position untouched by atom-text pollution.
          const cursor = range.to;
          const $cursor = state.doc.resolve(cursor);

          // The text node immediately before the cursor (the run that holds
          // the typed token). If the char before the cursor isn't text —
          // e.g. the cursor sits right after a chip — there's nothing to
          // convert. This text node starts AFTER any preceding chip (chips
          // are separate sibling nodes), so chip text can never leak in.
          const before = $cursor.nodeBefore;
          if (!before || !before.isText || !before.text) return null;

          const textNodeText = before.text;
          const textNodeStart = cursor - textNodeText.length;

          // Take the contiguous non-whitespace run at the END of the text
          // node — that's the token candidate (the boundary char is not in
          // the doc yet, so the node tail IS the token).
          const lastWsIdx = textNodeText.search(/\s\S*$/u);
          const tokenStartInText = lastWsIdx === -1 ? 0 : lastWsIdx + 1;
          const token = textNodeText.slice(tokenStartInText);
          if (!token) return null;

          const found = detect(token);
          if (!found) return null;

          // Map the detector's offsets (relative to `token`) to absolute doc
          // positions.
          const tokenStart = textNodeStart + tokenStartInText;
          const sliceFrom = tokenStart + found.start;
          // Any token chars the detector trimmed off the end (e.g. trailing
          // prose punctuation) stay as text, then the boundary char.
          const tail = token.slice(found.end) + boundary;

          chain()
            // Replace [chip-slice .. cursor) with the chip node followed by
            // the leftover tail + boundary char. Doing both in one
            // `insertContentAt` keeps positions simple: the boundary space is
            // a real text node AFTER the atom, giving the caret a valid
            // landing spot (an atom at the very end of a textblock otherwise
            // traps the caret and swallows subsequently typed spaces).
            .insertContentAt({ from: sliceFrom, to: cursor }, [
              { type: type.name, attrs: found.attrs },
              { type: 'text', text: tail },
            ])
            // Land the caret at the END of the inserted content (after the
            // boundary space) so typing continues as plain text.
            .command(({ tr, dispatch }) => {
              if (dispatch) {
                // chip = 1 pos, then `tail` chars. Caret sits past them.
                const pos = Math.min(sliceFrom + 1 + tail.length, tr.doc.content.size);
                tr.setSelection(TextSelection.create(tr.doc, pos));
              }
              return true;
            })
            .run();
          return;
        },
      });

    if (this.options.enablePaths) {
      rules.push(
        makeRule((token) => {
          const m = findFilePaths(token);
          if (m.length === 0) return null;
          const hit = m[0]!;
          return { start: hit.start, end: hit.end, attrs: { kind: 'path', path: hit.path } };
        }),
      );
    }
    if (this.options.enableUrls) {
      rules.push(
        makeRule((token) => {
          const m = findUrls(token);
          if (m.length === 0) return null;
          const hit = m[0]!;
          return { start: hit.start, end: hit.end, attrs: { kind: 'url', href: hit.href } };
        }),
      );
    }

    return rules;
  },

  addProseMirrorPlugins() {
    const enablePaths = this.options.enablePaths;
    const enableUrls = this.options.enableUrls;
    const type = this.type;

    return [
      new Plugin({
        key: chipPasteKey,
        props: {
          // Paste the TEXT that was copied — with detected paths/URLs turned
          // into chips — never the styling the clipboard carried alongside it.
          //
          // ProseMirror prefers `text/html` over `text/plain`, and a terminal
          // puts colour-span HTML on the clipboard: those spans arrived as real
          // marks, and the HTML branch parses with `preserveWhitespace: false`,
          // collapsing the indentation a `tree` listing is made of.
          //
          // So this owns EVERY plain-text paste, not just one containing a
          // path. Bailing out on "no hits" handed the rest back to the HTML
          // branch, which is the mangling one.
          //
          // Not fixable via `transformPastedHTML`/`clipboardTextParser`:
          // `asText` is decided before either runs, so blanking the HTML there
          // pastes nothing at all.
          handlePaste: (view, event) => {
            const text = event.clipboardData?.getData('text/plain');
            if (!text) return false;
            // Inside a code block PM already pastes verbatim text and a chip
            // would be nonsense there — leave its own handling alone.
            if (view.state.selection.$from.parent.type.spec.code) return false;

            const { schema } = view.state;
            // One paragraph per LINE: a newline cannot live inside a PM text
            // node, so the previous single-slice build flattened a multi-line
            // paste into one run-on line — and a `tree` dump is exactly the
            // text most likely to contain a path.
            const paragraphs = chipPasteLines(text, enablePaths, enableUrls).map(
              (line) =>
                schema.nodes.paragraph!.create(
                  null,
                  line.map((part) =>
                    'chip' in part ? type.create(part.chip) : schema.text(part.text),
                  ),
                ),
            );

            const { from, to } = view.state.selection;
            // A single paragraph stays an INLINE slice (open on both sides) so
            // it merges into the line the caret is on — pasting one path into
            // the middle of a sentence must not split the sentence. Several
            // paragraphs are a block slice, which is what preserves the lines.
            const slice =
              paragraphs.length === 1
                ? new Slice(paragraphs[0]!.content, 0, 0)
                : new Slice(Fragment.fromArray(paragraphs), 1, 1);
            const tr = view.state.tr.replaceRange(from, to, slice);
            view.dispatch(tr.scrollIntoView());
            return true;
          },
        },
      }),
    ];
  },
});

export interface ChipHit {
  start: number;
  end: number;
  attrs: Record<string, unknown>;
}

/**
 * Which spans of a pasted string become chips, in order and non-overlapping.
 *
 * Exported so the paste rule is testable without an editor.
 */
export function chipHits(
  text: string,
  enablePaths: boolean,
  enableUrls: boolean,
): ChipHit[] {
  const hits: ChipHit[] = [];
  if (enablePaths) {
    for (const m of findFilePaths(text)) {
      hits.push({ start: m.start, end: m.end, attrs: { kind: 'path', path: m.path } });
    }
  }
  if (enableUrls) {
    for (const m of findUrls(text)) {
      hits.push({ start: m.start, end: m.end, attrs: { kind: 'url', href: m.href } });
    }
  }
  hits.sort((a, b) => a.start - b.start);
  // Drop overlaps (a path inside a URL etc.) — first wins.
  const merged: ChipHit[] = [];
  let cursor = 0;
  for (const h of hits) {
    if (h.start < cursor) continue;
    merged.push(h);
    cursor = h.end;
  }
  return merged;
}

/**
 * Split a pasted string into lines, with chip spans marked.
 *
 * The shape the paste rule builds nodes from: one entry per LINE, each a list
 * of text runs and chips. Pure, so the line-splitting that a multi-line
 * terminal paste depends on is testable on its own.
 */
export function chipPasteLines(
  text: string,
  enablePaths: boolean,
  enableUrls: boolean,
): Array<Array<{ text: string } | { chip: Record<string, unknown> }>> {
  const merged = chipHits(text, enablePaths, enableUrls);
  const lines: Array<Array<{ text: string } | { chip: Record<string, unknown> }>> = [];
  let line: Array<{ text: string } | { chip: Record<string, unknown> }> = [];
  const pushText = (s: string) => {
    if (!s) return;
    const segments = s.split(/\r\n?|\n/);
    segments.forEach((segment, i) => {
      if (i > 0) {
        lines.push(line);
        line = [];
      }
      if (segment) line.push({ text: segment });
    });
  };
  let last = 0;
  for (const h of merged) {
    pushText(text.slice(last, h.start));
    line.push({ chip: h.attrs });
    last = h.end;
  }
  pushText(text.slice(last));
  lines.push(line);
  return lines;
}

export default ChipNode;
