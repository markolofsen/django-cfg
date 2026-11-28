import { useCallback, useEffect, useRef } from 'react';

import type { ComposerNodes } from '../focus/use-composer-nodes';

/**
 * The microphone stays open after a stop is asked for, until the words stop arriving. Recognition runs behind the voice: the engine reports a phrase a few hundred
 * milliseconds after it was said, and the widget's stop closes the engine at once and drops what is still on its way. So the stop waits for the field to stay unchanged for
 * `QUIET_MS` (but at least that long, and never past `PATIENCE_MS`); the stop is then the widget's own, and its commit puts what was heard into the draft.
 */
export const QUIET_MS = 450;
export const PATIENCE_MS = 2500;
const POLL_MS = 80;

/**
 * `stop(after)` ends the dictation after the grace period, then runs `after` once the transcript has reached the draft. The microphone button's own press while
 * recording goes through the same wait (a capture listener takes the press first and re-issues it later), so every way to stop loses nothing.
 */
export function useGracefulStop({ mic }: ComposerNodes, recording: boolean, draftText: () => string): (after?: () => void) => void {
  const waiting = useRef(false);
  const ours = useRef(false);

  const stop = useCallback(
    (after?: () => void) => {
      if (waiting.current) return;
      waiting.current = true;
      const began = Date.now();
      let seen = draftText();
      let changed = began;
      const settle = () => {
        const now = Date.now();
        const text = draftText();
        if (text !== seen) {
          seen = text;
          changed = now;
        }
        if (now - changed < QUIET_MS && now - began < PATIENCE_MS) return void window.setTimeout(settle, POLL_MS);
        ours.current = true;
        mic()?.click();
        ours.current = false;
        waiting.current = false;
        // The widget commits the transcript on that click; the draft holds it one render later.
        if (after) window.setTimeout(after, 80);
      };
      window.setTimeout(settle, POLL_MS);
    },
    [mic, draftText],
  );

  useEffect(() => {
    const button = mic();
    if (!recording || !button) return;
    const take = (event: Event) => {
      if (ours.current) return;
      event.preventDefault();
      event.stopImmediatePropagation();
      stop();
    };
    button.addEventListener('click', take, true);
    return () => button.removeEventListener('click', take, true);
  }, [recording, mic, stop]);

  return stop;
}
