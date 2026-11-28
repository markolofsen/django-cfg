/**
 * Deterministic mock RecognitionEngine for stories.
 *
 * Built from public `createExternalEngine` — no internal imports, no
 * microphone, no network. Emits a scripted partial→final sequence on a
 * timer so screenshots / CI are stable.
 */

import {
  createExternalEngine,
  type RecognitionEngine,
} from '..';

export interface MockEngineOptions {
  phrases?: string[];
  partialIntervalMs?: number;
  finalIntervalMs?: number;
  id?: string;
}

const DEFAULT_PHRASES = [
  'Hello and welcome to the dictation demo.',
  'This text is being typed by the mock engine.',
  'Try the buttons on the right to control the session.',
];

/**
 * Per-language phrase sets: the mock HONOURS the session language the
 * way a real engine would, so the language chip / menu visibly change
 * the output in stories — switching mid-recording restarts the session
 * and the transcript flips scripts.
 */
const PHRASES_BY_LANGUAGE: Record<string, string[]> = {
  ru: [
    'Привет, это демо диктовки.',
    'Этот текст печатает мок-движок по-русски.',
    'Переключите язык, чтобы сменить фразы.',
  ],
};

export function createMockEngine(
  opts: MockEngineOptions = {},
): RecognitionEngine {
  const partialMs = opts.partialIntervalMs ?? 120;
  const finalMs = opts.finalIntervalMs ?? 1500;
  // Captured from EngineStartOptions on every start — `onStart` runs
  // before the first scripted tick, so the subscribe loop always reads
  // the language of the CURRENT session.
  let sessionLanguage = '';

  const phrasesForSession = (): string[] => {
    if (opts.phrases) return opts.phrases;
    const primary = sessionLanguage.split('-')[0]?.toLowerCase() ?? '';
    return PHRASES_BY_LANGUAGE[primary] ?? DEFAULT_PHRASES;
  };

  return createExternalEngine({
    id: opts.id ?? 'mock',
    supported: true,
    // Rolling engine — emits many partial/final pairs per session, so
    // the session must stay open after each `emitFinal`.
    closeOnFinal: false,
    onStart: (start) => {
      sessionLanguage = start.language;
    },
    onStop: () => undefined,
    subscribe: (handle) => {
      let phraseIdx = 0;
      let charIdx = 0;
      let stopped = false;
      const timers: ReturnType<typeof setTimeout>[] = [];

      // Kick into listening state immediately so the UI light goes on.
      const tStart = setTimeout(() => handle.markListening(), 0);
      timers.push(tStart);

      const tick = (): void => {
        if (stopped) return;
        const phrases = phrasesForSession();
        const phrase = phrases[phraseIdx % phrases.length] ?? '';
        charIdx = Math.min(charIdx + 2, phrase.length);
        handle.emitPartial(phrase.slice(0, charIdx));
        if (charIdx >= phrase.length) {
          const tFinal = setTimeout(() => {
            if (stopped) return;
            handle.emitFinal(phrase);
            phraseIdx += 1;
            charIdx = 0;
            const tNext = setTimeout(tick, partialMs);
            timers.push(tNext);
          }, Math.max(0, finalMs - partialMs));
          timers.push(tFinal);
          return;
        }
        const tNext = setTimeout(tick, partialMs);
        timers.push(tNext);
      };
      const tFirst = setTimeout(tick, partialMs);
      timers.push(tFirst);

      return () => {
        stopped = true;
        timers.forEach(clearTimeout);
      };
    },
  });
}
