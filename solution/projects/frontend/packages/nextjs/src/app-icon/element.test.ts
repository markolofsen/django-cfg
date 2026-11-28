import assert from 'node:assert/strict';
import { describe, it } from 'node:test';

import type { ReactElement } from 'react';

import { appIconElement, appIconGradient, oklchToHex } from './element';

const GOLDEN = '#3f93f7';

type Tile = ReactElement<{ style: Record<string, unknown>; children: ReactElement<{ width: number }> }>;

describe('app-icon', () => {
  it('converts oklch to a stable hex (golden)', () => {
    assert.equal(oklchToHex(0.66, 0.17, 255), GOLDEN);
    assert.equal(oklchToHex(1, 0, 0), '#ffffff');
  });

  it('builds the gradient from two hex stops', () => {
    assert.match(appIconGradient(55), /^linear-gradient\(150deg, #[0-9a-f]{6}, #[0-9a-f]{6}\)$/);
  });

  it('draws a full-bleed tile with no border and a smaller glyph on a square', () => {
    const rounded = appIconElement({ glyph: [['path', { key: 'a', d: 'M0 0' }]], hue: 55, size: 100 }) as Tile;
    const square = appIconElement({ glyph: [['path', { key: 'a', d: 'M0 0' }]], hue: 55, size: 100, shape: 'square' }) as Tile;
    assert.equal(rounded.props.style.border, undefined);
    assert.equal(rounded.props.style.borderRadius, 23);
    assert.equal(square.props.style.borderRadius, 0);
    assert.equal(rounded.props.children.props.width, 58);
    assert.equal(square.props.children.props.width, 46);
  });

  it('refuses a glyph that is not a lucide module', () => {
    assert.throws(() => appIconElement({ glyph: {}, hue: 0, size: 10 }), /lucide/);
  });
});
