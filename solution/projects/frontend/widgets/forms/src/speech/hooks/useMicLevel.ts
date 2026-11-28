'use client';

import { useEffect, useRef, useState } from 'react';

/**
 * RMS level meter driven by an `AnalyserNode`. Attach a `MediaStream`
 * (the one returned from `startMicCapture`) and read `level` (0..1) for
 * VU meters / mic-pulse animations. Returns 0 when no stream is bound.
 */
export function useMicLevel(stream: MediaStream | null): number {
  const [level, setLevel] = useState(0);
  const raf = useRef<number | null>(null);

  useEffect(() => {
    if (!stream) {
      setLevel(0);
      return undefined;
    }
    const AC =
      (window as unknown as { AudioContext?: typeof AudioContext }).AudioContext ??
      (window as unknown as { webkitAudioContext?: typeof AudioContext }).webkitAudioContext;
    if (!AC) return undefined;
    const ctx = new AC();
    const source = ctx.createMediaStreamSource(stream);
    const analyser = ctx.createAnalyser();
    analyser.fftSize = 1024;
    analyser.smoothingTimeConstant = 0.7;
    source.connect(analyser);
    const buf = new Float32Array(analyser.fftSize);

    const tick = (): void => {
      analyser.getFloatTimeDomainData(buf);
      let sum = 0;
      for (let i = 0; i < buf.length; i += 1) sum += buf[i]! * buf[i]!;
      const rms = Math.sqrt(sum / buf.length);
      // soft compression so loud peaks don't dominate the meter
      setLevel(Math.min(1, rms * 2.5));
      raf.current = requestAnimationFrame(tick);
    };
    tick();

    return () => {
      if (raf.current != null) cancelAnimationFrame(raf.current);
      raf.current = null;
      source.disconnect();
      analyser.disconnect();
      void ctx.close();
    };
  }, [stream]);

  return level;
}
