'use client';

import { useEffect, useRef } from 'react';

export interface UseHotkeyChordOptions {
  /** Whether the chord is active. @default true */
  enabled?: boolean;
  /** Max delay between consecutive keys, in ms. @default 800 */
  window?: number;
  /**
   * Fire even when focus is inside an input / textarea / contenteditable.
   * @default false — chord sequences shouldn't hijack typing
   */
  enableOnFormTags?: boolean;
  /** Prevent default browser behaviour on each key. @default false */
  preventDefault?: boolean;
}

const FORM_TAGS = new Set(['INPUT', 'TEXTAREA', 'SELECT']);

function isEditableTarget(el: EventTarget | null): boolean {
  if (!(el instanceof HTMLElement)) return false;
  if (FORM_TAGS.has(el.tagName)) return true;
  if (el.isContentEditable) return true;
  return false;
}

/**
 * Linear-style chord shortcuts — fire `callback` when the user presses
 * a sequence of bare keys within a time window.
 *
 * @example
 * ```tsx
 * useHotkeyChord(['g', 't'], () => navigate('/tasks'));
 * useHotkeyChord(['g', 'i'], () => navigate('/inbox'), { window: 1200 });
 * ```
 *
 * Each step is a single bare key (no modifiers). Pressing any
 * non-sequence key resets progress, so partially-typed sequences don't
 * fire accidentally.
 */
export function useHotkeyChord(
  keys: readonly string[],
  callback: (event: KeyboardEvent) => void,
  options: UseHotkeyChordOptions = {},
): void {
  const { enabled = true, window: chordWindow = 800, enableOnFormTags = false, preventDefault = false } = options;
  const callbackRef = useRef(callback);
  callbackRef.current = callback;

  // The listener is rebound on the chord's CONTENTS, not the array's identity:
  // callers write `useHotkeyChord(['g', 't'], …)` with a fresh literal each
  // render, which would otherwise tear down and re-add the keydown listener
  // continuously and reset any chord in progress.
  const keysKey = keys.join('|');
  const keysRef = useRef(keys);
  keysRef.current = keys;

  useEffect(() => {
    if (!enabled) return;
    if (typeof window === 'undefined') return;
    const sequence = keysRef.current.map((k) => k.toLowerCase());
    if (!sequence.length) return;
    let progress = 0;
    let timer: ReturnType<typeof setTimeout> | null = null;

    const reset = () => {
      progress = 0;
      if (timer) {
        clearTimeout(timer);
        timer = null;
      }
    };

    const onKey = (e: KeyboardEvent) => {
      if (!enableOnFormTags && isEditableTarget(e.target)) return;
      // Chords don't carry modifiers.
      if (e.metaKey || e.ctrlKey || e.altKey) return reset();

      const expected = sequence[progress];
      if (!expected) return;
      const pressed = e.key.toLowerCase();
      if (pressed !== expected) return reset();

      if (preventDefault) e.preventDefault();
      progress++;
      if (progress >= sequence.length) {
        callbackRef.current(e);
        reset();
        return;
      }

      if (timer) clearTimeout(timer);
      timer = setTimeout(reset, chordWindow);
    };

    window.addEventListener('keydown', onKey);
    return () => {
      window.removeEventListener('keydown', onKey);
      if (timer) clearTimeout(timer);
    };
  }, [keysKey, enabled, chordWindow, enableOnFormTags, preventDefault]);
}
