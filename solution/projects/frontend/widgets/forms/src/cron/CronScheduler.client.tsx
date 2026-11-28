'use client';

/**
 * CronScheduler Client Component
 *
 * Compact cron builder. The default surface is a single popover trigger
 * that reads like a value input ("Weekdays at 09:00") — the schedule
 * editor lives inside the popover, following the ui-core combobox
 * pattern. Pass `inline` to render the editor expanded without a popover.
 */

import { useState } from 'react';
import { Calendar, ChevronsUpDown, Check, Copy } from 'lucide-react';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@djangocfg/ui-core/components';
import { cn } from '@djangocfg/ui-core/lib';
import { CronSchedulerProvider } from './context/CronSchedulerContext';
import { useCronType, useCronPreview, useCronSize } from './context/hooks';
import {
  ScheduleTypeSelector,
  TimeSelector,
  DayChips,
  MonthDayGrid,
  CustomInput,
} from './components';
import type { CronSchedulerProps } from './types';

// ============================================================================
// Schedule editor (shared by inline + popover modes)
// ============================================================================

interface ScheduleEditorProps {
  timeFormat: '12h' | '24h';
  disabled: boolean;
}

function ScheduleEditor({ timeFormat, disabled }: ScheduleEditorProps) {
  const { type } = useCronType();
  const size = useCronSize();
  const isSm = size === 'sm';

  return (
    <div className={isSm ? 'space-y-1.5' : 'space-y-3'}>
      <ScheduleTypeSelector disabled={disabled} />

      {type !== 'custom' && (
        <TimeSelector format={timeFormat} disabled={disabled} />
      )}
      {type === 'weekly' && <DayChips disabled={disabled} showPresets />}
      {type === 'monthly' && <MonthDayGrid disabled={disabled} showPresets />}
      {type === 'custom' && <CustomInput disabled={disabled} />}
    </div>
  );
}

// ============================================================================
// Cron expression line (shared)
// ============================================================================

function CronExpressionLine({
  allowCopy,
  className,
}: {
  allowCopy: boolean;
  className?: string;
}) {
  const [copied, setCopied] = useState(false);
  const { cronExpression, isValid } = useCronPreview();
  const isSm = useCronSize() === 'sm';

  const handleCopy = async (e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await navigator.clipboard.writeText(cronExpression);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  return (
    <div className={cn('flex items-center', isSm ? 'gap-1' : 'gap-1.5', className)}>
      <code
        className={cn(
          'font-mono text-muted-foreground',
          isSm ? 'text-[11px]' : 'text-xs'
        )}
      >
        {cronExpression}
      </code>
      {allowCopy && (
        <button
          type="button"
          onClick={handleCopy}
          disabled={!isValid}
          className={cn(
            'rounded p-0.5 transition-colors',
            'hover:bg-muted focus:outline-none focus-visible:ring-2 focus-visible:ring-ring/50',
            'disabled:opacity-50 disabled:cursor-not-allowed'
          )}
          aria-label={copied ? 'Cron expression copied' : 'Copy cron expression'}
          title={copied ? 'Copied!' : 'Copy cron expression'}
        >
          {copied ? (
            <Check aria-hidden="true" className="h-3 w-3 text-success" />
          ) : (
            <Copy aria-hidden="true" className="h-3 w-3 text-muted-foreground" />
          )}
        </button>
      )}
    </div>
  );
}

// ============================================================================
// Compact popover trigger (default surface)
// ============================================================================

interface CompactTriggerProps {
  showCronExpression: boolean;
  allowCopy: boolean;
  timeFormat: '12h' | '24h';
  disabled: boolean;
  placeholder: string;
  className?: string;
}

function CompactTrigger({
  showCronExpression,
  allowCopy,
  timeFormat,
  disabled,
  placeholder,
  className,
}: CompactTriggerProps) {
  const [open, setOpen] = useState(false);
  const { humanDescription, isValid } = useCronPreview();
  const isSm = useCronSize() === 'sm';

  return (
    <div className={cn(isSm ? 'space-y-1' : 'space-y-1.5', className)}>
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <button
            type="button"
            role="combobox"
            aria-expanded={open}
            disabled={disabled}
            className={cn(
              'flex w-full items-center rounded-md border',
              'border-input bg-transparent shadow-xs transition-colors',
              'hover:bg-accent/40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/50',
              'disabled:cursor-not-allowed disabled:opacity-50',
              isSm ? 'h-8 gap-1.5 px-2 text-xs' : 'h-9 gap-2 px-3 text-sm',
              !isValid && 'border-destructive/50'
            )}
          >
            <Calendar
              aria-hidden="true"
              className={cn(
                'shrink-0',
                isSm ? 'h-3.5 w-3.5' : 'h-4 w-4',
                isValid ? 'text-muted-foreground' : 'text-destructive'
              )}
            />
            <span
              className={cn(
                'flex-1 truncate text-left',
                !isValid && 'text-destructive'
              )}
            >
              {humanDescription || placeholder}
            </span>
            <ChevronsUpDown
              aria-hidden="true"
              className={cn('shrink-0 opacity-50', isSm ? 'h-3.5 w-3.5' : 'h-4 w-4')}
            />
          </button>
        </PopoverTrigger>
        <PopoverContent
          className={cn(
            'w-[var(--radix-popover-trigger-width)]',
            isSm ? 'min-w-[280px] p-2' : 'min-w-[320px] p-3'
          )}
          align="start"
        >
          <ScheduleEditor timeFormat={timeFormat} disabled={disabled} />
        </PopoverContent>
      </Popover>

      {showCronExpression && (
        <CronExpressionLine allowCopy={allowCopy} className="px-1" />
      )}
    </div>
  );
}

// ============================================================================
// Inline variant (editor expanded, no popover)
// ============================================================================

interface InlineSchedulerProps extends ScheduleEditorProps {
  showCronExpression: boolean;
  allowCopy: boolean;
  className?: string;
}

function InlineScheduler({
  timeFormat,
  disabled,
  showCronExpression,
  allowCopy,
  className,
}: InlineSchedulerProps) {
  const isSm = useCronSize() === 'sm';

  return (
    <div className={cn(isSm ? 'space-y-1.5' : 'space-y-3', className)}>
      <ScheduleEditor timeFormat={timeFormat} disabled={disabled} />
      <InlinePreview showCronExpression={showCronExpression} allowCopy={allowCopy} />
    </div>
  );
}

function InlinePreview({
  showCronExpression,
  allowCopy,
}: {
  showCronExpression: boolean;
  allowCopy: boolean;
}) {
  const { humanDescription, isValid } = useCronPreview();
  const isSm = useCronSize() === 'sm';

  return (
    <div
      role="status"
      aria-live="polite"
      className={cn(
        'flex items-center justify-between gap-2 rounded-md border',
        'bg-muted/30 border-border/50',
        isSm ? 'px-2 py-1' : 'px-3 py-2',
        !isValid && 'border-destructive/30 bg-destructive/5'
      )}
    >
      <div className={cn('flex min-w-0 items-center', isSm ? 'gap-1.5' : 'gap-2')}>
        <Calendar
          aria-hidden="true"
          className={cn(
            'shrink-0',
            isSm ? 'h-3 w-3' : 'h-4 w-4',
            isValid ? 'text-primary' : 'text-destructive'
          )}
        />
        <span
          className={cn(
            'truncate',
            isSm ? 'text-[11px]' : 'text-sm',
            !isValid && 'text-destructive'
          )}
        >
          {humanDescription}
        </span>
      </div>
      {showCronExpression && (
        <CronExpressionLine allowCopy={allowCopy} className="shrink-0" />
      )}
    </div>
  );
}

// ============================================================================
// Main Component (with Provider)
// ============================================================================

/**
 * CronScheduler - compact cron expression builder
 *
 * Default surface is a single popover trigger that reads the schedule as
 * plain text ("Weekdays at 09:00"). Pass `inline` for the legacy expanded
 * layout.
 *
 * @example
 * <CronScheduler value={cron} onChange={setCron} showCronExpression />
 *
 * @example
 * // Legacy expanded layout
 * <CronScheduler value="0 9 * * 1-5" onChange={setCron} inline />
 */
export function CronScheduler({
  value,
  onChange,
  defaultType = 'daily',
  showCronExpression = false,
  allowCopy = false,
  timeFormat = '24h',
  disabled = false,
  inline = false,
  placeholder = 'Set a schedule',
  size = 'default',
  className,
}: CronSchedulerProps) {
  return (
    <CronSchedulerProvider
      value={value}
      onChange={onChange}
      defaultType={defaultType}
      size={size}
    >
      {inline ? (
        <InlineScheduler
          timeFormat={timeFormat}
          disabled={disabled}
          showCronExpression={showCronExpression}
          allowCopy={allowCopy}
          className={className}
        />
      ) : (
        <CompactTrigger
          showCronExpression={showCronExpression}
          allowCopy={allowCopy}
          timeFormat={timeFormat}
          disabled={disabled}
          placeholder={placeholder}
          className={className}
        />
      )}
    </CronSchedulerProvider>
  );
}

export default CronScheduler;
