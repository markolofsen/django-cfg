'use client';

import { useCallback, useEffect, useRef } from 'react';

export interface SoundEffectOptions {
  /** 0..1 master volume. @default 1 */
  volume?: number;
  /** Set to true to skip play() entirely (e.g. user-prefs gating). @default false */
  silenced?: boolean;
}

export interface SoundEffectApi {
  /** Trigger playback. Fire-and-forget; cancel-safe. */
  play: () => void;
  /** Eagerly preload the asset. */
  preload: () => void;
}

/**
 * One-shot single-asset hook — the minimal "play a ding" helper.
 *
 * Lower level than `useNotificationSounds` (no persisted mute, no
 * per-event toggles). Use when you have ONE asset, ONE trigger, and
 * don't need cross-component sync.
 *
 * @example
 * ```tsx
 * const submitDing = useSoundEffect('/sfx/ding.mp3');
 * <Button onClick={() => { submitDing.play(); doStuff(); }} />
 * ```
 */
export function useSoundEffect(
  url: string | null | undefined,
  options: SoundEffectOptions = {},
): SoundEffectApi {
  const { volume = 1, silenced = false } = options;
  const templateRef = useRef<HTMLAudioElement | null>(null);
  const volumeRef = useRef(volume);
  volumeRef.current = volume;
  const silencedRef = useRef(silenced);
  silencedRef.current = silenced;
  const urlRef = useRef(url);
  urlRef.current = url;

  useEffect(() => {
    if (typeof window === 'undefined' || !url) return;
    const el = new Audio(url);
    el.preload = 'auto';
    el.crossOrigin = 'anonymous';
    templateRef.current = el;
    return () => {
      templateRef.current = null;
    };
  }, [url]);

  const play = useCallback(() => {
    if (silencedRef.current) return;
    const u = urlRef.current;
    if (!u || typeof window === 'undefined') return;
    const fresh = new Audio(u);
    fresh.preload = 'auto';
    fresh.volume = volumeRef.current;
    const p = fresh.play();
    if (p && typeof p.catch === 'function') p.catch(() => undefined);
  }, []);

  const preload = useCallback(() => {
    const el = templateRef.current;
    if (!el) return;
    try {
      el.load();
    } catch {
      // ignore
    }
  }, []);

  return { play, preload };
}
