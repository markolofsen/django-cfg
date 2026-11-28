import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { describe, expect, it } from 'vitest';

const here = dirname(fileURLToPath(import.meta.url));
const read = (rel: string) => readFileSync(join(here, rel), 'utf8');

/**
 * Overlay primitives take their safe-area and height from the shared tokens (`--safe-*`, `--app-height`,
 * defined in styles/css/base.css) instead of each inventing `100vh` / bare `env()` handling.
 */
describe('overlay primitives read the PWA tokens', () => {
  const files = ['drawer/index.tsx', 'sheet/index.tsx', 'dialog/index.tsx', '../feedback/sonner/index.tsx'];

  for (const f of files) {
    it(`${f} has no raw 100vh and no bare env(safe-area-*)`, () => {
      const src = read(f).replace(/\/\*[\s\S]*?\*\/|\/\/.*$/gm, '');
      expect(src).not.toMatch(/100vh/);
      // env() is only allowed as the fallback inside a --safe-* token read.
      for (const m of src.matchAll(/env\(safe-area[^)]*\)/g)) {
        const before = src.slice(Math.max(0, m.index! - 14), m.index!);
        expect(before).toMatch(/--safe-\w+,$/);
      }
    });
  }

  it('side drawers and sheets are pinned with inset-y-0 and h-auto, not h-full', () => {
    // (snap-point drawers keep h-full on purpose: vaul translates a full-height panel.)
    expect(read('drawer/index.tsx')).toMatch(/left: "inset-y-0 left-0 h-auto border-r"/);
    expect(read('sheet/index.tsx')).not.toMatch(/inset-y-0 (left|right)-0 h-full/);
  });

  it('they use the tokens', () => {
    expect(read('drawer/index.tsx')).toContain('--app-height');
    expect(read('drawer/index.tsx')).toContain('--safe-bottom');
    expect(read('sheet/index.tsx')).toContain('--safe-top');
    expect(read('dialog/index.tsx')).toContain('--safe-top');
    expect(read('../feedback/sonner/index.tsx')).toContain('--safe-bottom');
  });
});
