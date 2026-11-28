'use client';

import { useEffect, useRef } from 'react';

import { normaliseFinal } from '../core/transcript';
import type { UseSpeechRecognitionConfig, UseSpeechRecognitionReturn } from '../types';
import { useSpeechRecognition } from './useSpeechRecognition';

export interface UseDictationConfig
  extends Omit<UseSpeechRecognitionConfig, 'onFinal'> {
  /** Controlled value the dictation is appending to. */
  value: string;
  /** Called with the next value after each final segment lands. */
  onChange: (next: string) => void;
  /** Joiner between the previous value and the new segment. Default ' '. */
  separator?: string;
}

export interface UseDictationReturn extends UseSpeechRecognitionReturn {
  /** Convenience — same as `toggle`, named for dictation UIs. */
  toggleDictation: () => Promise<void>;
}

/**
 * Convenience adapter that pipes final transcript segments straight into
 * a controlled string (`<textarea>` / `<input>` / TipTap). Interim text
 * is left alone — bind `transcript.interim` separately if you want to
 * show a live ghost.
 */
export function useDictation(config: UseDictationConfig): UseDictationReturn {
  const { value, onChange, separator = ' ', ...rest } = config;

  // Stash latest value in a ref so the onFinal closure always sees the
  // freshest text without forcing the underlying hook to resubscribe.
  const valueRef = useRef(value);
  valueRef.current = value;
  const onChangeRef = useRef(onChange);
  onChangeRef.current = onChange;

  const rec = useSpeechRecognition({
    ...rest,
    onFinal: (text) => {
      const clean = normaliseFinal(text);
      if (!clean) return;
      const prev = valueRef.current;
      const next = prev ? `${prev}${separator}${clean}` : clean;
      onChangeRef.current(next);
    },
  });

  useEffect(() => {
    valueRef.current = value;
  }, [value]);

  return {
    ...rec,
    toggleDictation: rec.toggle,
  };
}
