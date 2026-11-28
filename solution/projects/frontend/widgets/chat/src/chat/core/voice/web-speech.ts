import type { VoiceCapability } from "../capabilities";

/**
 * The browser's own dictation, as a `VoiceCapability`.
 *
 * This is the package's DEFAULT engine, and the reason the capability seam
 * still exists: audio never leaves the device here, but a host with a server
 * transcriber, Whisper, or a native bridge supplies its own capability and this
 * steps aside. Neither available means no microphone button at all — a greyed
 * out mic is a promise the product cannot keep.
 *
 * Everything racy — an interim replacing its predecessor, a result arriving
 * after stop, an engine that ends on its own — is `VoiceSession`'s, not this
 * file's. This is the adapter and nothing more.
 */

/**
 * The two constructor spellings, without pulling in DOM lib types the package
 * does not depend on.
 *
 * Typed structurally rather than via `SpeechRecognition` from `lib.dom`: that
 * type is not in every consumer's TS configuration, and a package that fails to
 * compile in a host missing one DOM lib is worse than one local interface.
 */
interface RecognitionLike {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  start: () => void;
  stop: () => void;
  abort: () => void;
  onresult: ((event: RecognitionEventLike) => void) | null;
  onerror: ((event: { readonly error?: string }) => void) | null;
  onend: (() => void) | null;
}

interface RecognitionResultLike {
  readonly isFinal: boolean;
  readonly length: number;
  readonly [index: number]: { readonly transcript: string } | undefined;
}

interface RecognitionEventLike {
  readonly resultIndex: number;
  readonly results: {
    readonly length: number;
    readonly [index: number]: RecognitionResultLike | undefined;
  };
}

type RecognitionConstructor = new () => RecognitionLike;

function constructorFor(): RecognitionConstructor | undefined {
  if (typeof window === "undefined") return undefined;
  const scope = window as unknown as {
    SpeechRecognition?: RecognitionConstructor;
    webkitSpeechRecognition?: RecognitionConstructor;
  };
  return scope.SpeechRecognition ?? scope.webkitSpeechRecognition;
}

/**
 * Whether the browser can dictate at all.
 *
 * Exported so a host can decide before rendering. MediaRecorder is deliberately
 * NOT treated as support: it only produces audio, and turning that into text
 * needs a transcription endpoint — audio leaving the device, which is exactly
 * the decision the capability seam leaves to the host.
 */
export function isWebSpeechAvailable(): boolean {
  return constructorFor() !== undefined;
}

export interface WebSpeechOptions {
  /** BCP-47 tag. Read at START, so a change applies to the next dictation. */
  readonly language: () => string;
}

/**
 * Build the default capability, or `undefined` when the browser has no engine.
 *
 * `language` is a FUNCTION, not a value: the capability object outlives any one
 * dictation, and reading the tag at start is what lets a language change take
 * effect without rebuilding the session mid-sentence.
 */
export function createWebSpeechCapability(
  options: WebSpeechOptions,
): VoiceCapability | undefined {
  const Recognition = constructorFor();
  if (Recognition === undefined) return undefined;

  let active: RecognitionLike | null = null;

  return {
    start: (onText, signal) =>
      new Promise<void>((resolve, reject) => {
        if (signal.aborted) {
          resolve();
          return;
        }
        const recognition = new Recognition();
        active = recognition;
        // `continuous` so a pause between sentences does not end the session,
        // and `interimResults` so words appear while they are being said. The
        // interim half is what `VoiceSession`'s replace-never-append rule is
        // for; without it dictation is silent until a phrase completes.
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = options.language();

        const finish = (): void => {
          if (active === recognition) active = null;
          signal.removeEventListener("abort", onAbort);
        };

        const onAbort = (): void => {
          recognition.abort();
          finish();
          resolve();
        };
        signal.addEventListener("abort", onAbort, { once: true });

        recognition.onresult = (event) => {
          // From `resultIndex`, not from zero: the engine re-sends the whole
          // results list, and replaying it from the start re-delivers phrases
          // already committed — the sentence duplicates itself.
          for (let i = event.resultIndex; i < event.results.length; i += 1) {
            const result = event.results[i];
            const transcript = result?.[0]?.transcript;
            if (result === undefined || transcript === undefined) continue;
            onText(transcript, result.isFinal);
          }
        };

        recognition.onerror = (event) => {
          finish();
          // `no-speech` and `aborted` are ordinary endings, not faults: the
          // first is a silent room and the second is the user pressing stop.
          // Surfacing either as an error puts a red message under a composer
          // for doing nothing wrong.
          if (event.error === "no-speech" || event.error === "aborted") {
            resolve();
            return;
          }
          reject(new Error(event.error ?? "speech recognition failed"));
        };

        recognition.onend = () => {
          finish();
          resolve();
        };

        try {
          recognition.start();
        } catch (cause) {
          // `start()` throws synchronously when one is already running — a
          // double-press. Treat it as a no-op rather than a failure.
          finish();
          resolve();
          void cause;
        }
      }),
    stop: () => {
      // `stop()` rather than `abort()`: it lets the engine deliver the final
      // result for what was already said, which is the difference between
      // pressing stop mid-sentence and losing that sentence.
      active?.stop();
    },
  };
}
