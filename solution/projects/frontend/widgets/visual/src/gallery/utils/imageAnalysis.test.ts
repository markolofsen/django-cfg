import { describe, expect, it } from 'vitest';

import { analyzeImage, analyzeImages, getAspectRatio, getOrientation } from './imageAnalysis';
import type { GalleryMediaItem } from '../types';

/**
 * The gallery reserves each tile's box from these two numbers before the image
 * itself loads. Get them wrong and the grid reflows as images arrive — layout
 * shift, which is both the worst-looking failure mode a gallery has and a
 * measured CWV regression.
 *
 * The defaults matter as much as the maths: dimensions are optional on a
 * `GalleryMediaItem`, so most real items hit the fallback path.
 */

const item = (over: Partial<GalleryMediaItem>): GalleryMediaItem => ({
  id: '1',
  src: '/a.png',
  ...over,
});

describe('getOrientation', () => {
  it('calls a wide image landscape', () => {
    expect(getOrientation(1920, 1080)).toBe('landscape');
  });

  it('calls a tall image portrait', () => {
    expect(getOrientation(1080, 1920)).toBe('portrait');
  });

  it('calls a 1:1 image square', () => {
    expect(getOrientation(500, 500)).toBe('square');
  });

  it('treats near-square as square via a deadband, not as a knife edge', () => {
    // Ratios between 0.8 and 1.2 inclusive are square. Without the deadband a
    // 1000x999 photo would be tagged landscape and get the wrong tile.
    expect(getOrientation(1000, 999)).toBe('square');
    expect(getOrientation(999, 1000)).toBe('square');
    expect(getOrientation(120, 100)).toBe('square');
    expect(getOrientation(80, 100)).toBe('square');
  });

  it('uses a strict comparison at each deadband edge', () => {
    // ratio exactly 1.2 / 0.8 stays square; a hair past flips.
    expect(getOrientation(1200, 1000)).toBe('square');
    expect(getOrientation(1201, 1000)).toBe('landscape');
    expect(getOrientation(800, 1000)).toBe('square');
    expect(getOrientation(799, 1000)).toBe('portrait');
  });

  it('defaults to landscape when either dimension is missing', () => {
    // Documented assumption — most gallery content is landscape, so this is
    // the cheapest guess to be wrong about.
    expect(getOrientation(undefined, undefined)).toBe('landscape');
    expect(getOrientation(1000, undefined)).toBe('landscape');
    expect(getOrientation(undefined, 1000)).toBe('landscape');
  });

  it('treats a zero dimension as missing rather than dividing by it', () => {
    // `0` is falsy, so it takes the default branch. Without that, `w/0` is
    // Infinity and every zero-height item would be tagged landscape anyway —
    // but a zero WIDTH would give ratio 0 and be tagged portrait. Asserted so
    // both stay on the documented default.
    expect(getOrientation(0, 1000)).toBe('landscape');
    expect(getOrientation(1000, 0)).toBe('landscape');
  });
});

describe('getAspectRatio', () => {
  it('is width over height', () => {
    expect(getAspectRatio(1920, 1080)).toBeCloseTo(16 / 9, 10);
    expect(getAspectRatio(1080, 1920)).toBeCloseTo(9 / 16, 10);
    expect(getAspectRatio(500, 500)).toBe(1);
  });

  it('defaults to 16/9 when either dimension is missing', () => {
    expect(getAspectRatio(undefined, undefined)).toBeCloseTo(16 / 9, 10);
    expect(getAspectRatio(1000, undefined)).toBeCloseTo(16 / 9, 10);
    expect(getAspectRatio(undefined, 1000)).toBeCloseTo(16 / 9, 10);
  });

  it('never returns Infinity or 0 for a zero dimension', () => {
    // Either would make the reserved box collapse or blow up the layout.
    expect(getAspectRatio(1000, 0)).toBeCloseTo(16 / 9, 10);
    expect(getAspectRatio(0, 1000)).toBeCloseTo(16 / 9, 10);
    expect(Number.isFinite(getAspectRatio(1000, 0))).toBe(true);
  });
});

describe('analyzeImage', () => {
  it('adds the two derived fields without dropping any of the original', () => {
    const source = item({ id: 'x', src: '/x.png', alt: 'x', width: 200, height: 100, thumbnail: '/t.png' });
    expect(analyzeImage(source)).toEqual({
      ...source,
      orientation: 'landscape',
      aspectRatio: 2,
    });
  });

  it('does not mutate the item it was given', () => {
    // The gallery holds the caller's array; mutating it would leak derived
    // fields back into whatever state the host owns.
    const source = item({ width: 200, height: 100 });
    analyzeImage(source);
    expect(source).not.toHaveProperty('orientation');
    expect(source).not.toHaveProperty('aspectRatio');
  });

  it('applies the defaults for an item with no dimensions', () => {
    const out = analyzeImage(item({}));
    expect(out.orientation).toBe('landscape');
    expect(out.aspectRatio).toBeCloseTo(16 / 9, 10);
  });
});

describe('analyzeImages', () => {
  it('preserves order and length', () => {
    const out = analyzeImages([
      item({ id: 'a', width: 200, height: 100 }),
      item({ id: 'b', width: 100, height: 200 }),
      item({ id: 'c' }),
    ]);
    expect(out.map((i) => i.id)).toEqual(['a', 'b', 'c']);
    expect(out.map((i) => i.orientation)).toEqual(['landscape', 'portrait', 'landscape']);
  });

  it('returns an empty array for an empty input', () => {
    expect(analyzeImages([])).toEqual([]);
  });
});
