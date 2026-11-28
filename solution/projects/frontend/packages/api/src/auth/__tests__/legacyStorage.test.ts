// @vitest-environment jsdom
import { beforeEach, describe, expect, it } from 'vitest';

import { purgeLegacyTokenStorage } from '../hooks/legacyStorage';

describe('purgeLegacyTokenStorage', () => {
  beforeEach(() => localStorage.clear());

  it('removes the pre-cookie token entries and keeps everything else', () => {
    localStorage.setItem('cfg.auth.access_token', 'a');
    localStorage.setItem('cfg.auth.refresh_token', 'r');
    localStorage.setItem('cfg.ui.sidebar_width', '240');
    expect(purgeLegacyTokenStorage().sort()).toEqual(['cfg.auth.access_token', 'cfg.auth.refresh_token']);
    expect(localStorage.getItem('cfg.ui.sidebar_width')).toBe('240');
    expect(localStorage.getItem('cfg.auth.access_token')).toBeNull();
  });

  it('does nothing when there is nothing to remove', () => {
    expect(purgeLegacyTokenStorage()).toEqual([]);
  });
});
