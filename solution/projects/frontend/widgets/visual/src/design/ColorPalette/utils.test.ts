import { describe, expect, it } from 'vitest';

import { formatColor, getReadableContrast } from './utils';

/**
 * `getReadableContrast` decides whether a swatch gets black or white label
 * text. Get it backwards on a given colour and the label vanishes into its own
 * background — an accessibility failure that only shows up on the specific
 * palette entry that tripped it.
 *
 * `formatColor` writes the string people copy out of the picker into their own
 * code, so a wrong channel order or a dropped `%` is a colour that silently
 * differs from the one they clicked.
 */

describe('formatColor — hex', () => {
  it('lowercases, so copied values are consistent regardless of input casing', () => {
    expect(formatColor('#AABBCC', 'hex')).toBe('#aabbcc');
  });

  it('does not attempt to parse in hex mode, returning even a malformed value as-is', () => {
    expect(formatColor('not-a-color', 'hex')).toBe('not-a-color');
  });
});

describe('formatColor — rgb', () => {
  it('converts a 6-digit hex, keeping the r/g/b order', () => {
    expect(formatColor('#ff8000', 'rgb')).toBe('rgb(255, 128, 0)');
  });

  it('expands a 3-digit shorthand by doubling each nibble', () => {
    // `#abc` is `#aabbcc`, not `#a0b0c0`. Getting this wrong shifts every
    // shorthand colour in the palette.
    expect(formatColor('#abc', 'rgb')).toBe('rgb(170, 187, 204)');
    expect(formatColor('#fff', 'rgb')).toBe('rgb(255, 255, 255)');
    expect(formatColor('#000', 'rgb')).toBe('rgb(0, 0, 0)');
  });

  it('accepts a hex with no leading # and with surrounding whitespace', () => {
    expect(formatColor('ff8000', 'rgb')).toBe('rgb(255, 128, 0)');
    expect(formatColor('  #ff8000  ', 'rgb')).toBe('rgb(255, 128, 0)');
  });

  it('falls back to the original string when the hex is unparseable', () => {
    // The swatch keeps showing something rather than "rgb(NaN, NaN, NaN)".
    expect(formatColor('#gg0000', 'rgb')).toBe('#gg0000');
    expect(formatColor('#ff00', 'rgb')).toBe('#ff00');
    expect(formatColor('', 'rgb')).toBe('');
  });
});

describe('formatColor — hsl', () => {
  it('reports a greyscale colour as zero saturation with no hue', () => {
    expect(formatColor('#808080', 'hsl')).toBe('hsl(0, 0%, 50%)');
    expect(formatColor('#000000', 'hsl')).toBe('hsl(0, 0%, 0%)');
    expect(formatColor('#ffffff', 'hsl')).toBe('hsl(0, 0%, 100%)');
  });

  it('puts the primaries on their standard hue angles', () => {
    // 0 / 120 / 240 are the definition. A drift here means the hue wheel
    // in the picker no longer matches the value it reports.
    expect(formatColor('#ff0000', 'hsl')).toBe('hsl(0, 100%, 50%)');
    expect(formatColor('#00ff00', 'hsl')).toBe('hsl(120, 100%, 50%)');
    expect(formatColor('#0000ff', 'hsl')).toBe('hsl(240, 100%, 50%)');
  });

  it('wraps a magenta-side hue into 0–360 rather than emitting a negative', () => {
    // The red branch adds 6 when g < b precisely to avoid a negative hue.
    // `hsl(-60, …)` is not what a user wants pasted into their stylesheet.
    expect(formatColor('#ff00ff', 'hsl')).toBe('hsl(300, 100%, 50%)');
  });

  it('emits units on saturation and lightness but not on hue', () => {
    expect(formatColor('#3366cc', 'hsl')).toMatch(/^hsl\(\d+, \d+%, \d+%\)$/);
  });

  it('falls back to the original string when the hex is unparseable', () => {
    expect(formatColor('#zzz', 'hsl')).toBe('#zzz');
  });
});

describe('getReadableContrast', () => {
  it('calls white light and black dark', () => {
    expect(getReadableContrast('#ffffff')).toBe('light');
    expect(getReadableContrast('#000000')).toBe('dark');
  });

  it('picks by contrast, not by which channel is lit', () => {
    // The old implementation asked "is this bright enough" against a fixed
    // number, so all three saturated primaries came out the same. They are
    // not: red reads better in black (5.25:1 vs 4.00:1) and blue in white
    // (8.59:1 vs 2.44:1). Asserting the ratio's winner is the contract; the
    // luminance formula behind it is not.
    expect(getReadableContrast('#ff0000')).toBe('light');
    expect(getReadableContrast('#0000ff')).toBe('dark');
  });

  it('weights green above red above blue, as human vision does', () => {
    // Cyan (green+blue) reaches 16.75:1 against black; magenta (red+blue)
    // 6.70:1 — both black, but the gap is the weighting. A naive
    // (r+g+b)/3 average would score the two identically.
    expect(getReadableContrast('#00ffff')).toBe('light');
    expect(getReadableContrast('#ffff00')).toBe('light');
    expect(getReadableContrast('#0000ff')).toBe('dark');
  });

  it('has no cliff at #999999, where the old threshold put one', () => {
    // 0.6 × 255 = 153 = 0x99, so the old `> 0.6` test made this exact grey and
    // its immediate neighbour disagree. Both are 7.4:1 against black and under
    // 2.9:1 against white — there is no boundary here at all.
    expect(getReadableContrast('#999999')).toBe('light');
    expect(getReadableContrast('#9a9a9a')).toBe('light');
  });

  it('gives pure green black text, not white', () => {
    // Regression, accessibility. The function used to test Rec. 601 luminance
    // against a hard-coded `> 0.6`. #00ff00 scores 0.587 — just under — so the
    // swatch was labelled in WHITE at a contrast of 1.37:1, where black gives
    // 15.30:1. AA wants 4.5:1 for body text, so the label was effectively
    // invisible on a bright green swatch.
    //
    // It now compares the two real contrast ratios instead of guessing where
    // the crossover sits.
    expect(getReadableContrast('#00ff00')).toBe('light');
  });

  it('gives a mid grey black text, which the old threshold also got wrong', () => {
    // #999999: 7.37:1 against black, 2.85:1 against white.
    expect(getReadableContrast('#999999')).toBe('light');
  });

  it('still gives a saturated blue white text', () => {
    // The fix must not simply flip everything: #0000ff is 8.59:1 white vs
    // 2.44:1 black.
    expect(getReadableContrast('#0000ff')).toBe('dark');
  });

  it('accepts a 3-digit shorthand', () => {
    expect(getReadableContrast('#fff')).toBe('light');
    expect(getReadableContrast('#000')).toBe('dark');
  });

  it('defaults to dark for an unparseable colour', () => {
    // Dark means white text, which is the safer guess against the unknown
    // surface a broken value is likely to render as.
    expect(getReadableContrast('nonsense')).toBe('dark');
    expect(getReadableContrast('')).toBe('dark');
  });
});
