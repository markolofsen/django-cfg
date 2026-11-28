'use client';

import { useSyncExternalStore } from 'react';

const noopSubscribe = () => () => {};

/**
 * Apple platforms use Meta (⌘) for “primary” shortcuts; Windows/Linux use Ctrl.
 * Matches typical `event.metaKey || event.ctrlKey` handling in app hotkeys.
 */
function isAppleLikeClient(): boolean {
  if (typeof navigator === 'undefined') return false;
  const ua = navigator.userAgent;
  if (/Mac|iPhone|iPad|iPod/i.test(ua)) return true;
  // iPadOS 13+ may report as MacIntel with touch
  if (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1) return true;
  return false;
}

/**
 * Modifier label for shortcut hints (e.g. tooltips): `⌘` on Apple, `Ctrl` elsewhere.
 * SSR / first server snapshot returns `Ctrl` to match `getServerSnapshot`.
 */
export function useShortcutModLabel(): '⌘' | 'Ctrl' {
  return useSyncExternalStore(noopSubscribe, () => (isAppleLikeClient() ? '⌘' : 'Ctrl'), () => 'Ctrl');
}
