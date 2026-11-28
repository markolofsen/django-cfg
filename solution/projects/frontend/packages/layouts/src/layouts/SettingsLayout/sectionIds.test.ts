import { describe, expect, it } from 'vitest';

import { parseSettingsHash } from './intent/parseSettingsHash';
import { MCP_SECTION_ID, defineSettingsSections, settingsHref } from './sectionIds';

describe('settingsHref', () => {
  it('spells the fragment the dialog reads', () => {
    expect(settingsHref('mcp')).toBe('#settings/mcp');
    expect(settingsHref('api-keys')).toBe('#settings/api-keys');
  });

  it('follows a custom urlKey', () => {
    expect(settingsHref('mcp', 'prefs')).toBe('#prefs/mcp');
  });

  it('round-trips through the parser', () => {
    const fragment = settingsHref('billing').slice(1);
    expect(parseSettingsHash(fragment, 'settings')).toMatchObject({ open: true, section: 'billing' });
  });
});

describe('defineSettingsSections', () => {
  it('returns the very array it was given', () => {
    const list = [{ id: 'billing', label: 'Billing', content: null }];
    expect(defineSettingsSections(list)).toBe(list);
  });

  it('MCP_SECTION_ID is the id the MCP widget uses', () => {
    expect(MCP_SECTION_ID).toBe('mcp');
  });
});
