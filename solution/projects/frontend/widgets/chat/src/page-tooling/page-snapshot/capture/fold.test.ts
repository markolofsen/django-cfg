import { describe, expect, it } from 'vitest';

import { foldSiblings } from './fold';
import type { CSTNode } from '../cst/types';

/** Build N identically-shaped interactive rows. */
function rows(n: number, role: 'button' = 'button'): CSTNode[] {
  return Array.from({ length: n }, (_, i) => ({
    type: 'container' as const,
    role: 'section' as const,
    children: [
      { type: 'interactive' as const, role, ref: `@e${i + 1}` as const, name: `Row ${i}` },
    ],
  }));
}

describe('foldSiblings', () => {
  it('does not fold short chains (< 5)', () => {
    const { children, foldedCount } = foldSiblings(rows(4));
    expect(foldedCount).toBe(0);
    expect(children).toHaveLength(4);
  });

  it('folds a long chain of identical siblings', () => {
    const { children, foldedCount } = foldSiblings(rows(100));
    expect(foldedCount).toBe(1);
    // 3 kept + 1 collapse marker.
    expect(children).toHaveLength(4);
    expect(children[3]).toEqual({
      type: 'text',
      content: '[… 97 more similar items collapsed]',
    });
  });

  it('keeps the first 3 instances', () => {
    const { children } = foldSiblings(rows(20));
    expect(children.slice(0, 3).every((n) => n.type === 'container')).toBe(true);
  });

  it('does not fold structurally different siblings', () => {
    const mixed: CSTNode[] = [
      { type: 'interactive', role: 'button', ref: '@e1', name: 'A' },
      { type: 'interactive', role: 'textbox', ref: '@e2', name: 'B' },
      { type: 'interactive', role: 'checkbox', ref: '@e3', name: 'C' },
      { type: 'interactive', role: 'link', ref: '@e4', name: 'D' },
      { type: 'interactive', role: 'select', ref: '@e5', name: 'E' },
      { type: 'interactive', role: 'tab', ref: '@e6', name: 'F' },
    ];
    const { foldedCount, children } = foldSiblings(mixed);
    expect(foldedCount).toBe(0);
    expect(children).toHaveLength(6);
  });

  it('folds nested repetitive lists too', () => {
    const table: CSTNode[] = [
      { type: 'container', role: 'table', children: rows(50) },
    ];
    const { children, foldedCount } = foldSiblings(table);
    expect(foldedCount).toBe(1);
    const tableNode = children[0];
    expect(tableNode?.type).toBe('container');
    if (tableNode?.type === 'container') {
      expect(tableNode.children).toHaveLength(4); // 3 + marker
    }
  });
});
