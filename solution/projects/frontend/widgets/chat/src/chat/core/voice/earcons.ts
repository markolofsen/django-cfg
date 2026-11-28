/**
 * The two dictation earcons, as a port.
 *
 * The session plays them, not the button: the button knows what was pressed,
 * only the session knows what the engine did. A permission prompt, a silence
 * timeout and an already-running engine all sit between the two.
 *
 * ORDER: the start tone plays before the engine is asked to listen, the stop
 * tone after it is told to stop. A tone inside that window is transcribed as a
 * word. Reversing either line is silent — dictation still works and the
 * transcript merely gains a phantom syllable.
 */

export type EarconKind = "start" | "stop";

/**
 * How a host plays one tone.
 *
 * A function, not a URL pair: the package ships no audio. The host already owns
 * preloading, the mute gate and the autoplay-rejection rule.
 *
 * Must not throw and must not block — it runs on the path that opens the
 * microphone.
 */
export type PlayEarcon = (kind: EarconKind) => void;

/**
 * The dictation-tones capability.
 *
 * Separate from `VoiceCapability` because an absent voice capability means the
 * DEFAULT engine — a host on that path has no object to hang a player on. Sound
 * and engine are also independent choices: the browser's recogniser with our
 * tones, or the reverse.
 *
 * Declared here rather than in `core/capabilities.ts` so the port, the safety
 * wrapper and the seam that exposes them stay in one file.
 */
export interface VoiceSoundsCapability {
  readonly play: PlayEarcon;
}

/**
 * Wrap a player so a throwing host costs a tone, not the sentence.
 *
 * `undefined` in ⇒ no-op out, so the session holds one shape and needs no null
 * check at either call site.
 */
export function safeEarcon(play: PlayEarcon | undefined): PlayEarcon {
  if (play === undefined) return () => undefined;
  return (kind) => {
    try {
      play(kind);
    } catch {
      // Silent: this would fire once per dictation and train the reader to
      // ignore the screen during voice work.
    }
  };
}
