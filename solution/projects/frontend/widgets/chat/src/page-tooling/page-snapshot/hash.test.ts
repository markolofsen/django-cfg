import { describe, expect, it } from 'vitest';

import { serializeCST } from './cst/serialize';
import type { CSTRootNode } from './cst/types';
import { hashSnapshot } from './hash';

const sampleRoot: CSTRootNode = {
  type: 'root',
  title: 'Billing Settings',
  url: 'https://app.example.com/settings/billing',
  children: [{ type: 'text', content: 'Configure your subscription.' }],
};

describe('hashSnapshot', () => {
  it('is stable for identical input', () => {
    const s = serializeCST(sampleRoot);
    expect(hashSnapshot(s)).toBe(hashSnapshot(s));
  });

  it('changes when the snapshot changes', () => {
    const a = hashSnapshot(serializeCST(sampleRoot));
    const mutated: CSTRootNode = { ...sampleRoot, title: 'Other Page' };
    const b = hashSnapshot(serializeCST(mutated));
    expect(a).not.toBe(b);
  });

  it('returns an 8-char hex string', () => {
    expect(hashSnapshot('anything')).toMatch(/^[0-9a-f]{8}$/);
  });

  it('handles an empty string', () => {
    expect(hashSnapshot('')).toMatch(/^[0-9a-f]{8}$/);
  });
});
