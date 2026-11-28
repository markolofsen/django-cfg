import { useSyncExternalStore } from 'react';

/**
 * A prompt typed outside the assistant (the header's AI mode) waiting for the composer. The composer, once mounted, puts it in the draft and
 * sends it, then clears it. One slot: asking twice before the composer exists keeps the last.
 */
let pending: string | null = null;
const listeners = new Set<() => void>();
const emit = () => listeners.forEach((listener) => listener());

export function askAssistant(text: string): void {
  pending = text.trim() || null;
  emit();
}

export function clearPendingPrompt(): void {
  pending = null;
  emit();
}

const subscribe = (listener: () => void) => {
  listeners.add(listener);
  return () => void listeners.delete(listener);
};

export const usePendingPrompt = (): string | null => useSyncExternalStore(subscribe, () => pending, () => null);
