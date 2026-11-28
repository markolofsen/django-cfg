'use client';

import { useMemo } from 'react';

import { useBrowserDetect, useDeviceDetect } from '@djangocfg/ui-core/hooks';

import type { RecognitionEngine } from '../types';
import { createWebSpeechEngine } from '../core/engine/webspeech';

export type VoiceUnsupportedReason =
  | 'no-engine'
  | 'no-mediadevices'
  | 'in-app-browser'
  | 'unknown';

export interface VoiceSupport {
  /** Should the host render the voice button at all? */
  supported: boolean;
  /** Why is it off? `null` when supported. */
  reason: VoiceUnsupportedReason | null;
  /** Engine id that would be used if rendered (for badges / telemetry). */
  engineId: string | null;
  /** True on a mobile UA — useful for hiding on phones if the host wants. */
  isMobile: boolean;
  /** True inside Facebook / Instagram / TikTok / etc. in-app browsers. */
  isInApp: boolean;
}

/**
 * Decides whether the `<VoiceComposerSlot>` should render the mic
 * button. Three gates:
 *
 *  1. A `RecognitionEngine` reports `isSupported === true`. With no
 *     custom engine passed we probe `createWebSpeechEngine()` —
 *     Chrome / Edge / Safari pass, Firefox does not.
 *  2. `navigator.mediaDevices.getUserMedia` exists — but ONLY for an
 *     engine that captures through the browser. An engine declaring
 *     `usesMicrophone: false` owns capture elsewhere (native shell,
 *     sidecar), and `RecognitionEngine` states outright that consumers
 *     must not gate those on `getUserMedia`. This hook did anyway, and
 *     it ran the check FIRST, so in every environment that lacks the
 *     API — Wails WKWebView, a non-secure context, headless — the mic
 *     button was never rendered for an engine that works fine there.
 *     `useSpeechRecognition` already honours the flag; only the gate
 *     deciding whether the button exists did not.
 *  3. The host browser is not a known in-app WebView (Instagram,
 *     Facebook, TikTok, …) — mic permission flows are broken in most
 *     of them. The host can override this gate by passing a custom
 *     engine that already handles the case.
 */
export function useVoiceSupport(engine?: RecognitionEngine): VoiceSupport {
  const browser = useBrowserDetect();
  const device = useDeviceDetect();

  return useMemo<VoiceSupport>(() => {
    const isMobile = device.selectors.isMobile;
    const isInApp = browser.isInAppBrowser;

    // If the host didn't pass a custom engine we can only fall back to
    // the browser Web Speech API — bail when it's not available
    // (Firefox / some WebViews).
    const probe = engine ?? createWebSpeechEngine();

    // Checked after the probe, because the answer depends on which engine
    // this is. Omitted means `true`: the browser-native engines all open a
    // stream themselves.
    if (probe.usesMicrophone !== false) {
      const hasMediaDevices =
        typeof navigator !== 'undefined' && !!navigator.mediaDevices?.getUserMedia;
      if (!hasMediaDevices) {
        return { supported: false, reason: 'no-mediadevices', engineId: null, isMobile, isInApp };
      }
    }

    if (!probe.isSupported) {
      // In-app browsers are the most common reason a probe fails on
      // mobile; surface a friendlier code so the UI can hide silently.
      if (isInApp) {
        return { supported: false, reason: 'in-app-browser', engineId: null, isMobile, isInApp };
      }
      return { supported: false, reason: 'no-engine', engineId: null, isMobile, isInApp };
    }

    return {
      supported: true,
      reason: null,
      engineId: probe.id,
      isMobile,
      isInApp,
    };
  }, [engine, browser.isInAppBrowser, device.selectors.isMobile]);
}
