import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, it } from 'vitest';

import { PrettyCode, type PrettyCodeProps } from './pretty-code';

/**
 * Static markup, no DOM: the questions are "what did it draw" and "did it
 * throw". The component is mounted by a chat once per token, so the second one
 * is the property that matters.
 */
const render = (props: Partial<PrettyCodeProps> & Pick<PrettyCodeProps, 'data'>) =>
  renderToStaticMarkup(<PrettyCode language="ts" {...props} />);

describe('a fence', () => {
  it('draws the source with Prism tokens, a language label and a copy button', () => {
    const html = render({ data: 'const x: number = 1;' });

    expect(html).toContain('data-slot="pretty-code"');
    expect(html).toContain('TypeScript');
    expect(html).toContain('aria-label="Copy code"');
    expect(html).toContain('class="token');
    expect(html).toContain('color:');
  });

  it('wraps rather than scrolls sideways', () => {
    expect(render({ data: 'x'.repeat(400) })).toContain('white-space:pre-wrap');
  });

  it('is compact on request: 12px type', () => {
    expect(render({ data: 'a', isCompact: true })).toContain('font-size:12px');
    expect(render({ data: 'a' })).toContain('font-size:14px');
  });

  it('takes its words from the host when it passes them', () => {
    const html = render({ data: 'a', labels: { copyCode: 'Скопировать' } });

    expect(html).toContain('aria-label="Скопировать"');
  });

  it('scrolls only past maxLines, and then as a keyboard-reachable region', () => {
    const lines = Array.from({ length: 30 }, (_, i) => `line ${i}`).join('\n');

    expect(render({ data: lines, maxLines: 10 })).toContain('role="region"');
    expect(render({ data: lines, maxLines: 100 })).not.toContain('role="region"');
  });

  it('stringifies an object', () => {
    expect(render({ data: { a: 1 }, language: 'json' })).toContain('JSON');
  });
});

describe('half-arrived input does not throw', () => {
  const cases: ReadonlyArray<readonly [string, Partial<PrettyCodeProps> & Pick<PrettyCodeProps, 'data'>]> = [
    ['an empty body while the fence is open', { data: '', pending: true }],
    ['an empty body that is final', { data: '' }],
    ['a line cut mid-token', { data: 'const s = "unterminated' }],
    ['an unknown language', { data: 'nuqneH', language: 'klingon' }],
    ['no language', { data: 'plain', language: '' }],
    ['a cyclic object', { data: (() => { const o: Record<string, unknown> = {}; o.self = o; return o; })() }],
    ['an inline chip', { data: 'x', inline: true }],
    ['the plain variant', { data: 'x', variant: 'plain' }],
  ];

  for (const [name, props] of cases) {
    it(`survives ${name}`, () => {
      expect(() => render(props)).not.toThrow();
    });
  }

  it('shows no "no content" line for a block that has not started', () => {
    const html = render({ data: '', pending: true });

    expect(html).toContain('data-slot="pretty-code"');
    expect(html).not.toContain('No content available');
  });

  it('says so for a block that is empty and final', () => {
    expect(render({ data: '' })).toContain('No content available');
  });
});

describe('weight', () => {
  it('tokenizes a 5 000-line block well inside a frame budget per token', () => {
    const data = Array.from({ length: 5000 }, (_, i) => `const value${i}: number = compute(${i}, "x");`).join('\n');
    const start = performance.now();
    const html = render({ data, isCompact: true });
    const ms = performance.now() - start;

    expect(html.length).toBeGreaterThan(data.length);
    // Generous on purpose (a loaded CI box): the number is recorded in the decision, this only catches an order of magnitude.
    expect(ms).toBeLessThan(2000);
  });
});
