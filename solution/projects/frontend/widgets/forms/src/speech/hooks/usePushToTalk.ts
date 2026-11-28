'use client';

import { useEffect, useRef } from 'react';

import type { UseSpeechRecognitionReturn } from '../types';

export interface UsePushToTalkOptions {
  /** Key to hold. Combine modifiers with `+`, e.g. `'alt'`, `'mod+alt'`. */
  key: string;
  /** Disable the binding without unmounting. */
  enabled?: boolean;
}

const MOD_KEYS = new Set(['shift', 'ctrl', 'alt', 'meta', 'mod']);

/** `mod` resolves to ⌘ on Apple platforms, Ctrl elsewhere. */
function isApplePlatform(): boolean {
  if (typeof navigator === 'undefined') return false;
  const p =
    (navigator as { userAgentData?: { platform?: string } }).userAgentData
      ?.platform ?? navigator.platform;
  return /mac|iphone|ipad|ipod/i.test(p ?? '');
}

function parseChord(chord: string): { mods: Set<string>; main: string | null } {
  const parts = chord
    .toLowerCase()
    .split('+')
    .map((s) => s.trim());
  const modAlias = isApplePlatform() ? 'meta' : 'ctrl';
  const mods = new Set<string>();
  let main: string | null = null;
  for (const part of parts) {
    if (MOD_KEYS.has(part)) {
      mods.add(part === 'mod' ? modAlias : part);
    } else if (part) {
      main = part;
    }
  }
  return { mods, main };
}

function matches(e: KeyboardEvent, mods: Set<string>, main: string | null): boolean {
  if (mods.has('shift') !== e.shiftKey) return false;
  if (mods.has('ctrl') !== e.ctrlKey) return false;
  if (mods.has('alt') !== e.altKey) return false;
  if (mods.has('meta') !== e.metaKey) return false;
  if (main && e.key.toLowerCase() !== main) return false;
  return true;
}

/**
 * Key-up matcher — modifier state is unreliable on `keyup` (releasing
 * the modifier itself drops the flag before the main key's keyup), so
 * we only check the main key here. Pure-modifier chords match when the
 * released key is one of the chord's modifiers.
 */
function matchesRelease(
  e: KeyboardEvent,
  mods: Set<string>,
  main: string | null,
): boolean {
  const key = e.key.toLowerCase();
  if (main) return key === main;
  // Pure-modifier chord: stop when any chord modifier is released.
  return (
    (mods.has('shift') && key === 'shift') ||
    (mods.has('ctrl') && key === 'control') ||
    (mods.has('alt') && key === 'alt') ||
    (mods.has('meta') && key === 'meta')
  );
}

/**
 * Hold-to-talk wiring. Press → `start()`, release → `stop()`. Ignores
 * repeats and skips keydown inside `<input>` / `<textarea>` unless a
 * modifier is in the chord.
 */
export function usePushToTalk(
  recognition: Pick<UseSpeechRecognitionReturn, 'start' | 'stop' | 'status'>,
  opts: UsePushToTalkOptions,
): void {
  const { key, enabled = true } = opts;

  // The caller's `recognition` is a fresh object every render, and `level`
  // inside it updates ~60x/s while the mic is live. Depending on it directly
  // would tear down and re-add the window listeners every frame, dropping any
  // keypress that lands in the gap. The ref keeps the handlers current without
  // making the effect re-run.
  const recognitionRef = useRef(recognition);
  useEffect(() => {
    recognitionRef.current = recognition;
  });

  useEffect(() => {
    if (!enabled || typeof window === 'undefined') return undefined;
    const { mods, main } = parseChord(key);

    const onDown = (e: KeyboardEvent): void => {
      if (e.repeat) return;
      if (!main && mods.size === 0) return;
      const target = e.target as HTMLElement | null;
      const inField =
        target?.tagName === 'INPUT' ||
        target?.tagName === 'TEXTAREA' ||
        target?.isContentEditable;
      if (inField && mods.size === 0) return;
      if (!matches(e, mods, main)) return;
      const rec = recognitionRef.current;
      if (rec.status === 'listening' || rec.status === 'starting') return;
      e.preventDefault();
      void rec.start();
    };
    const onUp = (e: KeyboardEvent): void => {
      if (!matchesRelease(e, mods, main)) return;
      const rec = recognitionRef.current;
      if (rec.status !== 'listening' && rec.status !== 'starting') return;
      void rec.stop();
    };

    window.addEventListener('keydown', onDown);
    window.addEventListener('keyup', onUp);
    return () => {
      window.removeEventListener('keydown', onDown);
      window.removeEventListener('keyup', onUp);
    };
  }, [enabled, key]);
}
