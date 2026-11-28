/**
 * Turning a seed into a stable choice.
 *
 * Pure and vendor-free on purpose: this is the half that decides WHICH drawing a
 * seed gets, and it has to be assertable without rendering anything. The drawing
 * library is swappable; this arithmetic is the product's contract.
 */

/**
 * FNV-1a, 32-bit.
 *
 * Chosen over the shorter `hash * 31 + c` this package used for the blink phase
 * because that one is weak in its low bits, and a corpus index is exactly
 * `hash % length` — a small length reads only those bits, so short seeds that
 * differ late would collide into one style. FNV mixes every byte through the
 * whole word.
 *
 * Iterates over UTF-16 code units rather than code points: two seeds that differ
 * only in astral-plane characters still differ here, because their surrogate
 * pairs do. Nothing needs the stronger property, and code-unit iteration is what
 * makes this identical across every engine.
 */
export function hashSeed(seed: string): number {
  let hash = 0x811c9dc5;
  for (let i = 0; i < seed.length; i += 1) {
    hash ^= seed.charCodeAt(i);
    // The FNV prime, as shifts: a plain `hash * 16777619` exceeds 2^53 and
    // loses the low bits to float rounding, which is the one thing this
    // function must not do.
    hash = (hash + (hash << 1) + (hash << 4) + (hash << 7) + (hash << 8) + (hash << 24)) >>> 0;
  }
  return hash >>> 0;
}

/**
 * Pick one member of a list from a seed.
 *
 * The list's ORDER and LENGTH are part of the identity: `hash % length` remaps
 * every existing seed when either changes, so a corpus is append-with-care and
 * is pinned by a golden test. That cost is accepted deliberately — it buys
 * permanent per-agent stability, which is the property the product needs.
 *
 * Throws on an empty list rather than returning `undefined`. A caller that has
 * no options has a corpus bug, and a silent `undefined` would surface far away
 * as a blank tile.
 */
export function pickFromSeed<T>(items: readonly T[], seed: string): T {
  if (items.length === 0) {
    throw new Error("pickFromSeed: empty corpus");
  }
  const item = items[hashSeed(seed) % items.length];
  // `noUncheckedIndexedAccess` widens the element type; the modulo above makes
  // the index in-range, so this narrows what the compiler cannot prove.
  return item as T;
}
