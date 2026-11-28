import { describe, expect, it } from 'vitest';

import { NAV_GEOMETRY, SHELL_CLASS, SIDEBAR_SPACING } from './geometry';

const SIZES = /\btext-(base|lg|xl|2xl)\b/;

describe('sidebar geometry', () => {
  for (const form of ['desktop', 'mobile'] as const) {
    it(`${form}: rows use 14px text and a 16-20px icon, not a large font`, () => {
      expect(NAV_GEOMETRY[form].item).toMatch(/\btext-(sm|\(length:--sidebar-item-font\))/);
      expect(NAV_GEOMETRY[form].item).not.toMatch(SIZES);
      expect(NAV_GEOMETRY[form].item).toMatch(/\[&>svg\]:size-(4|5)/);
      expect(NAV_GEOMETRY[form].label).toMatch(/\btext-xs\b/);
    });

    it(`${form}: horizontal inset is tight (8px), vertical body padding is roomier`, () => {
      expect(NAV_GEOMETRY[form].inset).toBe('px-2');
      expect(NAV_GEOMETRY[form].item).toMatch(form === 'mobile' ? /\bpx-2\.5\b/ : /\bpx-2\b/);
      expect(SIDEBAR_SPACING[form].body).toMatch(form === 'mobile' ? /\bpy-2\b/ : /\bpy-3\b/);
    });
  }

  it('mobile rows are 40px with a 44px hit area (see touch-safe.css); desktop rows are 36px', () => {
    expect(NAV_GEOMETRY.mobile.item).toMatch(/\bh-10\b/);
    expect(NAV_GEOMETRY.desktop.item).toContain('h-(--sidebar-item-h)');
    // A coarse pointer on a docked sidebar (tablet) still gets a 44px row.
    expect(NAV_GEOMETRY.desktop.item).toContain('pointer-coarse:min-h-11');
  });

  it('mobile header and footer never go under the status bar or home indicator', () => {
    expect(SIDEBAR_SPACING.mobile.header).toContain('env(safe-area-inset-top');
    expect(SIDEBAR_SPACING.mobile.footer).toContain('env(safe-area-inset-bottom');
  });

  it('the shell is one dynamic viewport tall and clips, so the document never scrolls', () => {
    expect(SHELL_CLASS).toContain('h-[var(--app-height,100dvh)]');
    expect(SHELL_CLASS).toContain('overflow-hidden');
    expect(SHELL_CLASS).toContain('min-h-0');
    expect(SHELL_CLASS).not.toMatch(/min-h-(screen|svh)/);
  });

  it('mobile header and footer also respect the side safe areas (landscape notch)', () => {
    expect(SIDEBAR_SPACING.mobile.header).toContain('env(safe-area-inset-left');
    expect(SIDEBAR_SPACING.mobile.footer).toContain('env(safe-area-inset-right');
  });
});
