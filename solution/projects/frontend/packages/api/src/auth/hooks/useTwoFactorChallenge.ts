'use client';

import { useSyncExternalStore } from 'react';

/** A pending login that needs a TOTP or backup code before tokens are issued. */
export interface TwoFactorChallenge {
  sessionId: string;
}

// Module-scoped on purpose: one sign-in is in flight per page, and the sign-in
// form and the challenge dialog share it without either importing the other.
let current: TwoFactorChallenge | null = null;
const listeners = new Set<() => void>();

const set = (next: TwoFactorChallenge | null): void => {
  current = next;
  for (const listener of [...listeners]) listener();
};

const subscribe = (listener: () => void): (() => void) => {
  listeners.add(listener);
  return () => {
    listeners.delete(listener);
  };
};

/** Called by whichever step received `requires_2fa` (OTP, password, OAuth callback). */
export const beginTwoFactorChallenge = (challenge: TwoFactorChallenge): void => set(challenge);

/** Called when the challenge is verified or abandoned. */
export const endTwoFactorChallenge = (): void => set(null);

/** The pending challenge, or null. */
export const useTwoFactorChallenge = (): TwoFactorChallenge | null =>
  useSyncExternalStore(subscribe, () => current, () => null);
