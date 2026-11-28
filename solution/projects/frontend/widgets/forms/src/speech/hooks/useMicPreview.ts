'use client';

import { useEffect, useState } from 'react';

import { sttLogger } from '../core/logger';

/**
 * Short-lived microphone preview stream for the voice control menu.
 *
 * While `active` is true, opens a `getUserMedia` audio stream on the
 * requested device so the menu can show a LIVE level meter — the
 * instant "is my mic working?" check (claude.ai's mic popover does the
 * same). The stream is stopped the moment `active` flips false or the
 * device changes, so the mic indicator in the browser tab never
 * lingers after the menu closes.
 *
 * Returns `null` while inactive, before permission resolves, or when
 * capture fails (permission denied / no device) — consumers render the
 * meter flat at zero in that case.
 */
export function useMicPreview(
  active: boolean,
  deviceId: string | null,
): MediaStream | null {
  const [stream, setStream] = useState<MediaStream | null>(null);

  useEffect(() => {
    if (!active) {
      setStream(null);
      return undefined;
    }
    if (typeof navigator === 'undefined' || !navigator.mediaDevices?.getUserMedia) {
      return undefined;
    }
    let cancelled = false;
    let opened: MediaStream | null = null;

    const constraints: MediaStreamConstraints = {
      audio: deviceId ? { deviceId: { exact: deviceId } } : true,
    };
    navigator.mediaDevices
      .getUserMedia(constraints)
      .then((s) => {
        if (cancelled) {
          s.getTracks().forEach((t) => t.stop());
          return;
        }
        opened = s;
        setStream(s);
      })
      .catch((cause) => {
        sttLogger.warn('[mic-preview] getUserMedia failed', cause);
      });

    return () => {
      cancelled = true;
      opened?.getTracks().forEach((t) => t.stop());
      setStream(null);
    };
  }, [active, deviceId]);

  return stream;
}
