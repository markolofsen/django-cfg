import React from 'react';
import { describe, expect, it } from 'vitest';

import { extractTextFromChildren, hasMarkdownSyntax, looksLikePlainProse } from './plainText';

/**
 * `looksLikePlainProse` picks which renderer a chat bubble gets. A false
 * POSITIVE is the expensive direction: prose-mode escapes nothing, so a
 * message the detector wrongly calls plain shows its `**` and `#` to the
 * reader as literal characters. The module's own comment commits to erring
 * markdown-ward, and these assertions are what keeps that promise honest.
 *
 * `extractTextFromChildren` is what the `<pre>` renderer uses to pull code out
 * of a highlighted tree for copy-to-clipboard; if it drops a branch, users copy
 * a truncated snippet and never notice until it fails to run.
 */

describe('looksLikePlainProse', () => {
  it('accepts a short one-line message', () => {
    expect(looksLikePlainProse('hey, are you around?')).toBe(true);
  });

  it('accepts empty and whitespace-only content', () => {
    expect(looksLikePlainProse('')).toBe(true);
    expect(looksLikePlainProse('   \n  ')).toBe(true);
  });

  it('rejects anything over 500 characters', () => {
    expect(looksLikePlainProse('a'.repeat(500))).toBe(true);
    expect(looksLikePlainProse('a'.repeat(501))).toBe(false);
  });

  it('rejects a paragraph break', () => {
    expect(looksLikePlainProse('one\n\ntwo')).toBe(false);
  });

  it('rejects more than four single line breaks', () => {
    expect(looksLikePlainProse('a\nb\nc\nd\ne')).toBe(false);
  });

  it('rejects any markdown marker', () => {
    expect(looksLikePlainProse('**bold**')).toBe(false);
    expect(looksLikePlainProse('# heading')).toBe(false);
  });

  it('rejects a single-newline message, because hasMarkdownSyntax treats a newline as markdown', () => {
    // Below the 4-newline cap, but `hasMarkdownSyntax` short-circuits on any
    // newline after trim — so two-line messages go through the markdown path.
    expect(looksLikePlainProse('line one\nline two')).toBe(false);
  });
});

describe('hasMarkdownSyntax', () => {
  it('treats any interior newline as markdown territory', () => {
    expect(hasMarkdownSyntax('a\nb')).toBe(true);
  });

  it('ignores leading and trailing newlines', () => {
    expect(hasMarkdownSyntax('\n hello \n')).toBe(false);
  });

  it('detects inline HTML, which the plain path would show as literal brackets', () => {
    expect(hasMarkdownSyntax('use <br> here')).toBe(true);
    expect(hasMarkdownSyntax('a <b>bold</b> word')).toBe(true);
    expect(hasMarkdownSyntax('self <img src="x"/> closing')).toBe(true);
  });

  it('does not read a bare comparison as an HTML tag', () => {
    expect(hasMarkdownSyntax('if a < b and c > d')).toBe(false);
  });

  it('detects headers, emphasis, links, code and lists', () => {
    expect(hasMarkdownSyntax('# h')).toBe(true);
    expect(hasMarkdownSyntax('**b**')).toBe(true);
    expect(hasMarkdownSyntax('*i*')).toBe(true);
    expect(hasMarkdownSyntax('__b__')).toBe(true);
    expect(hasMarkdownSyntax('_i_')).toBe(true);
    expect(hasMarkdownSyntax('[a](b)')).toBe(true);
    expect(hasMarkdownSyntax('![a](b)')).toBe(true);
    expect(hasMarkdownSyntax('`x`')).toBe(true);
    expect(hasMarkdownSyntax('- item')).toBe(true);
    expect(hasMarkdownSyntax('1. item')).toBe(true);
    expect(hasMarkdownSyntax('> quote')).toBe(true);
    expect(hasMarkdownSyntax('| a | b |')).toBe(true);
    expect(hasMarkdownSyntax('~~s~~')).toBe(true);
  });

  it('returns false for ordinary prose', () => {
    expect(hasMarkdownSyntax('just a normal sentence.')).toBe(false);
    expect(hasMarkdownSyntax('')).toBe(false);
  });

  it('flags a snake_case identifier as markdown — a known false positive', () => {
    // The `_i_` italic pattern matches `foo_bar_baz`. Harmless by design:
    // the markdown path renders the word correctly either way, and the
    // module's comment says false positives only cost a render. Asserted so
    // a "fix" that tightens this into a false NEGATIVE has to argue for it.
    expect(hasMarkdownSyntax('call foo_bar_baz now')).toBe(true);
  });
});

describe('extractTextFromChildren', () => {
  it('returns a string as-is and stringifies a number', () => {
    expect(extractTextFromChildren('hi')).toBe('hi');
    expect(extractTextFromChildren(42)).toBe('42');
  });

  it('joins an array with no separator, so copied code keeps its exact spacing', () => {
    expect(extractTextFromChildren(['a', 'b', 'c'])).toBe('abc');
  });

  it('descends through element children', () => {
    const tree = React.createElement('span', null, 'a', React.createElement('em', null, 'b'));
    expect(extractTextFromChildren(tree)).toBe('ab');
  });

  it('descends through arbitrarily nested elements', () => {
    const tree = React.createElement(
      'div',
      null,
      React.createElement('span', null, React.createElement('code', null, 'deep')),
      '!',
    );
    expect(extractTextFromChildren(tree)).toBe('deep!');
  });

  it('yields empty string for the nodes that carry no text', () => {
    expect(extractTextFromChildren(null)).toBe('');
    expect(extractTextFromChildren(undefined)).toBe('');
    expect(extractTextFromChildren(true)).toBe('');
    expect(extractTextFromChildren(false)).toBe('');
  });

  it('yields empty string for an element with no children', () => {
    expect(extractTextFromChildren(React.createElement('br'))).toBe('');
  });

  it('does not drop a zero, which is falsy but is real text', () => {
    expect(extractTextFromChildren(0)).toBe('0');
  });
});
