export interface BackoffPolicy {
  /** The first retry waits up to twice this; each later one doubles the ceiling. */
  baseMs: number;
  maxMs: number;
}

export const DEFAULT_BACKOFF: BackoffPolicy = { baseMs: 500, maxMs: 30_000 };

/**
 * Full jitter: a uniform delay between 0 and an exponentially growing ceiling,
 * capped, the first retry included. Jitter is what keeps every tab of a
 * restarted server from reconnecting in the same instant.
 *
 * `attempt` counts failures since the connection was last stable, starting at 1.
 */
export function backoffDelay(
  attempt: number,
  random: () => number,
  policy: BackoffPolicy = DEFAULT_BACKOFF,
): number {
  const exponent = Math.max(1, Math.min(attempt, 30));
  const ceiling = Math.min(policy.maxMs, policy.baseMs * 2 ** exponent);
  return random() * ceiling;
}
