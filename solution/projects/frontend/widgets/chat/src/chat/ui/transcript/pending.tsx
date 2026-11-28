import { memo, useEffect, useRef, useState } from "react";

import { TurnMark } from "./turn-mark";

export interface PendingIndicatorProps {
  /**
   * What the wait is for — "Thinking…", say. Optional: the dots alone already
   * say "something is happening", and a label is the host's copy.
   */
  readonly label?: string;
  readonly className?: string;
  /**
   * Rendered beside the label once the wait passes `elapsedAfterMs`, given the
   * whole seconds waited.
   *
   * Absent ⇒ no counter, which is the right default: a number invites watching
   * it. It earns its place only in the long tail, where an agent thinking for
   * forty seconds is otherwise indistinguishable from a hung one.
   */
  readonly elapsed?: (seconds: number) => string;
  /** How long to stay quiet before the counter appears. */
  readonly elapsedAfterMs?: number;
}

const DEFAULT_ELAPSED_AFTER_MS = 5_000;

/**
 * The "your turn was sent, nothing has come back yet" row.
 *
 * Carries `TurnMark` in its waiting state — the same shape that leads the reply
 * once text starts and rests under it when the turn ends. Three bouncing dots
 * lived here before, and their fault was being a dead end: they said "busy",
 * then vanished, so the end of an answer was marked by nothing at all.
 *
 * `aria-live="off"` on the row: the transcript already announces turn start and
 * end through one polite region, and a second live region here would make every
 * reply be announced twice.
 */
function PendingIndicatorRaw({
  label,
  className,
  elapsed,
  elapsedAfterMs = DEFAULT_ELAPSED_AFTER_MS,
}: PendingIndicatorProps) {
  const seconds = useElapsedSeconds(elapsed !== undefined, elapsedAfterMs);

  return (
    <div className={className} aria-live="off">
      <TurnMark state="waiting" />
      {label === undefined ? null : <span>{label}</span>}
      {seconds === null || elapsed === undefined ? null : (
        <span className="tabular-nums">{elapsed(seconds)}</span>
      )}
    </div>
  );
}

export const PendingIndicator = memo(PendingIndicatorRaw);

/**
 * Whole seconds since this row mounted, or `null` while under the threshold.
 *
 * Mount time is the start, and that is exact rather than approximate: the row
 * is rendered only while the turn is pending, so it mounts when the wait begins
 * and unmounts on the first part.
 *
 * The interval only runs when a counter was asked for — an unused indicator
 * must not tick once per second forever behind a background tab.
 */
function useElapsedSeconds(enabled: boolean, afterMs: number): number | null {
  const startedAt = useRef<number>(0);
  const [seconds, setSeconds] = useState<number | null>(null);

  useEffect(() => {
    if (!enabled) return;
    startedAt.current = Date.now();
    const id = setInterval(() => {
      const waited = Date.now() - startedAt.current;
      setSeconds(waited < afterMs ? null : Math.floor(waited / 1_000));
    }, 1_000);
    return () => clearInterval(id);
  }, [enabled, afterMs]);

  return seconds;
}
