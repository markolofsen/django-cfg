'use client';

import { useCallback, useEffect, useMemo, useRef, useSyncExternalStore } from 'react';

import { createSoundBus, type SoundBus } from './createSoundBus';
import { useAudioPrefs } from './useAudioPrefs';

export interface NotificationSoundsConfig<E extends string> {
  /**
   * Persistence key for the mute / volume / per-event toggles. Use one
   * key per product surface (e.g. `'chat.audio'`, `'alerts.audio'`).
   */
  storageKey: string;
  /** Event → URL map. `false`/missing silences the event. */
  sounds?: Partial<Record<E, string | false>>;
  /** Master volume override. When set, the persisted value is ignored. */
  volume?: number;
  /**
   * Per-event volume multipliers (0..1). Final per-play volume is
   * `master × eventVolumes[event] ?? 1`. Use this to dim error / status
   * sounds so they don't feel jarring next to message dings. Slack /
   * Linear / Intercom-style defaults: error ≈ 0.25, mention ≈ 1.0,
   * received/sent ≈ 0.6.
   */
  eventVolumes?: Partial<Record<E, number>>;
  /** Master mute override. When set, the persisted value is ignored. */
  muted?: boolean;
  /** Custom predicate — return `false` to suppress one event. */
  shouldPlay?: (event: E) => boolean;
  /**
   * Skip all playback when the user prefers reduced motion. @default true
   */
  respectReducedMotion?: boolean;
  /**
   * Skip all playback when the user prefers reduced data. @default true
   */
  respectReducedData?: boolean;
  /**
   * Skip all playback when the tab is hidden. @default true
   */
  muteWhenHidden?: boolean;
  /**
   * Disable the hook entirely — bus is not created, prefs are not read,
   * `play()` is a no-op. Useful when the surrounding host plays sounds
   * itself (e.g. Electron / Wails backend) and the React layer should
   * stay silent.
   */
  silenced?: boolean;
  /**
   * Side-channel fired whenever `play()` would have triggered an event.
   * Stays active even when `silenced=true`. Use to bridge into a native
   * audio backend (cmdop_go, Tauri, …).
   */
  onSoundEvent?: (event: E) => void;
}

export interface NotificationSoundsApi<E extends string> {
  play: (event: E) => void;
  preload: (event: E) => void;
  unlock: () => void;
  isUnlocked: boolean;
  /** Resolved mute state — combines persisted prefs + reduced-motion + hidden. */
  muted: boolean;
  setMuted: (m: boolean) => void;
  toggleMute: () => void;
  volume: number;
  setVolume: (v: number) => void;
  isEventEnabled: (event: E) => boolean;
  setEventEnabled: (event: E, enabled: boolean) => void;
  /** True when no sounds map is configured (or `silenced`). */
  isSilent: boolean;
}

function readReducedMotion(): boolean {
  if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') return false;
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}
function readReducedData(): boolean {
  if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') return false;
  return window.matchMedia('(prefers-reduced-data: reduce)').matches;
}
function readVisibilityHidden(): boolean {
  if (typeof document === 'undefined') return false;
  return document.visibilityState === 'hidden';
}

/**
 * Mid-level notification-sounds hook.
 *
 * Use when you need a small named map (`received`, `error`, `mention`)
 * with persisted mute + Safari unlock + reduced-motion / hidden-tab
 * guards. Pair with `useAudioPrefs(...)` if you need cross-component
 * access to the same mute state.
 *
 * @example
 * ```tsx
 * type Event = 'received' | 'error';
 * const sounds = useNotificationSounds<Event>({
 *   storageKey: 'myapp.audio',
 *   sounds: { received: '/r.mp3', error: '/e.mp3' },
 * });
 *
 * onMessage = (m) => sounds.play('received');
 * onMute = () => sounds.toggleMute();
 * ```
 */
export function useNotificationSounds<E extends string>(
  config: NotificationSoundsConfig<E>,
): NotificationSoundsApi<E> {
  const {
    storageKey,
    sounds = {},
    volume: volumeOverride,
    eventVolumes,
    muted: mutedOverride,
    shouldPlay,
    respectReducedMotion = true,
    respectReducedData = true,
    muteWhenHidden = true,
    silenced = false,
    onSoundEvent,
  } = config;

  const usePrefs = useAudioPrefs<E>(storageKey);
  const volumeP = usePrefs((s) => s.volume);
  const mutedP = usePrefs((s) => s.muted);
  const enabledMap = usePrefs((s) => s.enabled);
  const setVolumeP = usePrefs((s) => s.setVolume);
  const setMutedP = usePrefs((s) => s.setMuted);
  const setEventEnabledP = usePrefs((s) => s.setEventEnabled);

  const volume = volumeOverride != null ? volumeOverride : volumeP;
  const muted = mutedOverride != null ? mutedOverride : mutedP;

  // Refs for stable getters inside the bus.
  const volumeRef = useRef(volume);
  volumeRef.current = volume;
  const eventVolumesRef = useRef(eventVolumes);
  eventVolumesRef.current = eventVolumes;
  const mutedRef = useRef(muted);
  mutedRef.current = muted;
  const enabledRef = useRef(enabledMap);
  enabledRef.current = enabledMap;
  const reducedMotionRef = useRef(readReducedMotion());
  const reducedDataRef = useRef(readReducedData());
  const hiddenRef = useRef(readVisibilityHidden());
  const shouldPlayRef = useRef(shouldPlay);
  shouldPlayRef.current = shouldPlay;
  const silencedRef = useRef(silenced);
  silencedRef.current = silenced;
  const onSoundEventRef = useRef(onSoundEvent);
  onSoundEventRef.current = onSoundEvent;

  // Watch reduced-motion / reduced-data preference changes.
  useEffect(() => {
    if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') return;
    const mqMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
    const mqData = window.matchMedia('(prefers-reduced-data: reduce)');
    const onMotion = () => {
      reducedMotionRef.current = mqMotion.matches;
    };
    const onData = () => {
      reducedDataRef.current = mqData.matches;
    };
    mqMotion.addEventListener('change', onMotion);
    mqData.addEventListener('change', onData);
    return () => {
      mqMotion.removeEventListener('change', onMotion);
      mqData.removeEventListener('change', onData);
    };
  }, []);

  // Visibility tracking — mute while tab is hidden.
  useEffect(() => {
    if (!muteWhenHidden || typeof document === 'undefined') return;
    const onVis = () => {
      hiddenRef.current = document.visibilityState === 'hidden';
    };
    document.addEventListener('visibilitychange', onVis);
    return () => document.removeEventListener('visibilitychange', onVis);
  }, [muteWhenHidden]);

  const effectiveMuted = useCallback((): boolean => {
    if (silencedRef.current) return true;
    if (mutedRef.current) return true;
    if (muteWhenHidden && hiddenRef.current) return true;
    if (respectReducedMotion && reducedMotionRef.current) return true;
    if (respectReducedData && reducedDataRef.current) return true;
    return false;
  }, [muteWhenHidden, respectReducedMotion, respectReducedData]);

  const isEnabledImpl = useCallback((event: E): boolean => {
    if (shouldPlayRef.current && shouldPlayRef.current(event) === false) return false;
    const flag = enabledRef.current[event];
    if (flag === false) return false;
    return true;
  }, []);

  // Bus instance — created once per hook lifetime, sounds map hot-swapped.
  const busRef = useRef<SoundBus<E> | null>(null);
  if (busRef.current === null) {
    busRef.current = createSoundBus<E>({
      sounds,
      getVolume: (event) => {
        const master = volumeRef.current;
        if (event === undefined) return master;
        const scale = eventVolumesRef.current?.[event];
        if (scale === undefined) return master;
        return master * scale;
      },
      getMuted: () => effectiveMuted(),
      isEnabled: (event) => isEnabledImpl(event),
    });
  }

  useEffect(() => {
    busRef.current?.setSounds(sounds);
  }, [sounds]);

  // Preload all listed sounds once.
  useEffect(() => {
    const bus = busRef.current;
    if (!bus) return;
    for (const ev of Object.keys(sounds) as E[]) bus.preload(ev);
  }, [sounds]);

  useEffect(() => {
    const bus = busRef.current;
    return () => bus?.dispose();
  }, []);

  const isUnlocked = useSyncExternalStore(
    useCallback((cb) => busRef.current?.subscribeUnlock(cb) ?? (() => undefined), []),
    () => busRef.current?.isUnlocked() ?? false,
    () => false,
  );

  const play = useCallback(
    (event: E) => {
      onSoundEventRef.current?.(event);
      busRef.current?.play(event);
    },
    [],
  );
  const preload = useCallback((event: E) => busRef.current?.preload(event), []);
  const unlock = useCallback(() => busRef.current?.unlock(), []);

  const toggleMute = useCallback(() => setMutedP(!mutedRef.current), [setMutedP]);

  const isEventEnabled = useCallback((event: E) => isEnabledImpl(event), [isEnabledImpl]);

  const isSilent = useMemo(() => {
    if (silenced) return true;
    return !sounds || Object.keys(sounds).length === 0;
  }, [silenced, sounds]);

  return {
    play,
    preload,
    unlock,
    isUnlocked,
    muted,
    setMuted: (m: boolean) => setMutedP(m),
    toggleMute,
    volume,
    setVolume: (v: number) => setVolumeP(v),
    isEventEnabled,
    setEventEnabled: (event, enabled) => setEventEnabledP(event, enabled),
    isSilent,
  };
}
