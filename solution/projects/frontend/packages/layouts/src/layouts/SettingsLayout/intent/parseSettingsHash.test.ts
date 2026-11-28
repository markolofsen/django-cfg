import { describe, expect, it } from 'vitest';

import { buildSettingsHash, carriesIntent, parseSettingsHash, sectionToOpen } from './parseSettingsHash';

describe('parseSettingsHash', () => {
  it('is closed for an empty or foreign fragment', () => {
    expect(parseSettingsHash('', 'settings').open).toBe(false);
    expect(parseSettingsHash('profile/mcp', 'settings').open).toBe(false);
  });

  it('opens on the bare key with no section', () => {
    expect(parseSettingsHash('settings', 'settings')).toEqual({ open: true, section: null, params: {} });
  });

  it('reads the section before the query, not the query as part of it', () => {
    expect(parseSettingsHash('settings/mcp?request=abc&client=Claude', 'settings')).toEqual({
      open: true,
      section: 'mcp',
      params: { request: 'abc', client: 'Claude' },
    });
  });

  it('decodes values and keeps a section-less query', () => {
    expect(parseSettingsHash('settings?request=a%2Bb', 'settings').params).toEqual({ request: 'a+b' });
  });

  it('drops an over-long value and caps the number of params', () => {
    const long = 'x'.repeat(5000);
    expect(parseSettingsHash(`settings/mcp?request=${long}&ok=1`, 'settings').params).toEqual({ ok: '1' });
    const many = Array.from({ length: 20 }, (_, i) => `p${i}=1`).join('&');
    expect(Object.keys(parseSettingsHash(`settings/mcp?${many}`, 'settings').params)).toHaveLength(8);
  });
});

describe('buildSettingsHash', () => {
  it('never carries params', () => {
    expect(buildSettingsHash('settings', 'mcp')).toBe('settings/mcp');
    expect(buildSettingsHash('settings', null)).toBe('settings');
  });
});

describe('sectionToOpen', () => {
  it('uses the host-resolved id when there is one', () => {
    expect(sectionToOpen('mcp', 'mcp')).toBe('mcp');
  });

  it('keeps the requested id while the section is not registered yet (cold deep link)', () => {
    expect(sectionToOpen('mcp', null)).toBe('mcp');
  });

  it('is null for a bare #settings', () => {
    expect(sectionToOpen(null, null)).toBeNull();
  });
});

describe('carriesIntent', () => {
  it('is true only for a settings link with a query', () => {
    expect(carriesIntent('settings/mcp?request=abc&client=Claude', 'settings')).toBe(true);
    expect(carriesIntent('settings/mcp', 'settings')).toBe(false);
    expect(carriesIntent('settings', 'settings')).toBe(false);
    expect(carriesIntent('other/mcp?request=abc', 'settings')).toBe(false);
    expect(carriesIntent('', 'settings')).toBe(false);
  });
});
