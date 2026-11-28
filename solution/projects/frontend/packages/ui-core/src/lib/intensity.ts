// Adapted from jalcoui (MIT) — github.com/jal-co/ui
//
// Quantize a numeric value into a discrete intensity bucket. Used by
// heatmaps (activity-graph), gauges, and any thermal-style visualization
// that needs N colored steps.
//
// `thresholds` are upper bounds in ascending order, expressed as fractions
// of `max` or as absolute values — caller picks. The returned bucket index
// is in `[0, thresholds.length]`.
//
// Inspired by `getIntensity` at activity-graph.tsx:72-80.

/**
 * @param value      Current value.
 * @param thresholds Ascending upper bounds. The returned bucket is the
 *                   index of the first threshold `value` does not exceed,
 *                   or `thresholds.length` if it exceeds them all.
 * @returns Bucket index in `[0, thresholds.length]`. `0` for non-positive
 *          values (treated as "empty").
 *
 * @example
 *   getIntensity(0, [0.25, 0.5, 0.75])     // 0  (empty)
 *   getIntensity(0.1, [0.25, 0.5, 0.75])   // 1
 *   getIntensity(0.5, [0.25, 0.5, 0.75])   // 2
 *   getIntensity(0.8, [0.25, 0.5, 0.75])   // 3
 *   getIntensity(1.0, [0.25, 0.5, 0.75])   // 3
 *
 * @example
 *   // Quantize commits/day into 4 buckets relative to the busiest day:
 *   const max = Math.max(...counts);
 *   const ratio = count / max;
 *   const step = getIntensity(ratio, [0.25, 0.5, 0.75]); // 0..3
 */
export function getIntensity(value: number, thresholds: number[]): number {
  if (!(value > 0)) return 0;
  for (let i = 0; i < thresholds.length; i++) {
    const threshold = thresholds[i];
    if (threshold !== undefined && value <= threshold) return i + 1;
  }
  return thresholds.length;
}
