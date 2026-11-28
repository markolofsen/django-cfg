// Adapted from jalcoui (MIT) — github.com/jal-co/ui

'use client';

import * as React from 'react';
import { cn } from '@djangocfg/ui-core/lib';
import type { LogEntry } from '../types';
import { LEVEL_LABELS, getLevelToneClasses } from '../types';
import { parseAnsi, classesForSegment, stripAnsi } from '../utils/ansi';

function formatTimestamp(ts?: string): string {
  const d = ts ? new Date(ts) : new Date();
  const ms = d.getMilliseconds().toString().padStart(3, '0');
  return `${d.toLocaleTimeString('en-US', {
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })}.${ms}`;
}

/** Escape a string for use inside a `RegExp` constructor. */
function escapeRegex(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

interface MessageBodyProps {
  message: string;
  ansi: boolean;
  searchQuery: string;
}

/**
 * Render the message body. The render is staged in two passes:
 *
 * 1. ANSI parse — produces styled segments. When `ansi` is `false` the
 *    raw message becomes one segment.
 * 2. Search highlight — splits each segment's text on the search needle
 *    and wraps matches in `<mark>` while preserving the segment's tone
 *    classes.
 *
 * The two passes run independently so a needle that crosses an ANSI
 * boundary still highlights inside each segment.
 */
const MessageBody = React.memo(function MessageBody({
  message,
  ansi,
  searchQuery,
}: MessageBodyProps) {
  const segments = React.useMemo(
    () => (ansi ? parseAnsi(message) : [{ text: ansi ? message : stripAnsi(message) }]),
    [message, ansi],
  );

  const needle = searchQuery.trim();
  if (!needle) {
    return (
      <>
        {segments.map((seg, i) => (
          <span key={i} className={classesForSegment(seg)}>
            {seg.text}
          </span>
        ))}
      </>
    );
  }

  const re = new RegExp(`(${escapeRegex(needle)})`, 'gi');
  return (
    <>
      {segments.map((seg, i) => {
        const classes = classesForSegment(seg);
        const parts = seg.text.split(re);
        return (
          <span key={i} className={classes}>
            {parts.map((part, j) =>
              part.toLowerCase() === needle.toLowerCase() ? (
                <mark
                  key={j}
                  className="rounded-sm bg-warning/30 px-0.5 text-inherit"
                >
                  {part}
                </mark>
              ) : (
                <React.Fragment key={j}>{part}</React.Fragment>
              ),
            )}
          </span>
        );
      })}
    </>
  );
});

export interface LogRowProps {
  entry: LogEntry;
  index: number;
  /** Width of the line-number gutter in `ch` units (caller-computed
   * once per render so every row aligns). */
  lineNumberWidth: number;
  showLineNumbers: boolean;
  showTimestamps: boolean;
  ansi: boolean;
  searchQuery: string;
}

export const LogRow = React.memo(function LogRow({
  entry,
  index,
  lineNumberWidth,
  showLineNumbers,
  showTimestamps,
  ansi,
  searchQuery,
}: LogRowProps) {
  const tone = getLevelToneClasses(entry.level);

  return (
    <div className="flex gap-3 border-b border-border/20 px-3 py-1 transition-colors hover:bg-muted/30">
      {showLineNumbers && (
        <span
          className="shrink-0 select-none text-right text-muted-foreground/50 tabular-nums"
          style={{ width: `${lineNumberWidth}ch` }}
          aria-hidden="true"
        >
          {index + 1}
        </span>
      )}
      {showTimestamps && (
        <span className="shrink-0 text-muted-foreground/70 tabular-nums">
          {formatTimestamp(entry.timestamp)}
        </span>
      )}
      <span
        className={cn(
          'w-[3ch] shrink-0 text-right font-semibold tabular-nums',
          tone.text,
        )}
      >
        {LEVEL_LABELS[entry.level]}
      </span>
      <span className="min-w-0 flex-1 whitespace-pre-wrap break-words text-foreground/90">
        <MessageBody
          message={entry.message}
          ansi={ansi}
          searchQuery={searchQuery}
        />
      </span>
    </div>
  );
});
