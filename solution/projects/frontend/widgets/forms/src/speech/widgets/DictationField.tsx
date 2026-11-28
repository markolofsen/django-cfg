'use client';

import type * as React from 'react';

import { cn } from '@djangocfg/ui-core/lib';

import { DictationButton } from '../components/DictationButton';
import { ErrorBanner } from '../components/ErrorBanner';
import { MicMeter } from '../components/MicMeter';
import { PushToTalkHint } from '../components/PushToTalkHint';
import { useDictation } from '../hooks/useDictation';
import { usePushToTalk } from '../hooks/usePushToTalk';
import type { RecognitionEngine } from '../types';

export interface DictationFieldProps {
  value: string;
  onChange: (next: string) => void;
  /** Custom engine. Defaults to Web Speech via `useSpeechRecognition`. */
  engine?: RecognitionEngine;
  /** Override the language stored in `useSpeechPrefs`. */
  language?: string;
  /** Push-to-talk chord (e.g. `'alt'`, `'mod+alt'`). Disabled when omitted. */
  pushToTalk?: { key: string; enabled?: boolean };
  placeholder?: string;
  rows?: number;
  disabled?: boolean;
  /** Show the interim transcript as a ghost overlay below the textarea. */
  showInterim?: boolean;
  /** Show a small RMS meter inside the toolbar. */
  showMeter?: boolean;
  className?: string;
  textareaClassName?: string;
}

/**
 * Opinionated textarea + dictation button assembly. Final segments are
 * appended to the controlled `value` automatically. Press-and-hold
 * shortcut is optional; the mic button itself works as a toggle.
 */
export function DictationField({
  value,
  onChange,
  engine,
  language,
  pushToTalk,
  placeholder = 'Type or press the mic to dictate…',
  rows = 3,
  disabled,
  showInterim = true,
  showMeter = true,
  className,
  textareaClassName,
}: DictationFieldProps): React.ReactElement {
  const rec = useDictation({
    value,
    onChange,
    engine,
    language,
  });

  usePushToTalk(rec, {
    key: pushToTalk?.key ?? 'alt',
    enabled: !!pushToTalk && pushToTalk.enabled !== false,
  });

  return (
    <div className={cn('flex flex-col gap-2', className)}>
      <div className="relative">
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          rows={rows}
          disabled={disabled}
          className={cn(
            'w-full resize-y rounded-md border border-input bg-background px-3 py-2 text-sm',
            'placeholder:text-muted-foreground',
            'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
            'disabled:cursor-not-allowed disabled:opacity-50',
            textareaClassName,
          )}
        />
        {showInterim && rec.transcript.interim && (
          <div className="pointer-events-none mt-1 text-xs italic text-muted-foreground">
            … {rec.transcript.interim}
          </div>
        )}
      </div>

      <div className="flex items-center gap-2">
        <DictationButton
          status={rec.status}
          isSupported={rec.isSupported}
          onClick={() => void rec.toggleDictation()}
          size="sm"
          disabled={disabled}
        />
        {showMeter && <MicMeter level={rec.level} bars={10} height={20} />}
        {pushToTalk && <PushToTalkHint chord={pushToTalk.key} className="ml-auto" />}
      </div>

      <ErrorBanner error={rec.error} />
    </div>
  );
}
