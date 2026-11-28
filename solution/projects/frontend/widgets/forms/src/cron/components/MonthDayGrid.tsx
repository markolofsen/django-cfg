'use client';

/**
 * MonthDayGrid
 *
 * Full-width calendar-style grid for selecting days of the month.
 * Clean, intuitive design like a mini calendar.
 */

import { cn } from '@djangocfg/ui-core/lib';
import { useCronMonthDays, useCronSize } from '../context/hooks';
import type { MonthDay } from '../types';

// Fill to complete last row (31 days = 4 full rows + 3 days, need 4 more to fill)
const GRID_SIZE = 35; // 5 rows x 7 columns

export interface MonthDayGridProps {
  disabled?: boolean;
  showPresets?: boolean;
  className?: string;
}

export function MonthDayGrid({
  disabled,
  showPresets = true,
  className,
}: MonthDayGridProps) {
  const { monthDays, toggleMonthDay, setMonthDays } = useCronMonthDays();
  const isSm = useCronSize() === 'sm';

  // Ensure monthDays is always an array
  const safeMonthDays = Array.isArray(monthDays) ? monthDays : [];

  // Prepare presets data
  const is1st = safeMonthDays.length === 1 && safeMonthDays[0] === 1;
  const is15th = safeMonthDays.length === 1 && safeMonthDays[0] === 15;
  const is1stAnd15th = safeMonthDays.length === 2 && safeMonthDays.includes(1) && safeMonthDays.includes(15);

  const presets = [
    { label: '1st', isActive: is1st, days: [1] as MonthDay[] },
    { label: '15th', isActive: is15th, days: [15] as MonthDay[] },
    { label: '1st & 15th', isActive: is1stAnd15th, days: [1, 15] as MonthDay[] },
  ];

  // Prepare grid cells data
  const gridCells = Array.from({ length: GRID_SIZE }, (_, i) => {
    const day = i + 1;
    const isValidDay = day <= 31;
    const isSelected = isValidDay && safeMonthDays.includes(day as MonthDay);
    const isPartialMonth = day > 28;

    if (!isValidDay) {
      return { type: 'empty' as const, key: i };
    }

    return {
      type: 'day' as const,
      key: day,
      day: day as MonthDay,
      isSelected,
      className: cn(
        'flex items-center justify-center',
        'font-medium',
        isSm
          ? 'h-7 rounded-[5px] text-[10px] leading-none'
          : 'aspect-square rounded-lg text-sm',
        'transition-all duration-150',
        'focus:outline-none focus-visible:ring-2 focus-visible:ring-primary/50',
        'active:scale-[0.95]',
        isSelected
          ? 'bg-primary text-primary-foreground shadow-sm'
          : cn(
              'bg-muted/30 hover:bg-muted/60',
              isPartialMonth
                ? 'text-muted-foreground/50'
                : 'text-muted-foreground'
            ),
        disabled && 'opacity-50 cursor-not-allowed pointer-events-none'
      ),
    };
  });

  const selectionCount = safeMonthDays.length;

  return (
    <div className={cn(isSm ? 'space-y-1.5' : 'space-y-3', className)}>
      {/* Quick Presets */}
      {showPresets && (
        <div className={cn('flex', isSm ? 'gap-1' : 'gap-2')}>
          {presets.map((preset) => (
            <PresetButton
              key={preset.label}
              label={preset.label}
              isActive={preset.isActive}
              onClick={() => setMonthDays(preset.days)}
              disabled={disabled}
              compact={isSm}
            />
          ))}
        </div>
      )}

      {/* Calendar Grid - full width */}
      <div
        className={cn('grid grid-cols-7', isSm ? 'gap-0.5' : 'gap-1')}
        role="group"
        aria-label="Days of month"
      >
        {gridCells.map((cell) => {
          if (cell.type === 'empty') {
            return (
              <div
                key={cell.key}
                aria-hidden="true"
                className={isSm ? 'h-7' : 'aspect-square'}
              />
            );
          }

          return (
            <button
              key={cell.key}
              type="button"
              disabled={disabled}
              onClick={() => toggleMonthDay(cell.day)}
              aria-pressed={cell.isSelected}
              aria-label={`Day ${cell.day} of month`}
              className={cell.className}
            >
              {cell.day}
            </button>
          );
        })}
      </div>

      {/* Selection hint */}
      {selectionCount > 1 && (
        <p
          aria-live="polite"
          className={cn(
            'text-muted-foreground text-center',
            isSm ? 'text-[10px]' : 'text-xs'
          )}
        >
          {selectionCount} days selected
        </p>
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
