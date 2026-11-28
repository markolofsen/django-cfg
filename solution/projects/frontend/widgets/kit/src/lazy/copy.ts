/**
 * The two strings a placeholder needs, as a typed object rather than a
 * `t(key)` resolver.
 *
 * The donor read them through `useAppT()`, which is `useTypedT` and therefore
 * needs a provider: a fallback is what renders in a story, a test and a
 * server pass — the three places least likely to have mounted one. A typed
 * object is the schema of record, resolves to English with no provider, and
 * cannot be missing a key at build time.
 */
export interface LazyCopy {
  /** The caption under a panel-sized placeholder. */
  readonly loading: string;
  /** The accessible name when no caption is shown. */
  readonly loadingLabel: string;
}

export const DEFAULT_LAZY_COPY: LazyCopy = {
  loading: 'Loading…',
  loadingLabel: 'Loading',
};

let copy: LazyCopy = DEFAULT_LAZY_COPY;

/** Replace the placeholder copy once, at startup. */
export function configureLazyCopy(next: Partial<LazyCopy>): void {
  copy = { ...DEFAULT_LAZY_COPY, ...next };
}

/**
 * Read lazily, never at module scope: a host configures the copy after this
 * module is evaluated, and a baked-in read would pin every placeholder to
 * English with no symptom but the wrong word.
 */
export function lazyCopy(): LazyCopy {
  return copy;
}
