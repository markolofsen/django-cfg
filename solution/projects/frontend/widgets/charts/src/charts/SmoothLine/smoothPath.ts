// smoothPath — turn a polyline of points into a flowing SMOOTH curve.
//
// The straight-segment builders (`M x,y L x,y L x,y …`) draw the line as a
// jagged polyline: every data point is a sharp angle. This converts the same
// points into a MONOTONE-CUBIC spline (Fritsch–Carlson, == d3's curveMonotoneX)
// emitted as cubic-bezier segments (`M x,y C c1 c2 p …`), so the line flows in
// gentle curves through every point instead of kinking at each one.
//
// Why monotone-cubic and NOT Catmull-Rom (the previous curve):
//   Catmull-Rom makes pretty curves but "often produces inappropriate OVERSHOOTS
//   even for monotone data points" — it can shoot above a local max or below a
//   local min, i.e. it WOBBLES between points and invents values the data never
//   had. On a streaming chart those overshoots MOVE as the trailing control
//   points change, adding shimmer on top of the scroll. Monotone-cubic
//   (Fritsch–Carlson) guarantees "no overshoots beyond the given data points" —
//   the interpolant stays within the data's own bounds, so the curve can never
//   wobble or overshoot. It is the standard choice for data charts precisely
//   because it doesn't fabricate between-point values. See
//   en.wikipedia.org/wiki/Monotone_cubic_interpolation and d3-shape
//   `curveMonotoneX`.
//
// The algorithm (2-pass Fritsch–Carlson):
//   pass 1 — secant slopes between consecutive points, then a 3-point tangent at
//            each interior point (the Catmull-Rom-ish average);
//   pass 2 — clamp each tangent so it cannot exceed 3× the adjacent secant,
//            which is exactly what enforces monotonicity (kills overshoot).
//   The bezier control handles are then placed one third of the x-gap along each
//   point's tangent — the standard Hermite→bezier conversion.
//
// Pure geometry: this is NOT animation. The streaming engine scrolls the whole
// `<g>`; this builds the curve once per data change from the true points.
// `tension` still exists for API compat (and `0` is the SHARP disable path), but
// it no longer scales overshoot — monotone tangents need no tension knob.

/** A point in viewBox space. */
export interface Pt {
  x: number;
  y: number;
}

/**
 * Default smoothing tension. Retained for API compatibility — any value > 0
 * selects the monotone-cubic curve (which has no tension parameter of its own);
 * `0` degenerates to straight `L` segments for charts that need sharp corners
 * (ECG QRS spikes, which keep their own bespoke builder rather than this one).
 */
export const DEFAULT_TENSION = 0.5;

/**
 * Build a smooth `d` path through `points` using monotone-cubic → cubic bezier.
 *
 * @param points  anchor points, in draw order. The curve passes through each.
 * @param tension `0` → straight (`L`) segments; any value > 0 → monotone curve.
 * @param _bounds viewBox extent (kept for signature compat; monotone-cubic does
 *                not overshoot, so no clamp is needed).
 * @returns the full `M…`-prefixed path. For the BODY only (no leading `M`), use
 *          {@link smoothSegments}.
 */
export function smoothLinePath(
  points: readonly Pt[],
  tension: number,
  _bounds?: { width: number; height: number },
): string {
  const first = points[0];
  if (first === undefined) return '';
  const head = `${first.x.toFixed(2)},${first.y.toFixed(2)}`;
  if (points.length === 1) return `M${head}`;
  return `M${head} ${smoothSegments(points, tension)}`;
}

/**
 * The curve BODY (no leading `M`) — the `C …`/`L …` segments that connect the
 * points. Split out so the area builder can reuse the exact same curve between
 * its own `M0,baseline` open and `L…baseline Z` close (the fill must hug the
 * same flowing line as the stroke, not a straight re-trace).
 *
 * @param tension `0` → straight `L` segments (disable path); > 0 → monotone.
 * @param _bounds ignored (monotone-cubic does not overshoot) — kept for compat.
 */
export function smoothSegments(
  points: readonly Pt[],
  tension: number,
  _bounds?: { width: number; height: number },
): string {
  if (points.length < 2) return '';

  // tension <= 0 → straight polyline (the disable path; SHARP geometry).
  if (tension <= 0) {
    return points
      .slice(1)
      .map((p) => `L${p.x.toFixed(2)},${p.y.toFixed(2)}`)
      .join(' ');
  }

  const m = monotoneTangents(points);
  const out: string[] = [];

  for (let i = 0; i < points.length - 1; i += 1) {
    const p1 = points[i];
    const p2 = points[i + 1];
    // `m` is built from `points`, so it is the same length; all three reads are
    // in range for every `i` in this loop.
    const m1 = m[i];
    const m2 = m[i + 1];
    if (p1 === undefined || p2 === undefined || m1 === undefined || m2 === undefined) continue;
    const dx = (p2.x - p1.x) / 3;
    // Hermite → cubic bezier: handles sit one third of the x-gap along each
    // endpoint's tangent. Monotone tangents guarantee no overshoot, so no clamp.
    const c1x = p1.x + dx;
    const c1y = p1.y + dx * m1;
    const c2x = p2.x - dx;
    const c2y = p2.y - dx * m2;
    out.push(
      `C${c1x.toFixed(2)},${c1y.toFixed(2)} ${c2x.toFixed(2)},${c2y.toFixed(2)} ${p2.x.toFixed(2)},${p2.y.toFixed(2)}`,
    );
  }

  return out.join(' ');
}

/**
 * Trace a monotone-cubic curve through `points` onto a Canvas2D context using the
 * SAME Fritsch–Carlson tangents as {@link smoothSegments} — the canvas analogue
 * of emitting the `C …`/`L …` body, via `bezierCurveTo`/`lineTo`. The caller owns
 * `beginPath()` and the opening `moveTo` (so the area filler can open at the
 * baseline and close after); this only appends the curve through the points.
 *
 * @param tension `0` → straight `lineTo` segments (the SHARP disable path); any
 *                value > 0 → the monotone curve.
 */
export function traceSmoothSegments(
  ctx: CanvasRenderingContext2D,
  points: readonly Pt[],
  tension: number,
): void {
  if (points.length < 2) return;

  // tension <= 0 → straight polyline (the disable path; SHARP geometry).
  if (tension <= 0) {
    for (let i = 1; i < points.length; i += 1) {
      const p = points[i];
      if (p === undefined) continue;
      ctx.lineTo(p.x, p.y);
    }
    return;
  }

  const m = monotoneTangents(points);
  for (let i = 0; i < points.length - 1; i += 1) {
    const p1 = points[i];
    const p2 = points[i + 1];
    // `m` is built from `points`, so it is the same length; all three reads are
    // in range for every `i` in this loop.
    const m1 = m[i];
    const m2 = m[i + 1];
    if (p1 === undefined || p2 === undefined || m1 === undefined || m2 === undefined) continue;
    const dx = (p2.x - p1.x) / 3;
    // Hermite → cubic bezier: handles sit one third of the x-gap along each
    // endpoint's tangent. Monotone tangents guarantee no overshoot, so no clamp.
    ctx.bezierCurveTo(p1.x + dx, p1.y + dx * m1, p2.x - dx, p2.y - dx * m2, p2.x, p2.y);
  }
}

/**
 * Fritsch–Carlson monotone tangents (the slope dy/dx at each point). Two passes:
 * a 3-point initial tangent, then a clamp that enforces monotonicity so the
 * resulting cubic cannot overshoot the data between points. Mirrors d3-shape's
 * `curveMonotoneX`.
 */
function monotoneTangents(points: readonly Pt[]): number[] {
  const n = points.length;
  const tangents = new Array<number>(n).fill(0);
  if (n < 2) return tangents;

  // Secant slopes between consecutive points.
  const secants = new Array<number>(n - 1);
  for (let i = 0; i < n - 1; i += 1) {
    const a = points[i];
    const b = points[i + 1];
    if (a === undefined || b === undefined) continue;
    const dx = b.x - a.x;
    secants[i] = dx === 0 ? 0 : (b.y - a.y) / dx;
  }

  // Pass 1 — endpoint tangents = adjacent secant; interior = average of the two
  // neighbouring secants (the 3-point tangent). `secants` has n - 1 >= 1 entries,
  // so indices 0 and n - 2 both exist.
  tangents[0] = secants[0] ?? 0;
  tangents[n - 1] = secants[n - 2] ?? 0;
  for (let i = 1; i < n - 1; i += 1) {
    const prev = secants[i - 1];
    const cur = secants[i];
    if (prev === undefined || cur === undefined) continue;
    tangents[i] = (prev + cur) / 2;
  }

  // Pass 2 — clamp tangents to enforce monotonicity (Fritsch–Carlson). Where a
  // secant is flat, pin both surrounding tangents to 0 (a local extreme stays
  // flat). Otherwise scale the tangent so (α, β) lie in the monotone circle of
  // radius 3, which is what kills overshoot.
  for (let i = 0; i < n - 1; i += 1) {
    const s = secants[i];
    if (s === undefined) continue;
    if (s === 0) {
      tangents[i] = 0;
      tangents[i + 1] = 0;
      continue;
    }
    // `tangents` has n entries and i + 1 <= n - 1 here.
    const t1 = tangents[i];
    const t2 = tangents[i + 1];
    if (t1 === undefined || t2 === undefined) continue;
    const a = t1 / s;
    const b = t2 / s;
    // If a tangent points the "wrong" way relative to the secant, flatten it.
    if (a < 0) tangents[i] = 0;
    if (b < 0) tangents[i + 1] = 0;
    const h = a * a + b * b;
    if (h > 9) {
      const t = 3 / Math.sqrt(h);
      tangents[i] = t * a * s;
      tangents[i + 1] = t * b * s;
    }
  }

  return tangents;
}
