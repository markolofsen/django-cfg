let counter = 0;

/**
 * Cheap monotonic id — collisions are fine across sessions, we just need
 * uniqueness within one component lifecycle. Avoids pulling in nanoid for
 * a tool that already keeps the lazy chunk small.
 */
export function newSegmentId(): string {
  counter = (counter + 1) % Number.MAX_SAFE_INTEGER;
  return `seg_${Date.now().toString(36)}_${counter.toString(36)}`;
}
