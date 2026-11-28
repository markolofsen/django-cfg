import { describe, expect, it } from 'vitest';

import { serializeCST } from './serialize';
import type { CSTRootNode } from './types';

const sampleRoot: CSTRootNode = {
  type: 'root',
  title: 'Billing Settings',
  url: 'https://app.example.com/settings/billing',
  children: [
    {
      type: 'container',
      role: 'form',
      name: 'Billing',
      children: [
        {
          type: 'interactive',
          role: 'textbox',
          ref: '@e1',
          name: 'Company',
          value: 'Acme',
        },
        { type: 'text', content: 'Configure your subscription.' },
      ],
    },
  ],
};

describe('serializeCST', () => {
  it('produces a deterministic string for the same tree', () => {
    expect(serializeCST(sampleRoot)).toBe(serializeCST(sampleRoot));
  });

  it('drops undefined optional fields', () => {
    const json = serializeCST(sampleRoot);
    // The textbox has no `placeholder` — it must not appear.
    expect(json).not.toContain('placeholder');
    expect(json).toContain('"ref":"@e1"');
  });

  it('emits keys in a fixed order regardless of input key order', () => {
    const reordered: CSTRootNode = {
      children: sampleRoot.children,
      url: sampleRoot.url,
      type: 'root',
      title: sampleRoot.title,
    };
    expect(serializeCST(reordered)).toBe(serializeCST(sampleRoot));
  });
});
