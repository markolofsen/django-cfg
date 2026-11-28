import type { VoiceCapability } from "../core";

export interface MockVoiceOptions {
  /**
   * The sentence to dictate, revealed word by word.
   *
   * Each step emits the phrase so far as an INTERIM result, exactly as a real
   * engine does — it re-sends its whole current guess rather than the delta.
   * That is the behaviour `VoiceSession` exists to absorb, so a mock that
   * emitted deltas would make the story agree for the wrong reason.
   */
  readonly phrase?: string;
  /** Delay between words. Slow enough that `Recording` is visible on screen. */
  readonly delayMs?: number;
  /**
   * Fail instead of dictating — a denied microphone permission.
   *
   * The realistic failure: the user presses the mic and clicks "Block". It
   * settles on the snapshot as `error`; nothing throws.
   */
  readonly failWith?: string;
}

/**
 * A scripted `VoiceCapability` — no microphone, no Web Speech API.
 *
 * A story that needed real speech is a story nobody can run: it would demand a
 * permission prompt, a quiet room, and an engine that Firefox does not have. So
 * the mock owns the timing and the transcript, and the story asserts what the
 * COMPOSER does with them.
 */
export function mockVoice({
  phrase = "summarise the last three replies",
  delayMs = 260,
  failWith,
}: MockVoiceOptions = {}): VoiceCapability {
  let timer: ReturnType<typeof setTimeout> | undefined;
  let abort: (() => void) | undefined;

  return {
    start: (onText, signal) =>
      new Promise((resolve, reject) => {
        if (failWith !== undefined) {
          // Asynchronously, like a real permission denial: a synchronous throw
          // would reject before the session has stored its controller, and the
          // error would land on a session it can no longer match.
          timer = setTimeout(() => reject(new Error(failWith)), delayMs);
          return;
        }

        const words = phrase.split(" ");
        let index = 0;

        const step = () => {
          if (signal.aborted) return;
          index += 1;
          const soFar = words.slice(0, index).join(" ");
          if (index >= words.length) {
            // The last emission COMMITS. Without a final result the session
            // holds the whole sentence as interim, and a stop would still work
            // but the story would never exercise the commit path.
            onText(soFar, true);
            resolve();
            return;
          }
          onText(soFar, false);
          timer = setTimeout(step, delayMs);
        };

        abort = () => resolve();
        signal.addEventListener("abort", () => {
          clearTimeout(timer);
          abort?.();
        });
        timer = setTimeout(step, delayMs);
      }),
    stop: () => {
      clearTimeout(timer);
    },
  };
}
