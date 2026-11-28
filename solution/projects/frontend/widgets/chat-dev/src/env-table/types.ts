// Adapted from jalcoui (MIT) — github.com/jal-co/ui

import type * as React from 'react';

/**
 * Target environment for a variable. Renders as a colored badge next to the
 * variable name. Custom string values fall back to the muted tone.
 */
export type EnvEnvironment =
  | 'production'
  | 'preview'
  | 'development'
  | (string & {});

/**
 * Tone mapping for environment badges. Resolves to semantic surface tokens —
 * never raw color scales.
 */
export type EnvBadgeTone = 'success' | 'warning' | 'info' | 'muted';

/**
 * One environment variable row.
 */
export interface EnvVariable {
  /** Variable name (e.g. DATABASE_URL). */
  key: string;
  /** Variable value. Masked by default. */
  value: string;
  /** Target environment. When provided, renders as a badge. */
  environment?: EnvEnvironment;
  /** Optional description shown below the value. */
  description?: string;
  /** Mark the row as required — name renders in `text-destructive`. */
  required?: boolean;
}

export interface EnvTableProps
  extends Omit<React.ComponentProps<'div'>, 'children' | 'title'> {
  /** Environment variables to display. */
  variables: EnvVariable[];
  /** Optional heading above the table. */
  title?: string;
  /** Start with all values revealed. Defaults to `false`. */
  defaultRevealed?: boolean;
  /** Empty-state text. Defaults to `"No environment variables."`. */
  emptyLabel?: string;
}

/**
 * Map environment string → semantic tone. Unknown strings fall through to
 * `muted`.
 */
export function getEnvTone(env: EnvEnvironment | undefined): EnvBadgeTone {
  switch (env) {
    case 'production':
      return 'success';
    case 'preview':
      return 'info';
    case 'development':
      return 'warning';
    default:
      return 'muted';
  }
}

/**
 * Tailwind classes per env badge tone. All resolve to semantic tokens; opacity-
 * derived surfaces keep every preset safe even when `*-background` tokens are
 * not overridden.
 */
export const ENV_TONE_CLASSES: Record<EnvBadgeTone, string> = {
  success: 'bg-success/15 text-success',
  warning: 'bg-warning/15 text-warning',
  info: 'bg-info/15 text-info',
  muted: 'bg-muted text-muted-foreground',
};
