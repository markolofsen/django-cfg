'use client';

import type * as React from 'react';
import { useEffect } from 'react';

import { cn } from '@djangocfg/ui-core/lib';

import { DictationButton } from '../components/DictationButton';
import { ErrorBanner } from '../components/ErrorBanner';
import { MicMeter } from '../components/MicMeter';
import { TranscriptView } from '../components/TranscriptView';
import { useSpeechRecognition } from '../hooks/useSpeechRecognition';
import type { RecognitionEngine, Segment } from '../types';

export interface VoiceMessageRecorderProps {
  /** Called once when the user stops, with the full final transcript. */
  onSubmit: (text: string, segments: Segment[]) => void;
  onCancel?: () => void;
  engine?: RecognitionEngine;
  language?: string;
  /** Auto-stop after this many ms of silence. Default 1500. */
  silenceMs?: number;
  /** Hard cap on session length. Default 60000 ms. */
  maxMs?: number;
  className?: string;
}

/**
 * Press-to-record assembly for "voice memo" UIs. Records until the user
 * presses stop or silence-detection fires, then emits the full final
 * transcript via `onSubmit`. Pair with a chat composer or any send-button
 * flow.
 */
export function VoiceMessageRecorder({
  onSubmit,
  onCancel,
  engine,
  language,
  silenceMs = 1500,
  maxMs = 60000,
  className,
}: VoiceMessageRecorderProps): React.ReactElement {
  const rec = useSpeechRecognition({
    engine,
    language,
    autoStop: { silenceMs, maxMs },
  });

  // Auto-submit on transition out of listening — fires once the engine
  // finalises and closes. Reducer resets after.
  useEffect(() => {
    if (rec.status !== 'idle') return;
    if (!rec.transcript.final) return;
    onSubmit(rec.transcript.final, rec.transcript.segments);
    rec.reset();
    // The individual members, not `rec`: `useSpeechRecognition` returns a fresh
    // object literal every render, so depending on it would re-run this effect
    // continuously and re-submit the same transcript.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [rec.status, rec.transcript.final, rec.transcript.segments, onSubmit, rec.reset]);

  return (
    <div
      className={cn(
        'flex w-full flex-col gap-3 rounded-lg border border-border bg-card p-3',
        className,
      )}
    >
      <div className="flex items-center gap-3">
        <DictationButton
          status={rec.status}
          isSupported={rec.isSupported}
          onClick={() => void rec.toggle()}
          size="lg"
        />
        <MicMeter level={rec.level} bars={14} height={28} className="flex-1" />
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="rounded-md border border-border px-2 py-1 text-xs text-muted-foreground hover:bg-muted"
          >
            Cancel
          </button>
        )}
      </div>
      <TranscriptView transcript={rec.transcript} />
      <ErrorBanner error={rec.error} />
    </div>
  );
}
