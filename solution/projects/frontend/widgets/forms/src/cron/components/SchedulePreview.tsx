'use client';

/**
 * SchedulePreview
 *
 * Human-readable preview with cron expression and cheatsheet.
 * Shows initial value when it differs from current.
 */

import { useState, useCallback, useMemo } from 'react';
import { Calendar, Copy, Check, ArrowRight } from 'lucide-react';
import { cn } from '@djangocfg/ui-core/lib';
import { useCronPreview, useCronSize } from '../context/hooks';
import { CronCheatsheet } from './CronCheatsheet';

export interface SchedulePreviewProps {
  /** Show raw cron expression (default: true) */
  showCronExpression?: boolean;
  /** Enable copy to clipboard */
  allowCopy?: boolean;
  /** Show initial value when changed (default: true) */
  showInitialValue?: boolean;
  /** Additional CSS classes */
  className?: string;
}

export function SchedulePreview({
  showCronExpression = true,
  allowCopy = false,
  showInitialValue = true,
  className,
}: SchedulePreviewProps) {
  const { cronExpression, humanDescription, isValid, initialValue } = useCronPreview();
  const isSm = useCronSize() === 'sm';

  // Check if value has changed from initial
  const hasChanged = useMemo(
    () => showInitialValue && initialValue && initialValue !== cronExpression,
    [showInitialValue, initialValue, cronExpression]
  );
  const [copied, setCopied] = useState(false);

  const handleCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(cronExpression);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  }, [cronExpression]);

  return (
    <div
      role="status"
      aria-live="polite"
      className={cn(
        'rounded-lg border',
        isSm ? 'px-2 py-1.5' : 'px-3 py-2.5',
        'bg-muted/30 border-border/50',
        !isValid && 'border-destructive/30 bg-destructive/5',
        className
      )}
    >
      {/* Human description */}
      <div className="flex items-center justify-between gap-2">
        <div className={cn('flex items-center min-w-0', isSm ? 'gap-1.5' : 'gap-2')}>
          <Calendar
            aria-hidden="true"
            className={cn(
              'shrink-0',
              isSm ? 'h-3.5 w-3.5' : 'h-4 w-4',
              isValid ? 'text-primary' : 'text-destructive'
            )}
          />
          <span
            className={cn(
              isSm ? 'text-xs' : 'text-sm',
              isValid ? 'text-foreground' : 'text-destructive'
            )}
          >
            {humanDescription}
          </span>
        </div>

        {/* Copy Button */}
        {allowCopy && (
          <button
            type="button"
            onClick={handleCopy}
            disabled={!isValid}
            className={cn(
              'p-1 rounded transition-colors duration-150',
              'hover:bg-muted focus:outline-none focus-visible:ring-2 focus-visible:ring-primary/50',
              'disabled:opacity-50 disabled:cursor-not-allowed'
            )}
            aria-label={copied ? 'Cron expression copied' : 'Copy cron expression'}
            title={copied ? 'Copied!' : 'Copy cron expression'}
          >
            {copied ? (
              <Check aria-hidden="true" className="h-3.5 w-3.5 text-success" />
            ) : (
              <Copy aria-hidden="true" className="h-3.5 w-3.5 text-muted-foreground" />
            )}
          </button>
        )}
      </div>

      {/* Cron expression with cheatsheet */}
      {showCronExpression && (
        <div className="mt-1.5 pt-1.5 border-t border-border/30 flex items-center justify-between">
          <div className="flex items-center gap-1.5 min-w-0">
            {hasChanged && (
              <>
                <code className="text-xs font-mono text-muted-foreground/60 line-through">
                  {initialValue}
                </code>
                <ArrowRight aria-hidden="true" className="h-3 w-3 text-muted-foreground/40 shrink-0" />
              </>
            )}
            <code className="text-xs font-mono text-muted-foreground">
              {cronExpression}
            </code>
          </div>
          <CronCheatsheet />
        </div>
      )}
    </div>
  );
}
