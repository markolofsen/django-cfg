import { describe, expect, it } from 'vitest';

import { escapeQuoted, formatLabel, sanitizeLabel, toNodeId } from './sanitize';

/**
 * These builders write Mermaid SOURCE, so a label that escapes its own syntax
 * does not throw — it produces a different diagram, or a parse error a long
 * way from the call that caused it. That is what these hold.
 */

describe('sanitizeLabel', () => {
  it('drops the characters that would close a node or a line', () => {
    expect(sanitizeLabel('a"b')).toBe('ab');
    expect(sanitizeLabel('a<b>c')).toBe('abc');
    expect(sanitizeLabel('a{b}c')).toBe('abc');
    expect(sanitizeLabel('a|b')).toBe('ab');
    expect(sanitizeLabel('a\\b')).toBe('ab');
    expect(sanitizeLabel('a\nb')).toBe('ab');
  });

  it('encodes the ampersand, which mermaid reads as a node separator', () => {
    expect(sanitizeLabel('R&D')).toBe('R&amp;D');
  });

  it('leaves an apostrophe alone', () => {
    // The implementation replaces `'` with `'` — a no-op kept because the
    // character is safe. Asserted so a "fix" that starts stripping it fails.
    expect(sanitizeLabel("it's")).toBe("it's");
  });

  it('trims, so a label pasted with padding does not shift the layout', () => {
    expect(sanitizeLabel('  hello  ')).toBe('hello');
  });
});

describe('toNodeId', () => {
  it('collapses anything that is not an identifier character', () => {
    expect(toNodeId('my node!')).toBe('my_node_');
    expect(toNodeId('a-b.c')).toBe('a_b_c');
  });

  it('prefixes an id that does not start with a letter', () => {
    // A bare `1` is not a valid mermaid id, and the diagram fails to parse
    // rather than drawing the node wrong.
    expect(toNodeId('1st')).toBe('n1st');
    expect(toNodeId('_x')).toBe('n_x');
  });

  it('escapes a reserved word, case-insensitively', () => {
    // `end` closes a subgraph. A node called `end` truncates the diagram at
    // that line and everything after it silently disappears.
    expect(toNodeId('end')).toBe('end_');
    expect(toNodeId('End')).toBe('End_');
    expect(toNodeId('graph')).toBe('graph_');
    expect(toNodeId('classDef')).toBe('classDef_');
  });

  it('applies the prefix after sanitising, not before', () => {
    expect(toNodeId('end', 'svc')).toBe('svc_end_');
  });
});

describe('escapeQuoted', () => {
  it('escapes the quote and the backslash, in that order', () => {
    // Backslash first, or the escape it adds gets escaped again.
    expect(escapeQuoted('a\\b')).toBe('a\\\\b');
    expect(escapeQuoted('say "hi"')).toBe('say \\"hi\\"');
  });

  it('turns a newline into a break rather than dropping it', () => {
    // Unlike `sanitizeLabel`: inside quotes the line can be kept.
    expect(escapeQuoted('a\nb')).toBe('a<br/>b');
  });
});

describe('formatLabel', () => {
  it('is the plain label with no subtitle', () => {
    expect(formatLabel('Deploy')).toBe('Deploy');
  });

  it('adds the markup AFTER sanitising, which is the only reason it survives', () => {
    // `sanitizeLabel` strips `<` and `>`, so composing in the other order
    // would erase the tags and print the subtitle inline.
    expect(formatLabel('Deploy', 'to prod')).toBe('Deploy<br/><small>to prod</small>');
  });

  it('sanitises both halves', () => {
    expect(formatLabel('a"b', 'c|d')).toBe('ab<br/><small>cd</small>');
  });
});
