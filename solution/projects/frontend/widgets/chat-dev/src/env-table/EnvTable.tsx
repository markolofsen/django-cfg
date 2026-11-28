// Adapted from jalcoui (MIT) — github.com/jal-co/ui
//
// Read-only environment variable table with masked values, click-to-reveal,
// and per-row copy. Designed for settings pages, deploy previews, and docs.
//
// - Semantic tokens only (success / warning / info / destructive / muted).
// - No motion library — Tailwind `transition-colors` for hover feedback.
// - Requires <UiProviders> at the host root; mounts no providers itself.

'use client';

import * as React from 'react';
import { Check, ClipboardList, Copy, Eye, EyeOff } from 'lucide-react';
import { cn } from '@djangocfg/ui-core/lib';
import {
  ENV_TONE_CLASSES,
  getEnvTone,
  type EnvTableProps,
  type EnvVariable,
} from './types';
import { maskValue, useEnvMask } from './hooks/useEnvMask';

interface RowProps {
  variable: EnvVariable;
  revealed: boolean;
  copied: boolean;
  onToggleReveal: () => void;
  onCopy: () => void;
}

function EnvRow({ variable, revealed, copied, onToggleReveal, onCopy }: RowProps) {
  const tone = getEnvTone(variable.environment);
  const displayValue = revealed ? variable.value : maskValue(variable.value);

  return (
    <div
      data-slot="env-row"
      data-revealed={revealed}
      className="group flex items-start gap-3 px-3 py-2.5 transition-colors hover:bg-accent sm:items-center sm:px-4"
    >
      <div className="flex min-w-0 flex-1 flex-col gap-1.5 sm:flex-row sm:items-center sm:gap-4">
        {/* Key */}
        <div className="flex shrink-0 items-center gap-2 sm:w-[220px]">
          <span
            className={cn(
              'truncate font-mono text-xs font-semibold',
              variable.required ? 'text-destructive' : 'text-foreground',
            )}
          >
            {variable.key}
            {variable.required && (
              <span
                aria-label="required"
                className="ml-0.5 text-destructive"
                title="Required"
              >
                *
              </span>
            )}
          </span>
          {variable.environment && (
            <span
              className={cn(
                'shrink-0 rounded-full px-2 py-0.5 text-[10px] font-medium leading-none',
                ENV_TONE_CLASSES[tone],
              )}
            >
              {variable.environment}
            </span>
          )}
        </div>

        {/* Value */}
        <div className="min-w-0 flex-1">
          <span
            className={cn(
              'break-all font-mono text-xs',
              revealed ? 'text-foreground' : 'text-muted-foreground',
            )}
          >
            {displayValue}
          </span>
          {variable.description && (
            <p className="mt-0.5 text-[11px] text-muted-foreground">
              {variable.description}
            </p>
          )}
        </div>
      </div>

      {/* Actions */}
      <div className="flex shrink-0 items-center gap-0.5">
        <button
          type="button"
          onClick={onToggleReveal}
          aria-label={`${revealed ? 'Hide' : 'Reveal'} ${variable.key}`}
          aria-pressed={revealed}
          className="inline-flex items-center justify-center rounded-md p-1.5 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        >
          {revealed ? (
            <EyeOff className="size-3.5" />
          ) : (
            <Eye className="size-3.5" />
          )}
        </button>
        <button
          type="button"
          onClick={onCopy}
          aria-label={`Copy ${variable.key} value`}
          className="inline-flex items-center justify-center rounded-md p-1.5 text-muted-foreground transition-colors hover:bg-muted hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        >
          {copied ? (
            <Check className="size-3.5 text-success" />
          ) : (
            <Copy className="size-3.5" />
          )}
        </button>
      </div>
    </div>
  );
}

export function EnvTable({
  variables,
  title,
  defaultRevealed = false,
  emptyLabel = 'No environment variables.',
  className,
  ...props
}: EnvTableProps) {
  const {
    revealed,
    allRevealed,
    toggleIndex,
    toggleAll,
    copiedTarget,
    copyValue,
    copyAllAsEnv,
  } = useEnvMask({ variables, defaultRevealed });

  if (variables.length === 0) {
    return (
      <div
        data-slot="env-table"
        data-empty="true"
        className={cn(
          'flex items-center justify-center rounded-xl border border-border/60 bg-card py-10 text-sm text-muted-foreground shadow-sm',
          className,
        )}
        {...props}
      >
        {emptyLabel}
      </div>
    );
  }

  const copiedAll = copiedTarget === 'all';

  return (
    <div
      data-slot="env-table"
      className={cn(
        'overflow-hidden rounded-xl border border-border/60 bg-card shadow-sm',
        className,
      )}
      {...props}
    >
      {/* Header */}
      <div className="flex items-center justify-between border-b border-border/40 px-3 py-2.5 sm:px-4">
        <div className="flex items-center gap-2">
          {title && (
            <h3 className="text-sm font-semibold text-foreground">{title}</h3>
          )}
          <span className="rounded-full bg-muted px-2 py-0.5 text-[10px] font-medium text-muted-foreground">
            {variables.length}
          </span>
        </div>
        <div className="flex items-center gap-1">
          <button
            type="button"
            onClick={toggleAll}
            aria-label={allRevealed ? 'Hide all values' : 'Reveal all values'}
            aria-pressed={allRevealed}
            className="inline-flex items-center gap-1.5 rounded-md px-2 py-1.5 text-xs text-muted-foreground transition-colors hover:bg-muted hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          >
            {allRevealed ? (
              <EyeOff className="size-3.5" />
            ) : (
              <Eye className="size-3.5" />
            )}
            <span className="hidden sm:inline">
              {allRevealed ? 'Hide all' : 'Reveal all'}
            </span>
          </button>
          <button
            type="button"
            onClick={copyAllAsEnv}
            aria-label="Copy all as .env"
            className="inline-flex items-center gap-1.5 rounded-md px-2 py-1.5 text-xs text-muted-foreground transition-colors hover:bg-muted hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          >
            {copiedAll ? (
              <Check className="size-3.5 text-success" />
            ) : (
              <ClipboardList className="size-3.5" />
            )}
            <span className="hidden sm:inline">
              {copiedAll ? 'Copied!' : 'Copy .env'}
            </span>
          </button>
        </div>
      </div>

      {/* Rows */}
      <div className="divide-y divide-border/40">
        {variables.map((variable, i) => (
          <EnvRow
            key={`${variable.key}-${i}`}
            variable={variable}
            revealed={revealed.has(i)}
            copied={copiedTarget === i}
            onToggleReveal={() => toggleIndex(i)}
            onCopy={() => copyValue(i, variable.value)}
          />
        ))}
      </div>
    </div>
  );
}
