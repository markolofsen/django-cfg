import { useEffect, useRef, useState } from "react";
import { Loader2 } from "lucide-react";
import {
  ComposerBanner,
  ComposerBannerBody,
  ComposerBannerDescription,
  ComposerBannerIcon,
  ComposerBannerTitle,
} from "./banner";

/**
 * `<CommandProgress>` — "this session-control verb is still running".
 *
 * A control verb is not a turn: it opens no streaming message, so the
 * transcript's pending row never appears for it and the composer shows nothing.
 * The verb also takes real time — an engine walking a transcript is tens of
 * seconds — which leaves a person who pressed Enter with an emptied field, no
 * row in the conversation, and no evidence anything is happening. They press it
 * again.
 *
 * Above the composer rather than in the transcript, and that follows the
 * existing split rather than taste: `ComposerBanner` is where a notice about
 * the SESSION goes, while the transcript's pending row belongs to a turn. A row
 * in the transcript would also have to be removed again on completion, since
 * the verb writes no message the row could resolve into.
 *
 * Copy is the HOST's, like every other banner here: which verbs exist comes
 * from a generated catalogue this package does not read, and the sentence for
 * one does not template across locales.
 *
 * The elapsed counter is the load-bearing half. A spinner alone says "busy" and
 * says it identically at two seconds and at two minutes, which is exactly the
 * ambiguity that makes a person retry; a climbing number says the wait is
 * progressing rather than hung.
 */
export interface CommandProgressProps {
  /**
   * The verb in flight, or `null` when nothing is running. Null renders
   * nothing, so this can be mounted unconditionally beside the other slots.
   */
  readonly verb: string | null;
  /** What is happening, already localised — "Compacting the conversation…". */
  readonly title: string;
  /**
   * Given whole seconds waited, the counter's text. Called only after the quiet
   * threshold passes.
   */
  readonly elapsed: (seconds: number) => string;
  /**
   * How long to stay quiet before showing a number. A verb that finishes fast
   * should leave no trace of a counter at all — a digit that appears and
   * vanishes reads as a glitch.
   */
  readonly elapsedAfterMs?: number;
}

const DEFAULT_ELAPSED_AFTER_MS = 3_000;

export function CommandProgress({
  verb,
  title,
  elapsed,
  elapsedAfterMs = DEFAULT_ELAPSED_AFTER_MS,
}: CommandProgressProps) {
  const seconds = useElapsedSeconds(verb, elapsedAfterMs);

  if (verb === null) return null;

  const counter = seconds === null ? null : elapsed(seconds);

  return (
    <ComposerBanner>
      <ComposerBannerIcon tone="info">
        <Loader2 className="size-4 animate-spin" aria-hidden />
      </ComposerBannerIcon>
      <ComposerBannerBody>
        <ComposerBannerTitle>{title}</ComposerBannerTitle>
        {counter === null ? null : (
          <ComposerBannerDescription>
            <span className="tabular-nums">{counter}</span>
          </ComposerBannerDescription>
        )}
      </ComposerBannerBody>
    </ComposerBanner>
  );
}

/**
 * Whole seconds since THIS verb started, or `null` under the threshold.
 *
 * Keyed on the verb rather than on mount: the banner stays mounted between two
 * runs in the same room, so a mount-time start would report the age of the
 * previous wait. Re-running the effect on the verb restarts the clock, and a
 * `null` verb stops the interval rather than leaving it ticking behind an idle
 * room.
 */
function useElapsedSeconds(verb: string | null, afterMs: number): number | null {
  const startedAt = useRef(0);
  const [seconds, setSeconds] = useState<number | null>(null);

  useEffect(() => {
    if (verb === null) {
      setSeconds(null);
      return;
    }
    startedAt.current = Date.now();
    setSeconds(null);
    const id = setInterval(() => {
      const waited = Date.now() - startedAt.current;
      setSeconds(waited < afterMs ? null : Math.floor(waited / 1_000));
    }, 1_000);
    return () => clearInterval(id);
  }, [verb, afterMs]);

  return seconds;
}
