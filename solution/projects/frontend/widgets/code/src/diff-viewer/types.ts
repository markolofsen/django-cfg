// Adapted from jalcoui (MIT) — github.com/jal-co/ui

import type * as React from 'react';
import type { Language } from 'prism-react-renderer';

/** Layout of the diff: single-column unified vs. side-by-side split. */
export type DiffLayout = 'unified' | 'split';

/** Per-line kind in a computed diff. */
export type DiffLineType = 'added' | 'removed' | 'context';

/**
 * One rendered line in the diff. Old / new line numbers are independent:
 * an added line has no `oldNumber`, a removed line has no `newNumber`.
 */
export interface DiffLine {
  type: DiffLineType;
  content: string;
  oldNumber: number | null;
  newNumber: number | null;
}

/** Diff stats — rendered in the header pill. */
export interface DiffStats {
  added: number;
  removed: number;
}

interface WithStrings {
  /** Original code (LHS). */
  oldCode: string;
  /** Updated code (RHS). */
  newCode: string;
  patch?: never;
}

interface WithPatch {
  /** Pre-computed unified diff string (alternative to oldCode / newCode). */
  patch: string;
  oldCode?: never;
  newCode?: never;
}

export type DiffInput = WithStrings | WithPatch;

/**
 * Tone classes for a single diff line. Tailwind class strings backed by
 * semantic tokens — the diff viewer adapts to the host theme (light or
 * dark) unlike `PrettyCode`, which is intentionally always-dark. Diffs
 * are commonly embedded in documentation pages, where forcing a dark
 * surface on a light page looks like a bug.
 */
export interface DiffToneClasses {
  /** Row background tint. */
  row: string;
  /** Gutter / line-number column foreground. */
  num: string;
  /** Body text color. */
  text: string;
  /** Header stat pill color (e.g. `+12`). */
  stat: string;
}

/**
 * Mapping from line type to tone class bundle. Semantic tokens —
 * resolved by the host theme (light surfaces in light mode, dark in
 * dark mode).
 */
export const DIFF_TONE_CLASSES: Record<DiffLineType, DiffToneClasses> = {
  added: {
    row: 'bg-success/10',
    num: 'text-success/80',
    text: 'text-success',
    stat: 'text-success',
  },
  removed: {
    row: 'bg-destructive/15',
    num: 'text-destructive/80',
    text: 'text-destructive',
    stat: 'text-destructive',
  },
  context: {
    row: '',
    num: 'text-muted-foreground/60',
    text: 'text-foreground',
    stat: 'text-muted-foreground',
  },
};

export type DiffViewerProps = DiffInput &
  Omit<React.ComponentProps<'div'>, 'children'> & {
    /** Layout. @default `'unified'` */
    layout?: DiffLayout;
    /**
     * Prism language key for optional syntax highlighting. When omitted,
     * lines render as plain monospace. Highlighting reuses the same
     * `prism-react-renderer` instance as the `PrettyCode` tool — no
     * second highlighter is loaded.
     */
    language?: Language | string;
    /** Label for the LHS file header. */
    oldTitle?: string;
    /** Label for the RHS file header. */
    newTitle?: string;
    /** Show the copy-to-clipboard button. @default `true` */
    copyable?: boolean;
    /** Number of context lines around each hunk when diffing strings. @default `3` */
    context?: number;
    /**
     * The HOST caps this viewer's height and owns the scroller (e.g. a chat
     * bubble with `maxHeight` + `overflowY:auto`). Set it and the >100-line
     * virtualized path is skipped, because Virtuoso would otherwise open its
     * own fixed-height scroller INSIDE the host's — two scrollers of the same
     * size, neither owning the scroll position Virtuoso measures against,
     * leaving blank bands between consecutively-numbered rows.
     *
     * Not a styling hint and not a performance knob: it answers "who owns the
     * height", which has exactly one right answer per embedding. Leave it false
     * (the default) wherever the viewer is free to grow — documentation embeds
     * expect that, and they are the case virtualization exists for.
     *
     * @default `false`
     */
    hostScrolls?: boolean;
  };
