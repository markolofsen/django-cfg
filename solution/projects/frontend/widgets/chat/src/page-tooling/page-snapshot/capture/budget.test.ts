import { describe, expect, it } from 'vitest';

import { enforceBudget } from './budget';
import type { CSTNode } from '../cst/types';

describe('enforceBudget', () => {
  it('leaves a small snapshot untouched', () => {
    const children: CSTNode[] = [
      { type: 'text', content: 'short' },
      { type: 'interactive', role: 'button', ref: '@e1', name: 'Go' },
    ];
    const result = enforceBudget(children, 8_000);
    expect(result.degradation).toBe('none');
    expect(result.children).toEqual(children);
  });

  it('truncates long text when over budget', () => {
    const children: CSTNode[] = [
      { type: 'text', content: 'x'.repeat(5_000) },
    ];
    const result = enforceBudget(children, 100);
    expect(result.degradation).toBe('truncated');
    const text = result.children[0];
    expect(text?.type).toBe('text');
    if (text?.type === 'text') {
      expect(text.content).toContain('(truncated)');
      expect(text.content.length).toBeLessThan(200);
    }
  });

  it('falls back to interactive-only when truncation is not enough', () => {
    // Many text nodes — truncation alone still over a tiny budget.
    const children: CSTNode[] = Array.from({ length: 200 }, (_, i) => ({
      type: 'text' as const,
      content: `paragraph ${i} `.repeat(20),
    }));
    children.push({
      type: 'interactive',
      role: 'button',
      ref: '@e1',
      name: 'Submit',
    });
    const result = enforceBudget(children, 50);
    expect(result.degradation).toBe('interactive-only');
    // Only the interactive node survives.
    expect(result.children.every((n) => n.type === 'interactive')).toBe(true);
    expect(result.children).toHaveLength(1);
  });
});
