/**
 * `syncChips` — convert detected file-path / URL text in the document into
 * `editorChip` atom nodes. The analogue of `syncLeadingSlashNode` for the
 * chip node.
 *
 * Input/paste rules cover live typing + paste, but content arriving via
 * `setContent(markdown)` (the controlled `value` sync) is parsed straight
 * to plain text — a bare path or URL in the initial `value` would render
 * un-chipped without this pass. We scan every text node, run the pure
 * detectors, and replace each match range with a chip, walking
 * right-to-left within each text node so earlier offsets stay valid.
 *
 * Returns `true` when at least one replacement happened (callers may
 * suppress a feedback `onUpdate`).
 */
import type { Editor } from '@tiptap/react';
import { findFilePaths } from '../filePath/detect';
import { findUrls } from '../url/detect';

interface ChipOpts {
  paths: boolean;
  urls: boolean;
}

interface PendingHit {
  /** Absolute doc start. */
  from: number;
  /** Absolute doc end. */
  to: number;
  attrs: Record<string, unknown>;
}

export function syncChips(editor: Editor, opts: ChipOpts): boolean {
  if (!editor || editor.isDestroyed) return false;
  if (!opts.paths && !opts.urls) return false;
  const chipType = editor.schema.nodes.editorChip;
  if (!chipType) return false;

  const hits: PendingHit[] = [];

  editor.state.doc.descendants((node, pos) => {
    if (!node.isText || !node.text) return;
    const text = node.text;

    const local: { start: number; end: number; attrs: Record<string, unknown> }[] = [];
    if (opts.paths) {
      for (const m of findFilePaths(text)) {
        local.push({ start: m.start, end: m.end, attrs: { kind: 'path', path: m.path } });
      }
    }
    if (opts.urls) {
      for (const m of findUrls(text)) {
        local.push({ start: m.start, end: m.end, attrs: { kind: 'url', href: m.href } });
      }
    }
    if (local.length === 0) return;

    // Drop overlaps (e.g. a path shape inside a URL path) — earliest start
    // wins, longest at equal start.
    local.sort((a, b) => a.start - b.start || b.end - a.end);
    let cursor = 0;
    for (const h of local) {
      if (h.start < cursor) continue;
      hits.push({ from: pos + h.start, to: pos + h.end, attrs: h.attrs });
      cursor = h.end;
    }
  });

  if (hits.length === 0) return false;

  // Apply right-to-left so each replacement doesn't shift the positions of
  // the ones still pending.
  hits.sort((a, b) => b.from - a.from);
  let tr = editor.state.tr;
  for (const h of hits) {
    tr = tr.replaceWith(h.from, h.to, chipType.create(h.attrs));
  }
  editor.view.dispatch(tr);
  return true;
}
