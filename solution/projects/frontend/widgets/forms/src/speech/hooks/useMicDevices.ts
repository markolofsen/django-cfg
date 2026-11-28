'use client';

import { useEffect, useState } from 'react';

import { sttLogger } from '../core/logger';

export interface MicDevice {
  deviceId: string;
  label: string;
  groupId: string;
}

/**
 * Enumerates `audioinput` devices. The browser hides labels until the
 * page has been granted mic permission at least once — the consumer
 * should call `useSpeechRecognition().start()` first to populate labels.
 */
export function useMicDevices(): {
  devices: MicDevice[];
  refresh: () => Promise<void>;
} {
  const [devices, setDevices] = useState<MicDevice[]>([]);

  async function refresh(): Promise<void> {
    if (typeof navigator === 'undefined' || !navigator.mediaDevices?.enumerateDevices) {
      return;
    }
    try {
      const list = await navigator.mediaDevices.enumerateDevices();
      setDevices(
        list
          .filter((d) => d.kind === 'audioinput')
          .map((d) => ({
            deviceId: d.deviceId,
            label: d.label || 'Microphone',
            groupId: d.groupId,
          })),
      );
    } catch (cause) {
      sttLogger.warn('[devices] enumerate failed', cause);
    }
  }

  useEffect(() => {
    void refresh();
    if (typeof navigator === 'undefined' || !navigator.mediaDevices) return undefined;
    const handler = (): void => {
      void refresh();
    };
    navigator.mediaDevices.addEventListener?.('devicechange', handler);
    return () => {
      navigator.mediaDevices.removeEventListener?.('devicechange', handler);
    };
  }, []);

  return { devices, refresh };
}
