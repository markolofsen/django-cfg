'use client';

/**
 * DayChips
 *
 * Full-width day of week selector with clear labels.
 * Shows abbreviated day names for clarity.
 */

import { cn } from '@djangocfg/ui-core/lib';
import { useCronWeekDays, useCronSize } from '../context/hooks';
import type { WeekDay } from '../types';

const DAYS: { value: WeekDay; label: string; full: string }[] = [
  { value: 1, label: 'Mon', full: 'Monday' },
  { value: 2, label: 'Tue', full: 'Tuesday' },
  { value: 3, label: 'Wed', full: 'Wednesday' },
  { value: 4, label: 'Thu', full: 'Thursday' },
  { value: 5, label: 'Fri', full: 'Friday' },
  { value: 6, label: 'Sat', full: 'Saturday' },
  { value: 0, label: 'Sun', full: 'Sunday' },
];

export interface DayChipsProps {
  disabled?: boolean;
  showPresets?: boolean;
  className?: string;
}

export function DayChips({
  disabled,
  showPresets = true,
  className,
}: DayChipsProps) {
  const { weekDays, toggleWeekDay, setWeekDays } = useCronWeekDays();
  const isSm = useCronSize() === 'sm';

  // Ensure weekDays is always an array
  const safeWeekDays = Array.isArray(weekDays) ? weekDays : [];

  // Prepare data before render
  const isWeekdays = safeWeekDays.length === 5 && [1,2,3,4,5].every(d => safeWeekDays.includes(d as WeekDay));
  const isWeekendPreset = safeWeekDays.length === 2 && [0,6].every(d => safeWeekDays.includes(d as WeekDay));
  const isEveryday = safeWeekDays.length === 7;

  const dayButtons = DAYS.map(({ value, label, full }) => {
    const isSelected = safeWeekDays.includes(value);
    const isWeekendDay = value === 0 || value === 6;

    return {
      value,
      label,
      full,
      isSelected,
      isWeekendDay,
      className: cn(
        'flex flex-col items-center justify-center',
        'font-medium',
        isSm
          ? 'h-6 rounded-md text-[11px] leading-none'
          : 'py-2.5 rounded-lg text-xs',
        'transition-all duration-150',
        'focus:outline-none focus-visible:ring-2 focus-visible:ring-primary/50',
        'active:scale-[0.97]',
        isSelected
          ? 'bg-primary text-primary-foreground shadow-sm'
          : cn(
              'bg-muted/50 hover:bg-muted',
              isWeekendDay ? 'text-muted-foreground/70' : 'text-muted-foreground'
            ),
        disabled && 'opacity-50 cursor-not-allowed pointer-events-none'
      ),
    };
  });

  const presets = [
    { label: 'Weekdays', isActive: isWeekdays, days: [1, 2, 3, 4, 5] as WeekDay[] },
    { label: 'Weekends', isActive: isWeekendPreset, days: [0, 6] as WeekDay[] },
    { label: 'Every day', isActive: isEveryday, days: [0, 1, 2, 3, 4, 5, 6] as WeekDay[] },
  ];

  return (
    <div className={cn(isSm ? 'space-y-1.5' : 'space-y-3', className)}>
      {/* Day Grid - full width */}
      <div
        className={cn('grid grid-cols-7', isSm ? 'gap-1' : 'gap-1')}
        role="group"
        aria-label="Days of week"
      >
        {dayButtons.map((day) => (
          <button
            key={day.value}
            type="button"
            disabled={disabled}
            onClick={() => toggleWeekDay(day.value)}
            aria-pressed={day.isSelected}
            aria-label={day.full}
            className={day.className}
          >
            <span aria-hidden="true">{day.label}</span>
          </button>
        ))}
      </div>

      {/* Quick Presets */}
      {showPresets && (
        <div className={cn('flex', isSm ? 'gap-1' : 'gap-2')}>
          {presets.map((preset) => (
            <PresetButton
              key={preset.label}
              label={preset.label}
              isActive={preset.isActive}
              onClick={() => setWeekDays(preset.days)}
              disabled={disabled}
              compact={isSm}
            />
          ))}
        </div>
      )}
    </div>
  );
}

interface PresetButtonProps {
  label: string;
  isActive: boolean;
  onClick: () => void;
  disabled?: boolean;
  compact?: boolean;
}

function PresetButton({ label, isActive, onClick, disabled, compact }: PresetButtonProps) {
  return (
    <button
      type="button"
      disabled={disabled}
      onClick={onClick}
      className={cn(
        'flex-1 rounded-md font-medium',
        compact
          ? 'h-6 px-1.5 text-[11px] leading-none'
          : 'px-3 py-1.5 text-xs',
        'transition-colors duration-150',
        'focus:outline-none focus-visible:ring-2 focus-visible:ring-primary/50',
        isActive
          ? 'bg-primary/15 text-primary border border-primary/30'
          : 'bg-muted/30 text-muted-foreground hover:bg-muted/50 border border-transparent',
        disabled && 'opacity-50 cursor-not-allowed'
      )}
    >
      {label}
    </button>
  );
}
