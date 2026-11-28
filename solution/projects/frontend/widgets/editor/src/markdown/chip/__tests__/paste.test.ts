import { describe, expect, it } from 'vitest';

import { chipPasteLines } from '../ChipNode';

/**
 * Pasting a terminal dump into the composer.
 *
 * Two defects met here. The paste rule flattened every multi-line paste into
 * one paragraph (a newline cannot live inside a ProseMirror text node), and it
 * only claimed pastes that contained a path — handing everything else to
 * ProseMirror's HTML branch, which parses a terminal's colour-span clipboard
 * with `preserveWhitespace: false` and collapses the indentation.
 */

const text = (parts: ReturnType<typeof chipPasteLines>[number]) =>
  parts.map((p) => ('chip' in p ? '<chip>' : p.text)).join('');

describe('chipPasteLines', () => {
  it('keeps a multi-line paste as separate lines', () => {
    const lines = chipPasteLines('first\nsecond\nthird', true, true);
    expect(lines.map(text)).toEqual(['first', 'second', 'third']);
  });

  it('preserves indentation and box-drawing alignment', () => {
    // The reported case: a `tree` listing whose columns collapsed.
    const dump = 'src\n├── index.ts\n└── lib\n    └── util.ts';
    const lines = chipPasteLines(dump, false, false);
    expect(lines.map(text)).toEqual([
      'src',
      '├── index.ts',
      '└── lib',
      '    └── util.ts',
    ]);
  });

  it('keeps tabs and runs of spaces exactly', () => {
    const lines = chipPasteLines('a\t\tb   c', false, false);
    expect(text(lines[0]!)).toBe('a\t\tb   c');
  });

  it('keeps a blank line as a blank line', () => {
    const lines = chipPasteLines('one\n\ntwo', false, false);
    expect(lines.map(text)).toEqual(['one', '', 'two']);
  });

  it('normalises CRLF without losing the break', () => {
    const lines = chipPasteLines('one\r\ntwo\rthree', false, false);
    expect(lines.map(text)).toEqual(['one', 'two', 'three']);
  });

  it('handles a paste with no chips at all', () => {
    // This used to return false and fall through to the HTML branch — the
    // mangling path. It must produce lines like any other paste.
    const lines = chipPasteLines('just some prose\nover two lines', false, false);
    expect(lines.map(text)).toEqual(['just some prose', 'over two lines']);
  });

  it('marks a path inside its own line, not across lines', () => {
    // Absolute only — `findFilePaths` deliberately ignores bare relative paths.
    const lines = chipPasteLines('see /src/index.ts\nand more', true, false);
    expect(lines).toHaveLength(2);
    expect(lines[0]!.some((p) => 'chip' in p)).toBe(true);
    expect(lines[1]!.some((p) => 'chip' in p)).toBe(false);
    expect(text(lines[0]!)).toBe('see <chip>');
  });

  it('keeps text on both sides of a chip', () => {
    const lines = chipPasteLines('open /src/index.ts now', true, false);
    expect(text(lines[0]!)).toBe('open <chip> now');
  });

  it('emits no chips when both detectors are off', () => {
    const lines = chipPasteLines('see /src/index.ts and https://x.com', false, false);
    expect(lines[0]!.every((p) => 'text' in p)).toBe(true);
  });

  it('a single line stays a single line', () => {
    expect(chipPasteLines('one line', false, false)).toHaveLength(1);
  });

  it('does not drop a trailing newline into a lost line', () => {
    const lines = chipPasteLines('one\n', false, false);
    expect(lines.map(text)).toEqual(['one', '']);
  });
});
