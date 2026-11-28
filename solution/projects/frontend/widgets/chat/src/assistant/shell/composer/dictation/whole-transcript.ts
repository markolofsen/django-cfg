import type { VoiceCapability } from '../../../../chat/core';

/**
 * Browser dictation that always reports EVERYTHING heard since the start, as one text.
 *
 * The widget's own engine reports each result of the recogniser separately and the session stitches them (final results appended, the interim replaced). Chrome reports
 * several results at once, ends the recogniser by itself after a pause, and revises earlier results, and under those the field kept only the last words. Here the whole
 * transcript is rebuilt from `event.results` at every event and handed over as one replacing text, so nothing can be dropped by the stitching; a recogniser that ends on
 * its own is started again and its text is kept in front of the next one.
 */

interface ResultLike {
  readonly length: number;
  readonly [index: number]: { readonly transcript: string } | undefined;
}
interface EventLike {
  readonly results: { readonly length: number; readonly [index: number]: ResultLike | undefined };
}
interface RecognitionLike {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  start: () => void;
  stop: () => void;
  abort: () => void;
  onresult: ((event: EventLike) => void) | null;
  onerror: ((event: { readonly error?: string }) => void) | null;
  onend: (() => void) | null;
}
type Constructor = new () => RecognitionLike;

function constructorFor(): Constructor | undefined {
  if (typeof window === 'undefined') return undefined;
  const scope = window as unknown as { SpeechRecognition?: Constructor; webkitSpeechRecognition?: Constructor };
  return scope.SpeechRecognition ?? scope.webkitSpeechRecognition;
}

const join = (parts: string[]) => parts.map((part) => part.trim()).filter(Boolean).join(' ');

/** `language` is read at every (re)start, so a language picked in the menu applies to the next dictation. `undefined` when the browser cannot dictate. */
export function createWholeTranscriptSpeech(language: () => string): VoiceCapability | undefined {
  const Recognition = constructorFor();
  if (!Recognition) return undefined;
  let active: RecognitionLike | null = null;

  return {
    start: (onText, signal) =>
      new Promise<void>((resolve, reject) => {
        if (signal.aborted) return resolve();
        // What earlier recogniser runs of this dictation heard (a run that ended by itself is started again).
        let before = '';
        let latest = '';

        const run = () => {
          const recognition = new Recognition();
          active = recognition;
          recognition.continuous = true;
          recognition.interimResults = true;
          recognition.lang = language();

          recognition.onresult = (event) => {
            const heard: string[] = [];
            for (let i = 0; i < event.results.length; i += 1) {
              const text = event.results[i]?.[0]?.transcript;
              if (text) heard.push(text);
            }
            latest = join([before, ...heard]);
            // Always `final: false`: each report REPLACES the last, and the session's own stop commits the latest one.
            onText(latest, false);
          };
          recognition.onerror = (event) => {
            if (event.error === 'no-speech' || event.error === 'aborted') return;
            signal.removeEventListener('abort', onAbort);
            active = null;
            reject(new Error(event.error ?? 'speech recognition failed'));
          };
          recognition.onend = () => {
            if (active === recognition) active = null;
            if (signal.aborted) return resolve();
            // Ended by itself (a pause, a time limit): keep what was heard and listen again.
            before = latest;
            try {
              run();
            } catch {
              resolve();
            }
          };
          try {
            recognition.start();
          } catch {
            resolve();
          }
        };

        const onAbort = () => {
          active?.abort();
          active = null;
          resolve();
        };
        signal.addEventListener('abort', onAbort, { once: true });
        run();
      }),
    // Gracefully: the engine may still report what was said, and the session reads it until its own stop.
    stop: () => active?.stop(),
  };
}
