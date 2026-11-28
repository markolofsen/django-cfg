import { describe, expect, it } from 'vitest';

import { DEFAULT_TENSION, smoothLinePath, smoothSegments, type Pt } from './smoothPath';

/**
 * The whole reason this module replaced Catmull-Rom is the monotonicity
 * guarantee: the curve must never leave the range of the data it passes
 * through. A chart that overshoots is not ugly — it draws a value that was
 * never measured, and on a streaming chart the invented peak moves as the
 * trailing points change.
 *
 * So the assertions that matter are the INVARIANTS (passes through every
 * point; flat data stays flat; no control handle escapes the local y-range),
 * not the exact coordinate strings, which are an implementation detail of the
 * Hermite→bezier conversion.
 */

/** Pull every coordinate pair out of a `d` string. */
function coords(d: string): Pt[] {
  const out: Pt[] = [];
  for (const m of d.matchAll(/(-?\d+\.\d+),(-?\d+\.\d+)/g)) {
    const x = Number(m[1]);
    const y = Number(m[2]);
    out.push({ x, y });
  }
  return out;
}

describe('smoothLinePath — degenerate series', () => {
  it('returns an empty string for no points, so the <path> renders nothing', () => {
    // Not `'M'` or `'MNaN,NaN'` — an invalid `d` makes the browser log and
    // drop the path, which looks the same as a data outage.
    expect(smoothLinePath([], DEFAULT_TENSION)).toBe('');
  });

  it('emits a bare moveto for a single point', () => {
    expect(smoothLinePath([{ x: 1, y: 2 }], DEFAULT_TENSION)).toBe('M1.00,2.00');
  });

  it('joins two points with one cubic segment', () => {
    const d = smoothLinePath([{ x: 0, y: 0 }, { x: 10, y: 10 }], DEFAULT_TENSION);
    expect(d.startsWith('M0.00,0.00 ')).toBe(true);
    expect((d.match(/C/g) ?? []).length).toBe(1);
  });
});

describe('smoothSegments — the curve body', () => {
  it('is empty for fewer than two points, so the area builder has nothing to close over', () => {
    expect(smoothSegments([], DEFAULT_TENSION)).toBe('');
    expect(smoothSegments([{ x: 0, y: 0 }], DEFAULT_TENSION)).toBe('');
  });

  it('emits one C segment per gap', () => {
    const pts: Pt[] = [{ x: 0, y: 0 }, { x: 1, y: 5 }, { x: 2, y: 2 }, { x: 3, y: 8 }];
    expect((smoothSegments(pts, DEFAULT_TENSION).match(/C/g) ?? []).length).toBe(pts.length - 1);
  });

  it('carries no leading M, so it can be spliced between a caller\'s own open and close', () => {
    expect(smoothSegments([{ x: 0, y: 0 }, { x: 1, y: 1 }], DEFAULT_TENSION).startsWith('M')).toBe(false);
  });
});

describe('tension 0 — the sharp disable path', () => {
  const pts: Pt[] = [{ x: 0, y: 0 }, { x: 1, y: 5 }, { x: 2, y: 2 }];

  it('emits straight L segments and no curves', () => {
    const d = smoothSegments(pts, 0);
    expect(d).toBe('L1.00,5.00 L2.00,2.00');
    expect(d).not.toContain('C');
  });

  it('treats a negative tension as sharp too', () => {
    expect(smoothSegments(pts, -1)).not.toContain('C');
  });

  it('skips the first point, which the caller already emitted as the moveto', () => {
    expect(smoothLinePath(pts, 0)).toBe('M0.00,0.00 L1.00,5.00 L2.00,2.00');
  });
});

describe('the curve passes through every data point', () => {
  it('ends each cubic segment exactly on the next anchor', () => {
    // A monotone spline is an interpolant, not an approximation. If an
    // endpoint drifts, the line no longer touches the dot the chart draws.
    const pts: Pt[] = [{ x: 0, y: 10 }, { x: 10, y: 40 }, { x: 20, y: 5 }, { x: 30, y: 25 }];
    const d = smoothSegments(pts, DEFAULT_TENSION);
    const segments = d.split('C').slice(1);
    expect(segments).toHaveLength(3);
    segments.forEach((seg, i) => {
      const endpoint = coords(`C${seg}`).at(-1);
      const anchor = pts[i + 1];
      expect(endpoint?.x).toBeCloseTo(anchor?.x ?? NaN, 2);
      expect(endpoint?.y).toBeCloseTo(anchor?.y ?? NaN, 2);
    });
  });
});

describe('monotonicity — the guarantee this curve was chosen for', () => {
  it('keeps a flat series perfectly flat', () => {
    // Every secant is 0, so every tangent is pinned to 0 and no control
    // handle may leave the line. A wobble here is a visible fake trend.
    const pts: Pt[] = [{ x: 0, y: 50 }, { x: 10, y: 50 }, { x: 20, y: 50 }, { x: 30, y: 50 }];
    for (const p of coords(smoothSegments(pts, DEFAULT_TENSION))) {
      expect(p.y).toBeCloseTo(50, 2);
    }
  });

  it('flattens the tangent at a local maximum, so the peak is not overshot', () => {
    // Up then down: the middle point is a local max. Monotone tangents pin
    // it flat, so no control handle may rise above it.
    const pts: Pt[] = [{ x: 0, y: 0 }, { x: 10, y: 100 }, { x: 20, y: 0 }];
    // y grows downward in SVG, but the invariant is symmetric: no emitted
    // coordinate may exceed the data's own y-range.
    for (const p of coords(smoothSegments(pts, DEFAULT_TENSION))) {
      expect(p.y).toBeGreaterThanOrEqual(0);
      expect(p.y).toBeLessThanOrEqual(100);
    }
  });

  it('never leaves the data\'s y-range on a spiky series', () => {
    const pts: Pt[] = [
      { x: 0, y: 20 }, { x: 10, y: 80 }, { x: 20, y: 15 },
      { x: 30, y: 95 }, { x: 40, y: 40 }, { x: 50, y: 60 },
    ];
    const ys = pts.map((p) => p.y);
    const min = Math.min(...ys);
    const max = Math.max(...ys);
    for (const p of coords(smoothSegments(pts, DEFAULT_TENSION))) {
      expect(p.y).toBeGreaterThanOrEqual(min);
      expect(p.y).toBeLessThanOrEqual(max);
    }
  });

  it('keeps each segment\'s control handles inside that segment\'s own y-range', () => {
    // This is the monotonicity guarantee stated per-segment, which is where it
    // actually bites: a cubic whose handles stay between its two endpoints
    // cannot bulge past either of them. Checked segment-by-segment because a
    // flat list of emitted coordinates interleaves handles with endpoints and
    // is not itself expected to be sorted.
    const pts: Pt[] = [{ x: 0, y: 0 }, { x: 10, y: 1 }, { x: 20, y: 30 }, { x: 30, y: 100 }];
    const segments = smoothSegments(pts, DEFAULT_TENSION).split('C').slice(1);
    expect(segments).toHaveLength(pts.length - 1);
    segments.forEach((seg, i) => {
      const a = pts[i];
      const b = pts[i + 1];
      if (a === undefined || b === undefined) return;
      const lo = Math.min(a.y, b.y);
      const hi = Math.max(a.y, b.y);
      for (const p of coords(`C${seg}`)) {
        expect(p.y).toBeGreaterThanOrEqual(lo - 1e-6);
        expect(p.y).toBeLessThanOrEqual(hi + 1e-6);
      }
    });
  });
});

describe('numeric robustness', () => {
  it('emits no NaN when consecutive points share an x (a zero-width gap)', () => {
    // Streaming data can deliver two samples on the same timestamp. A NaN in
    // `d` silently blanks the whole line.
    const d = smoothSegments([{ x: 0, y: 0 }, { x: 0, y: 10 }, { x: 10, y: 20 }], DEFAULT_TENSION);
    expect(d).not.toContain('NaN');
  });

  it('emits two-decimal fixed coordinates, keeping the d string short and stable', () => {
    const d = smoothLinePath([{ x: 1 / 3, y: 2 / 3 }, { x: 1, y: 1 }], DEFAULT_TENSION);
    expect(d.startsWith('M0.33,0.67')).toBe(true);
    expect(d).not.toContain('NaN');
  });

  it('ignores the bounds argument, which is retained only for signature compat', () => {
    const pts: Pt[] = [{ x: 0, y: 0 }, { x: 10, y: 10 }];
    expect(smoothSegments(pts, DEFAULT_TENSION, { width: 1, height: 1 }))
      .toBe(smoothSegments(pts, DEFAULT_TENSION));
  });
});

describe('DEFAULT_TENSION', () => {
  it('is a positive value, so the default render is curved not sharp', () => {
    expect(DEFAULT_TENSION).toBeGreaterThan(0);
  });

  it('produces the same curve as any other positive tension, since monotone has no knob', () => {
    // Documented API-compat behaviour: tension no longer scales anything.
    // Asserted so a change that quietly re-introduces a tension term fails.
    const pts: Pt[] = [{ x: 0, y: 0 }, { x: 10, y: 30 }, { x: 20, y: 10 }];
    expect(smoothSegments(pts, 0.9)).toBe(smoothSegments(pts, DEFAULT_TENSION));
  });
});
