// @vitest-environment jsdom

import { describe, expect, it } from 'vitest';

import { renderDiagram } from './render';

/**
 * The diagram SVG is inserted with `dangerouslySetInnerHTML`, and its source is
 * written by a model. That makes "the parser never emits model text as markup"
 * a security claim, and a claim of that kind is worth a gate rather than a
 * comment — an upstream change could turn a label into markup and nothing else
 * here would notice.
 *
 * The parser escapes labels into `data-*` attributes, so these payloads survive
 * as TEXT. What is asserted is the property that matters: after a real DOM
 * parse, no element carries an event handler and no script or img exists.
 */

const PAYLOADS: ReadonlyArray<readonly [string, string]> = [
  ['a script tag', 'graph TD\n  A["<script>alert(1)</script>"] --> B[ok]'],
  ['an img onerror', 'graph TD\n  A["<img src=x onerror=alert(1)>"] --> B[ok]'],
  ['an svg onload', 'graph TD\n  A["<svg onload=alert(1)>"] --> B[ok]'],
  ['a quote break', 'graph TD\n  A["\\" onload=\\"alert(1)"] --> B[ok]'],
];

function dangerousNodes(svg: string): string[] {
  const host = document.createElement('div');
  host.innerHTML = svg;
  return [...host.querySelectorAll('*')]
    .filter(
      (node) =>
        [...node.attributes].some((attribute) => /^on/i.test(attribute.name)) ||
        node.tagName.toLowerCase() === 'script' ||
        node.tagName.toLowerCase() === 'img',
    )
    .map((node) => node.tagName);
}

describe('a diagram cannot smuggle markup out of a label', () => {
  it.each(PAYLOADS)('renders %s inert', (_name, source) => {
    const result = renderDiagram(source);

    expect(result.ok).toBe(true);
    if (result.ok) expect(dangerousNodes(result.svg)).toEqual([]);
  });

  it('detects a live payload, so the assertions above mean something', () => {
    // Without this control every case above passes just as well against a
    // detector that can see nothing at all.
    expect(dangerousNodes('<svg><img src=x onerror="alert(1)"></svg>')).toEqual(['IMG']);
  });
});
