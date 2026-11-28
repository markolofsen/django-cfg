'use client';

/**
 * ScheduleTypeSelector
 *
 * Segmented control for selecting schedule type.
 * Uses Tabs from ui-core styled as a compact segmented control.
 */

import { Tabs, TabsList, TabsTrigger } from '@djangocfg/ui-core/components';
import { cn } from '@djangocfg/ui-core/lib';
import { useCronType, useCronSize } from '../context/hooks';
import type { ScheduleType } from '../types';

const SCHEDULE_TYPES: { value: ScheduleType; label: string }[] = [
  { value: 'daily', label: 'Daily' },
  { value: 'weekly', label: 'Weekly' },
  { value: 'monthly', label: 'Monthly' },
  { value: 'custom', label: 'Custom' },
];

export interface ScheduleTypeSelectorProps {
  disabled?: boolean;
  className?: string;
}

export function ScheduleTypeSelector({
  disabled,
  className,
}: ScheduleTypeSelectorProps) {
  const { type, setType } = useCronType();
  const isSm = useCronSize() === 'sm';

  const triggerClassName = cn(
    'font-medium',
    isSm
      ? 'text-[11px] leading-none px-1 py-0.5 h-6 rounded-[5px]'
      : 'text-xs px-2 py-1.5',
    'data-[state=active]:shadow-sm',
    'transition-all duration-150'
  );

  const triggers = SCHEDULE_TYPES.map(({ value, label }) => ({
    value,
    label,
    disabled,
    className: triggerClassName,
  }));

  return (
    <Tabs
      value={type}
      onValueChange={(v) => setType(v as ScheduleType)}
      className={cn('w-full', className)}
    >
      <TabsList
        className={cn(
          'grid w-full grid-cols-4',
          isSm ? 'h-7 p-0.5 gap-0.5' : 'h-9 p-0.5'
        )}
      >
        {triggers.map((trigger) => (
          <TabsTrigger
            key={trigger.value}
            value={trigger.value}
            disabled={trigger.disabled}
            className={trigger.className}
          >
            {trigger.label}
          </TabsTrigger>
        ))}
      </TabsList>
    </Tabs>
  );
}
