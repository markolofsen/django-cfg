'use client';

/**
 * CronPreview
 *
 * Read-only sibling of `CronScheduler`. Renders a human-readable summary
 * for a cron expression plus an optional list of upcoming run times.
 *
 * Unlike `SchedulePreview` (which lives inside the editor and pulls its
 * state from `CronSchedulerProvider`), `CronPreview` is fully standalone:
 * pass a value, get a preview. Use it in dashboards, list rows, and
 * read-only schedule views where the heavier editor is not needed.
 *
 * @example
 * <CronPreview value="0 9 * * 1-5" />
 *
 * @example
 * <CronPreview value="*\/15 * * * *" nextRuns={5} />
 */

import * as React from 'react';
import { Calendar } from 'lucide-react';
import { cn } from '@djangocfg/ui-core/lib';
import { humanizeCron } from '../utils/cron-humanize';
import { getNextRuns, formatNextRun } from '../utils/cron-next-runs';
import { isValidCron } from '../utils/cron-parser';

export interface CronPreviewProps extends Omit<React.ComponentPropsWithoutRef<'div'>, 'children'> {
  /** Cron expression (standard 5-field format, e.g. `"0 9 * * 1-5"`). */
  value: string;
  /** Optional heading shown above the summary. */
  title?: string;
  /**
   * Number of upcoming run times to display.
   * `0` hides the list. Defaults to `5`.
   */
  nextRuns?: number;
  /** Show the raw cron expression alongside the summary. Defaults to `true`. */
  showExpression?: boolean;
  /** Base date for computing next runs. Defaults to "now". */
  referenceDate?: Date;
  /**
   * How the preview presents itself.
   *
   * `card` (default) is the dashboard form: a bordered, shadowed panel with a
   * header rule, an icon and an optional list of upcoming runs.
   *
   * `inline` is for a table cell or a list row — a single line of text, no
   * border, no background, no padding. Consumers used to approximate this by
   * passing `className="border-none bg-transparent p-0"`, which could not
   * work: it clears the OUTER container while the header keeps its own
   * `border-b`, so a hairline stayed behind and the cell read as a disabled
   * input. A presentation this different belongs to the component, not to a
   * caller guessing at its internals.
   */
  variant?: 'card' | 'inline';
  /** Additional CSS classes for the outer container. */
  className?: string;
}

export function CronPreview({
  value,
  title,
  nextRuns = 5,
  showExpression = true,
  referenceDate,
  variant = 'card',
  className,
  ...rest
}: CronPreviewProps) {
  const trimmed = (value ?? '').trim();
  const valid = isValidCron(trimmed);

  const summary = React.useMemo(() => humanizeCron(trimmed), [trimmed]);

  const runs = React.useMemo(() => {
    if (!valid || nextRuns <= 0) return [];
    return getNextRuns(trimmed, nextRuns, referenceDate ?? new Date());
  }, [trimmed, valid, nextRuns, referenceDate]);

  if (!valid) {
    // Inline stays inline even when the expression is wrong. A bordered error
    // card inside a table cell is the very box-in-a-box this variant exists to
    // avoid — the colour carries the message on its own.
    if (variant === 'inline') {
      return (
        <span
          data-slot="cron-preview"
          className={cn('inline-flex min-w-0 items-baseline gap-2 text-sm text-destructive', className)}
          {...(rest as React.ComponentPropsWithoutRef<'span'>)}
        >
          <code className="truncate font-mono">{trimmed || '(empty)'}</code>
        </span>
      );
    }
    return (
      <div
        data-slot="cron-preview"
        className={cn(
          'rounded-xl border border-destructive/30 bg-destructive/5 px-4 py-3 text-sm text-destructive',
          className
        )}
        {...rest}
      >
        Invalid cron expression: <code className="font-mono">{trimmed || '(empty)'}</code>
      </div>
    );
  }

  if (variant === 'inline') {
    // One line, nothing else. A row already carries the border, the background
    // and the padding of its table; repeating them here would draw a box
    // inside a box. `nextRuns` and `title` are deliberately ignored — a list
    // row has room for the rule, not for a schedule of its own.
    return (
      <span
        data-slot="cron-preview"
        className={cn('inline-flex min-w-0 items-baseline gap-2 text-sm', className)}
        {...(rest as React.ComponentPropsWithoutRef<'span'>)}
      >
        <span className="truncate text-foreground">{summary}</span>
        {showExpression && (
          <code className="shrink-0 font-mono text-xs text-muted-foreground">
            {trimmed}
          </code>
        )}
      </span>
    );
  }

  return (
    <div
      data-slot="cron-preview"
      role="status"
      aria-live="polite"
      className={cn(
        'overflow-hidden rounded-xl border border-border bg-card text-card-foreground shadow-sm',
        className
      )}
      {...rest}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-3 border-b border-border/60 px-4 py-3">
        <div className="flex min-w-0 items-start gap-2">
          <Calendar aria-hidden="true" className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" />
          <div className="flex min-w-0 flex-col gap-0.5">
            {title && (
              <h3 className="text-sm font-semibold text-foreground">{title}</h3>
            )}
            <p className="text-sm text-muted-foreground">{summary}</p>
          </div>
        </div>
        {showExpression && (
          <code className="shrink-0 rounded-md bg-muted px-2.5 py-1 font-mono text-xs text-foreground">
            {trimmed}
          </code>
        )}
      </div>

      {/* Next runs */}
      {runs.length > 0 && (
        <div className="px-4 py-3">
          <p className="mb-2 text-[10px] font-medium uppercase tracking-wide text-muted-foreground">
            Next {runs.length === 1 ? 'run' : `${runs.length} runs`}
          </p>
          <ol className="flex flex-col gap-1">
            {runs.map((run, i) => (
              <li
                key={run.toISOString()}
                className="flex items-center gap-2 text-sm"
              >
                <span className="flex size-5 shrink-0 items-center justify-center rounded-full bg-muted text-[10px] font-semibold text-muted-foreground">
                  {i + 1}
                </span>
                <span className="font-mono text-xs text-foreground">
                  {formatNextRun(run)}
                </span>
              </li>
            ))}
          </ol>
        </div>
      )}
    </div>
  );
}

export default CronPreview;
