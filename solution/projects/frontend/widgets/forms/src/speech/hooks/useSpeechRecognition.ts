'use client';

import { useCallback, useEffect, useMemo, useReducer, useRef, useState } from 'react';

import {
  EMPTY_TRANSCRIPT,
  INITIAL_STATE,
  buildTranscript,
  getSpeechLogger,
  reducer,
} from '../core';

const log = getSpeechLogger();
import { createWebSpeechEngine } from '../core/engine/webspeech';
import { useSpeechPrefs } from '../store/prefsStore';
import type {
  RecognitionEngine,
  Segment,
  UseSpeechRecognitionConfig,
  UseSpeechRecognitionReturn,
} from '../types';
import { useMicLevel } from './useMicLevel';
import { useResolvedLanguage } from './useResolvedLanguage';

/**
 * Main entry point. With no config it uses the browser Web Speech API
 * and the persisted language from `useSpeechPrefs`. Pass a custom
 * `engine` to route through Deepgram / Whisper / custom WebSocket.
 */
export function useSpeechRecognition(
  config: UseSpeechRecognitionConfig = {},
): UseSpeechRecognitionReturn {
  const prefs = useSpeechPrefs();
  const language = useResolvedLanguage(config.language);
  const engine = useMemo<RecognitionEngine>(
    () => config.engine ?? createWebSpeechEngine(),
    [config.engine],
  );

  const [state, dispatch] = useReducer(reducer, INITIAL_STATE);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const level = useMicLevel(stream);

  // Latest-callback refs so engine subscriptions never tear down on
  // every render — same trick the Chat reducer uses.
  const cbRef = useRef(config);
  cbRef.current = config;

  // Engine subscription lifecycle.
  useEffect(() => {
    log.engine.debug('subscribe', { engineId: engine.id });
    const offs = [
      engine.on('partial', (text, segmentId) => {
        log.engine.debug('partial', { len: text.length, segmentId });
        dispatch({ type: 'PARTIAL', text, segmentId });
        const seg: Segment = {
          id: segmentId,
          text,
          isFinal: false,
          startedAt: Date.now(),
        };
        cbRef.current.onPartial?.(text, seg);
      }),
      engine.on('final', (text, segmentId, confidence) => {
        log.engine.info('final', {
          len: text.length,
          segmentId,
          confidence,
        });
        dispatch({ type: 'FINAL', text, segmentId, confidence });
        const seg: Segment = {
          id: segmentId,
          text,
          isFinal: true,
          confidence,
          startedAt: Date.now(),
          endedAt: Date.now(),
        };
        cbRef.current.onFinal?.(text, seg);
      }),
      engine.on('error', (err) => {
        log.error.error('engine error', err);
        dispatch({ type: 'ERROR', error: err });
        cbRef.current.onError?.(err);
      }),
      engine.on('state', (s) => {
        log.engine.debug('state', s);
        if (s === 'listening') {
          dispatch({ type: 'STARTED' });
          cbRef.current.onStart?.();
          setStream(engine.getStream?.() ?? null);
        } else if (s === 'closed') {
          dispatch({ type: 'STOPPED' });
          cbRef.current.onStop?.();
          setStream(null);
        }
      }),
    ];
    return () => {
      offs.forEach((off) => off());
      // Release the mic / socket if the consumer unmounts (or swaps
      // the engine) mid-session. Without this the MediaRecorder and
      // getUserMedia stream keep running headless after unmount.
      engine.abort();
    };
  }, [engine]);

  // METER MONITOR STREAM. The Web Speech engine owns its microphone
  // capture internally and exposes NO MediaStream — without this,
  // `level` sits at 0 for the entire session: the wave meter stays a
  // flat dotted line and the silence auto-stop measures zeros (owner
  // report 2026-08-03). While listening, if the engine didn't hand us
  // its stream, open a parallel monitor stream purely for metering —
  // permission is already granted, Chrome allows both captures at
  // once. Engines that DO expose their stream (HTTP/WS) skip this.
  useEffect(() => {
    if (state.status !== 'listening') return undefined;
    if (engine.getStream?.()) return undefined;
    // External engines capture OUTSIDE the browser — a browser-side
    // monitor stream would meter the wrong (or no) microphone.
    if (engine.usesMicrophone === false) return undefined;
    if (typeof navigator === 'undefined' || !navigator.mediaDevices?.getUserMedia) {
      return undefined;
    }
    let cancelled = false;
    let opened: MediaStream | null = null;
    const deviceId =
      cbRef.current.deviceId ?? useSpeechPrefs.getState().deviceId ?? undefined;
    navigator.mediaDevices
      .getUserMedia({
        audio: deviceId ? { deviceId: { exact: deviceId } } : true,
      })
      .then((s) => {
        if (cancelled) {
          s.getTracks().forEach((t) => t.stop());
          return;
        }
        opened = s;
        setStream(s);
      })
      .catch((cause) => {
        log.engine.warn('meter monitor getUserMedia failed', cause);
      });
    return () => {
      cancelled = true;
      opened?.getTracks().forEach((t) => t.stop());
      setStream(null);
    };
  }, [state.status, engine]);

  // AutoStop driven by silence + maxMs caps. `level` updates ~60fps,
  // so it must NOT live in the effect deps — otherwise the silence
  // interval is torn down and recreated every animation frame, which
  // both wastes CPU and resets the silence timer before it can fire.
  // The interval reads the freshest level through a ref instead.
  const silenceTimer = useRef<number | null>(null);
  const maxTimer = useRef<number | null>(null);
  const levelRef = useRef(level);
  levelRef.current = level;
  useEffect(() => {
    if (state.status !== 'listening') return undefined;
    const { silenceMs, maxMs, silenceThreshold = 0.02 } = config.autoStop ?? {};
    if (maxMs) {
      maxTimer.current = window.setTimeout(() => {
        log.engine.debug('autoStop max duration hit');
        void engine.stop();
      }, maxMs);
    }
    let checkInterval: number | null = null;
    if (silenceMs) {
      checkInterval = window.setInterval(() => {
        if (levelRef.current < silenceThreshold) {
          if (silenceTimer.current == null) {
            silenceTimer.current = window.setTimeout(() => {
              log.engine.debug('autoStop silence detected');
              void engine.stop();
            }, silenceMs);
          }
        } else if (silenceTimer.current != null) {
          clearTimeout(silenceTimer.current);
          silenceTimer.current = null;
        }
      }, 200);
    }
    return () => {
      if (checkInterval != null) clearInterval(checkInterval);
      if (silenceTimer.current != null) clearTimeout(silenceTimer.current);
      silenceTimer.current = null;
      if (maxTimer.current != null) clearTimeout(maxTimer.current);
      maxTimer.current = null;
    };
  }, [state.status, config.autoStop, engine]);

  // Watchdog for the transient states. `starting` and `stopping` are
  // driven OUT only by an engine callback (`listening` / `closed`). The
  // browser Web Speech API does not guarantee those fire: a fast
  // press→release can leave the recognizer settling with no `onstart`
  // and no `onend`, and some WebViews drop the terminal event entirely.
  // When that happens the UI hangs in the transient state forever — the
  // reported "mic spinner never stops, next tap does nothing". Force the
  // engine to abort and snap back to `idle` if the transient state
  // outlives a generous timeout, so the control is always recoverable.
  //   starting: engine start can legitimately take ~1s (permission,
  //             warm-up) → 8s ceiling.
  //   stopping: the final-result tail is short → 4s ceiling.
  useEffect(() => {
    if (state.status !== 'starting' && state.status !== 'stopping') {
      return undefined;
    }
    const ceilingMs = state.status === 'starting' ? 8000 : 4000;
    const timer = window.setTimeout(() => {
      log.engine.warn(`watchdog: stuck in '${state.status}' — forcing idle`);
      engine.abort();
      dispatch({ type: 'ABORT' });
    }, ceilingMs);
    return () => window.clearTimeout(timer);
  }, [state.status, engine]);

  const start = useCallback(async () => {
    if (state.status === 'listening' || state.status === 'starting') return;
    dispatch({ type: 'START' });
    try {
      await engine.start({
        language,
        interim: config.interim ?? true,
        deviceId: config.deviceId ?? prefs.deviceId ?? undefined,
      });
    } catch (cause) {
      // engine already emitted 'error'; reducer caught it via subscription
      log.engine.warn('start threw', cause);
    }
  }, [engine, language, config.interim, config.deviceId, prefs.deviceId, state.status]);

  const stop = useCallback(async () => {
    if (state.status === 'idle' || state.status === 'stopping') return;
    dispatch({ type: 'STOP' });
    await engine.stop();
  }, [engine, state.status]);

  const abort = useCallback(() => {
    engine.abort();
    dispatch({ type: 'ABORT' });
  }, [engine]);

  const toggle = useCallback(async () => {
    if (state.status === 'listening' || state.status === 'starting') {
      await stop();
    } else {
      await start();
    }
  }, [state.status, start, stop]);

  const reset = useCallback(() => {
    dispatch({ type: 'RESET' });
  }, []);

  const transcript = useMemo(
    () => (state.segments.length === 0 ? EMPTY_TRANSCRIPT : buildTranscript(state.segments)),
    [state.segments],
  );

  return {
    status: state.status,
    isSupported: engine.isSupported,
    transcript,
    error: state.error,
    level,
    start,
    stop,
    abort,
    toggle,
    reset,
  };
}
