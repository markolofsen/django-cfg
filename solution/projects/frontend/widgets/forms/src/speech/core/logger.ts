/**
 * Speech recognition dev logger.
 *
 * Mirrors `getChatLogger()` in the Chat tool so consumers reason about both
 * surfaces the same way. Silent in production by default; emits `error`
 * level always.
 *
 * Opt-in mechanisms (any one is enough):
 *   1. `NODE_ENV === 'development'` (auto, via `isDev` from `@djangocfg/ui-core`).
 *   2. `localStorage.setItem('cfg.forms.speech_debug', '1')` — runtime
 *      toggle without a rebuild. Useful for diagnosing a prod bug.
 *   3. Explicit `getSpeechLogger(true)` from a host component.
 *
 * Sub-loggers:
 *   engine     — engine lifecycle (start/stop/abort/result)
 *   dictation  — `useDictation` state (anchor, partial → final merge)
 *   slot       — `VoiceComposerSlot` UI (mount, support gating, button)
 *   composer   — composer handle registry (focus / setValue / pin caret)
 *   mic        — `useMicLevel` / `useMicDevices` / device picker
 *   push       — push-to-talk hotkey events
 *   error      — caught errors (always emitted, even when disabled)
 */
import { consola, type ConsolaInstance } from 'consola';

import { isBrowser, isDev } from '@djangocfg/ui-core/lib';
import { CFG_KEYS } from '@djangocfg/api/storage';

export type SpeechLogScope =
  | 'engine'
  | 'dictation'
  | 'slot'
  | 'composer'
  | 'mic'
  | 'push'
  | 'error';

export interface SpeechLogger {
  engine: ConsolaInstance;
  dictation: ConsolaInstance;
  slot: ConsolaInstance;
  composer: ConsolaInstance;
  mic: ConsolaInstance;
  push: ConsolaInstance;
  error: ConsolaInstance;
  /** True when this logger is actually emitting. */
  enabled: boolean;
}

const SCOPES: SpeechLogScope[] = [
  'engine',
  'dictation',
  'slot',
  'composer',
  'mic',
  'push',
  'error',
];

const STORAGE_KEY = CFG_KEYS.formsSpeechDebug.key;

function readStorageFlag(): boolean {
  if (!isBrowser) return false;
  try {
    return window.localStorage.getItem(STORAGE_KEY) === '1';
  } catch {
    return false;
  }
}

const cache = new Map<boolean, SpeechLogger>();

function buildLogger(enabled: boolean): SpeechLogger {
  const root = consola.withTag('speech');
  const subs = Object.fromEntries(
    SCOPES.map((scope) => [scope, root.withTag(scope)]),
  ) as Record<SpeechLogScope, ConsolaInstance>;

  if (!enabled) {
    for (const scope of SCOPES) {
      if (scope === 'error') continue;
      subs[scope].level = -999;
    }
  }

  return { ...subs, enabled };
}

/**
 * Get the speech logger.
 *
 * @param debug Explicit override. `undefined` falls back to `isDev` OR
 *              `localStorage['cfg.forms.speech_debug'] === '1'`.
 */
export function getSpeechLogger(debug?: boolean): SpeechLogger {
  const enabled = debug ?? (isDev || readStorageFlag());
  let logger = cache.get(enabled);
  if (!logger) {
    logger = buildLogger(enabled);
    cache.set(enabled, logger);
  }
  return logger;
}

/**
 * Legacy flat-tag logger. New code should prefer `getSpeechLogger()` for
 * scoped output and the runtime opt-in switch.
 *
 * @deprecated Use `getSpeechLogger()`.
 */
// Tag was `ui-tools:speech` until that package was archived. Despite the
// deprecation note above this is what every engine and both mic hooks still
// call, so the old tag was on real production warnings, naming a package a
// reader could no longer find.
export const sttLogger = consola.withTag('speech');
