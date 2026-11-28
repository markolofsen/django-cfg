import type { VoiceCapability } from "../capabilities";
import { safeEarcon, type PlayEarcon } from "./earcons";

/**
 * Dictation as a state machine — no React, no Web Speech API.
 *
 * The host owns recognition; this owns the two rules that are easy to get
 * wrong and invisible when they are:
 *
 * 1. **An interim result REPLACES the previous interim, never appends.** The
 *    engine re-emits its whole current guess as it refines — "hello wor",
 *    "hello world" — so appending duplicates the sentence in front of the user.
 * 2. **A final result COMMITS**, and the next interim starts from empty.
 *
 * The draft therefore always reads `committed + interim`, and only `committed`
 * survives a stop.
 */

export interface VoiceSnapshot {
  readonly recording: boolean;
  /** Text the engine has committed. */
  readonly committed: string;
  /** The current guess. Replaced wholesale on each interim result. */
  readonly interim: string;
  /** What the composer should show: `committed + interim`. */
  readonly text: string;
  readonly error?: string;
}

export interface VoiceSessionOptions {
  readonly capability: VoiceCapability;
  readonly onChange: (snapshot: VoiceSnapshot) => void;
  /**
   * Play a start/stop tone. Absent ⇒ dictation is silent, which is a legitimate
   * configuration: the package ships no audio and a host that supplies none
   * gets working dictation without it.
   */
  readonly playEarcon?: PlayEarcon;
}

const IDLE: VoiceSnapshot = {
  recording: false,
  committed: "",
  interim: "",
  text: "",
};

export class VoiceSession {
  private snapshot: VoiceSnapshot = IDLE;
  private controller: AbortController | null = null;
  /** Wrapped once here so neither call site needs a null check or a try. */
  private readonly earcon: PlayEarcon;

  constructor(private readonly options: VoiceSessionOptions) {
    this.earcon = safeEarcon(options.playEarcon);
  }

  get state(): VoiceSnapshot {
    return this.snapshot;
  }

  /** Begin, or do nothing if already recording. */
  start(): void {
    if (this.snapshot.recording) return;

    const controller = new AbortController();
    this.controller = controller;
    this.emit({ recording: true, committed: "", interim: "", error: undefined });

    // Before `capability.start`: after it the microphone is live and the tone
    // is transcribed as a word.
    this.earcon("start");

    this.options.capability
      .start((text, final) => {
        // A result arriving after stop() belongs to a session the user ended.
        // Accepting it would append words to a draft they already sent.
        if (this.controller !== controller) return;
        this.receive(text, final);
      }, controller.signal)
      .then(() => {
        if (this.controller !== controller) return;
        // The engine ended on its own (a pause, a time limit). Commit whatever
        // interim was in flight rather than discarding the last words.
        this.commitAndStop();
      })
      .catch((cause: unknown) => {
        if (this.controller !== controller) return;
        this.controller = null;
        // Closes the pair. The start tone has already played — it must, before
        // the microphone opens — so silence here leaves a session the user heard
        // begin and never end.
        this.earcon("stop");
        // Failures settle on the snapshot; throwing here would surface as an
        // unhandled rejection while the user is mid-sentence.
        this.emit({
          recording: false,
          interim: "",
          error: cause instanceof Error ? cause.message : String(cause),
        });
      });
  }

  /**
   * Stop and commit the in-flight interim.
   *
   * Safe to call synchronously from a send: the capability's `stop` is invoked
   * first, so no further words can arrive.
   */
  stop(): void {
    if (!this.snapshot.recording) return;
    this.options.capability.stop();
    this.controller?.abort();
    this.controller = null;
    this.commitAndStop();
  }

  /**
   * Stop and DISCARD everything — for a send.
   *
   * Distinct from `stop()` on purpose: after a send the draft is cleared, so
   * committing dictated text back into it would resurrect the message the user
   * just sent.
   *
   * SILENT: the caller is a send, which plays its own chime. A stop tone under
   * it is two sounds for one action, and the user pressed send, not stop.
   */
  cancel(): void {
    this.options.capability.stop();
    this.controller?.abort();
    this.controller = null;
    // Through emit(), like every other transition. Assigning `this.snapshot`
    // directly is the one way to leave `text` stale, since emit() is the sole
    // place that recomputes it — a mutant doing exactly that survived a test
    // asserting only `text`, because the stale value happened to be correct.
    this.emit({ recording: false, committed: "", interim: "", error: undefined });
  }

  /** Take the dictated text and reset, for handing to the draft. */
  take(): string {
    const text = this.snapshot.text;
    this.cancel();
    return text;
  }

  dispose(): void {
    this.options.capability.stop();
    this.controller?.abort();
    this.controller = null;
  }

  private receive(text: string, final: boolean): void {
    if (final) {
      // Committed text accumulates with a separating space; the engine emits
      // phrases, not a continuous stream, so joining without one runs the
      // sentences together.
      const committed = this.snapshot.committed === ""
        ? text
        : `${this.snapshot.committed} ${text}`;
      this.emit({ committed, interim: "" });
      return;
    }
    // REPLACE, never append — the engine re-sends its whole current guess.
    this.emit({ interim: text });
  }

  /**
   * Both routes here — an explicit `stop()` and an engine ending on its own —
   * are moments the user must hear, so the stop tone lives here. The microphone
   * is already shut on both. `cancel()` does not pass through.
   */
  private commitAndStop(): void {
    this.earcon("stop");
    const { committed, interim } = this.snapshot;
    const merged = interim === ""
      ? committed
      : committed === ""
        ? interim
        : `${committed} ${interim}`;
    this.controller = null;
    this.emit({ recording: false, committed: merged, interim: "" });
  }

  private emit(patch: Partial<Omit<VoiceSnapshot, "text">>): void {
    const next = { ...this.snapshot, ...patch };
    // `text` is DERIVED, never assigned: two writers for one value is how the
    // draft and the snapshot drift apart.
    const text = next.interim === ""
      ? next.committed
      : next.committed === ""
        ? next.interim
        : `${next.committed} ${next.interim}`;
    this.snapshot = { ...next, text };
    this.options.onChange(this.snapshot);
  }
}
