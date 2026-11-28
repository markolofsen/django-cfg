/**
 * Deep Merge Utility
 *
 * Recursively merges objects, replacing arrays instead of merging them.
 */

function isPlainObject(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

/**
 * `T extends object` rather than `Record<string, unknown>`: call sites pass
 * Next.js config interfaces, which have declared keys and no index signature —
 * they are not assignable to `Record<string, unknown>`.
 */
export function deepMerge<T extends object>(target: T, source: Partial<T>): T {
  const output: T = { ...target };

  for (const key of Object.keys(source) as Array<keyof T & string>) {
    const sourceValue: unknown = source[key];
    if (sourceValue === undefined) continue;

    const targetValue: unknown = output[key];

    // Objects: deep merge. Arrays and primitives: replace.
    // The recursion is instantiated at Record<string, unknown> — all the guards
    // prove — and the result cast back to the key's declared type.
    const merged =
      isPlainObject(sourceValue) && isPlainObject(targetValue)
        ? deepMerge(targetValue, sourceValue)
        : sourceValue;

    output[key] = merged as T[typeof key];
  }

  return output;
}
