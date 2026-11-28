'use client';

import type * as React from 'react';
import { createContext, useContext, useMemo } from 'react';

import type { UseSpeechRecognitionConfig, UseSpeechRecognitionReturn } from '../types';
import { useSpeechRecognition } from '../hooks/useSpeechRecognition';

const Ctx = createContext<UseSpeechRecognitionReturn | null>(null);

export interface SpeechRecognitionProviderProps extends UseSpeechRecognitionConfig {
  children?: React.ReactNode;
}

/**
 * Lifts a single `useSpeechRecognition` instance into a context so any
 * descendant — composer slot, header badge, transcript overlay — can
 * read the same status / transcript / level without each component
 * spinning up its own engine. Mount it once per Chat (or per
 * dictation-aware screen).
 */
export function SpeechRecognitionProvider({
  children,
  ...config
}: SpeechRecognitionProviderProps): React.ReactElement {
  const rec = useSpeechRecognition(config);
  // Memo prevents context-value churn from leaking through to every
  // useContext consumer when only one of {status, level, transcript}
  // changes — React already triggers them via the inner state, the
  // outer object identity should stay stable across renders.
  const value = useMemo(() => rec, [rec]);
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useSpeechRecognitionContext(): UseSpeechRecognitionReturn {
  const ctx = useContext(Ctx);
  if (!ctx) {
    throw new Error(
      'useSpeechRecognitionContext must be used inside a <SpeechRecognitionProvider>.',
    );
  }
  return ctx;
}

export function useSpeechRecognitionContextOptional(): UseSpeechRecognitionReturn | null {
  return useContext(Ctx);
}
