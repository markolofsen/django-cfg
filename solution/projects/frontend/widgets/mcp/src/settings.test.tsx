import { isValidElement } from 'react';
import { describe, expect, it } from 'vitest';

import { mcpSettingsSection } from './settings';

describe('mcpSettingsSection', () => {
  it('is a Platform-group section with a fixed id and label', () => {
    const section = mcpSettingsSection();
    expect(section).toMatchObject({ id: 'mcp', label: 'MCP', title: 'MCP', group: 'platform' });
    expect(section.keywords).toContain('claude');
  });

  it('approves an assistant request above the list when the address brought one', () => {
    const { content } = mcpSettingsSection();
    expect(typeof content).toBe('function');
    if (typeof content !== 'function') return;
    const names = (node: unknown): string => JSON.stringify(node, (_k, v) => (typeof v === 'function' ? v.name : v));
    const plain = content({ intent: null });
    const asked = content({ intent: { params: { request: 'signed' }, clear: () => {} } });
    expect(isValidElement(plain) && isValidElement(asked)).toBe(true);
    expect(names(plain)).not.toContain('McpApproval');
    expect(names(asked)).toContain('McpApproval');
    expect(names(asked)).toContain('McpConnect');
  });
});
