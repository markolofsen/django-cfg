/**
 * Pairwise array comparison for `React.memo` props.
 *
 * Four hand-rolled copies of this existed across the nav layouts — two of them
 * (`navItemsShallowEqual` in NavbarShell and NavDesktopItems) byte-identical.
 * Each wrote `const bi = b[i]` inside `a.every`, which is safe only because the
 * length was compared on the line above; under `strict` that produced 26 of the
 * package's 28 errors, all asking the same question about the same missing
 * connection between the guard and the index.
 *
 * `entries()` carries the pair, so an element and its counterpart are produced
 * together and neither can be `undefined`. The guard is not restated — it is
 * expressed once, in the shape of the loop.
 */
export function shallowEqualBy<T>(
  a: readonly T[] | undefined,
  b: readonly T[] | undefined,
  equal: (x: T, y: T) => boolean,
): boolean {
  if (a === b) return true;
  if (!a || !b || a.length !== b.length) return false;
  for (const [index, left] of a.entries()) {
    const right = b[index];
    // `index` comes from `a.entries()` and the lengths matched, so `right`
    // exists. The check is what proves it to the compiler; it is not reachable.
    if (right === undefined || !equal(left, right)) return false;
  }
  return true;
}
