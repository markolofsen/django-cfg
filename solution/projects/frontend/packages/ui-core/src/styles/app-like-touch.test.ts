import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { describe, expect, it } from 'vitest';

const css = readFileSync(join(dirname(fileURLToPath(import.meta.url)), 'css/base.css'), 'utf8');

describe('base.css app-like touch rules', () => {
  it('disables double-tap zoom everywhere without blocking pinch', () => {
    expect(css).toMatch(/html\s*{[^}]*touch-action:\s*manipulation/);
    expect(css).toMatch(/text-size-adjust:\s*100%/);
    expect(css).not.toMatch(/touch-action:\s*(none|pan-)/);
  });

  it('floors text fields at 16px on touch devices only', () => {
    const block = css.slice(css.indexOf('@media (pointer: coarse)'));
    expect(block).toMatch(/font-size:\s*max\(16px, 1em\)/);
    expect(block).toContain('.input-compact');
  });

  it('shell rules apply only in installed display modes', () => {
    const rules = css.slice(css.indexOf('Installed app'));
    expect(rules).toContain('overscroll-behavior: none');
    expect(rules).toContain('-webkit-touch-callout: none');
    for (const mode of ['standalone', 'fullscreen', 'minimal-ui', 'window-controls-overlay']) {
      expect(rules).toContain(`[data-display-mode="${mode}"]`);
    }
    expect(rules).toMatch(/\.selectable/);
  });

  it('keeps overscroll-behavior out of the global scope', () => {
    const before = css.slice(0, css.indexOf('Installed app'));
    expect(before).not.toContain('overscroll-behavior');
  });
});
