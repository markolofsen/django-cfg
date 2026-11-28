// Adapted from jalcoui (MIT) — github.com/jal-co/ui

import type * as React from 'react';

/**
 * Severity level of a log entry. Five canonical levels — `error`, `warn`,
 * `info`, `debug` route to status / categorical semantic tokens; `verbose`
 * collapses to muted.
 */
export type LogLevel = 'error' | 'warn' | 'info' | 'debug' | 'verbose';

/**
 * Tone bucket each level resolves to. `debug` is intentionally **not** a
 * status — it routes through a categorical preset color so themes can
 * rotate it without polluting the destructive/warning/info/success
 * palette.
 */
export type LogTone = 'destructive' | 'warning' | 'info' | 'debug' | 'muted';

export interface LogEntry {
  /** Severity. */
  level: LogLevel;
  /** Log message text. May contain ANSI escape sequences. */
  message: string;
  /** ISO timestamp string. When omitted, the current time is used for display. */
  timestamp?: string;
}

/**
 * Tone CSS class bundle per `LogTone`. Every class resolves to a semantic
 * token (no raw color scales). `dot` and `text` ride on opacity-derived
 * surfaces so they survive every preset that overrides only the base
 * `--{status}` token.
 */
export interface LogToneClasses {
  /** Text color for the level label / icon. */
  text: string;
  /** Background for the filled dot. */
  dot: string;
  /** Badge surface when the level filter is active. */
  badge: string;
}

/**
 * Mapping from {@link LogLevel} to {@link LogTone}. `debug` collapses to
 * the categorical `debug` tone — it is not a status.
 */
export const LEVEL_TONE: Record<LogLevel, LogTone> = {
  error: 'destructive',
  warn: 'warning',
  info: 'info',
  debug: 'debug',
  verbose: 'muted',
};

/**
 * Short 3-letter labels rendered in monospace gutters. Matches `ERR`,
 * `WRN`, `INF`, `DBG`, `VRB` so columns align on screen.
 */
export const LEVEL_LABELS: Record<LogLevel, string> = {
  error: 'ERR',
  warn: 'WRN',
  info: 'INF',
  debug: 'DBG',
  verbose: 'VRB',
};

/**
 * Semantic-token class bundle per {@link LogTone}. All `bg-` / `text-`
 * values resolve through ui-core tokens — themes can swap them without
 * touching this file. `debug` uses a violet-ish categorical via the
 * `--chart-4`/`--chart-5` fallbacks already shipped in ui-core (we keep
 * it on the `muted` family for surface and lean on opacity for
 * differentiation; the actual debug color comes from the level dot in
 * the source).
 */
export const TONE_CLASSES: Record<LogTone, LogToneClasses> = {
  destructive: {
    text: 'text-destructive',
    dot: 'bg-destructive',
    badge: 'bg-destructive/15 text-destructive',
  },
  warning: {
    text: 'text-warning',
    dot: 'bg-warning',
    badge: 'bg-warning/15 text-warning',
  },
  info: {
    text: 'text-info',
    dot: 'bg-info',
    badge: 'bg-info/15 text-info',
  },
  // `debug` is categorical, not status — render via primary token tinted
  // for legibility; themes that recolour `--primary` get a free debug
  // shift without touching this file.
  debug: {
    text: 'text-primary',
    dot: 'bg-primary',
    badge: 'bg-primary/15 text-primary',
  },
  muted: {
    text: 'text-muted-foreground',
    dot: 'bg-muted-foreground/60',
    badge: 'bg-muted text-muted-foreground',
  },
};

/**
 * Resolve the tone class bundle for a level.
 */
export function getLevelToneClasses(level: LogLevel): LogToneClasses {
  return TONE_CLASSES[LEVEL_TONE[level]];
}

export interface LogViewerProps
  extends Omit<React.ComponentProps<'div'>, 'children' | 'title'> {
  /** Log entries to render. */
  entries: LogEntry[];
  /** Header title. @default "Logs" */
  title?: string;
  /** Maximum visible height in pixels. @default 400 */
  maxHeight?: number;
  /** Show monospace line numbers. @default true */
  lineNumbers?: boolean;
  /** Show timestamps. @default true */
  timestamps?: boolean;
  /** Auto-scroll to bottom when new entries arrive (and the user is
   * already pinned to the bottom). @default true */
  autoScroll?: boolean;
  /** Levels exposed in the toolbar filter chips. @default all five */
  levels?: LogLevel[];
  /** Interpret ANSI escape sequences (`\x1b[31m…`) in `message`.
   * @default true */
  ansi?: boolean;
  /** Optional callback wired to the "Clear" toolbar button — when
   * omitted, the button is hidden. */
  onClear?: () => void;
  /** Force-disable virtualization (small / Storybook usage). The
   * virtualized path uses `react-virtuoso` and handles 10k+ entries
   * without lag. @default false */
  noVirtualize?: boolean;
}
