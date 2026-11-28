'use client';

/**
 * TimeSelector
 *
 * Clean time picker with hour and minute selects.
 */

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@djangocfg/ui-core/components';
import { cn } from '@djangocfg/ui-core/lib';
import { Clock } from 'lucide-react';
import { useCronTime, useCronSize } from '../context/hooks';

const HOURS = Array.from({ length: 24 }, (_, i) => i);
const MINUTES = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55];

export interface TimeSelectorProps {
  format?: '12h' | '24h';
  disabled?: boolean;
  className?: string;
}

export function TimeSelector({
  format = '24h',
  disabled,
  className,
}: TimeSelectorProps) {
  const { hour, minute, setTime } = useCronTime();
  const isSm = useCronSize() === 'sm';

  const is24h = format === '24h';
  const displayHour = is24h ? hour : (hour % 12) || 12;
  const isPM = hour >= 12;

  const handleHourChange = (value: string) => {
    let newHour = parseInt(value, 10);
    if (!is24h) {
      if (isPM && newHour !== 12) newHour += 12;
      else if (!isPM && newHour === 12) newHour = 0;
    }
    setTime(newHour, minute);
  };

  const handleMinuteChange = (value: string) => {
    setTime(hour, parseInt(value, 10));
  };

  const handlePeriodChange = (value: string) => {
    const newIsPM = value === 'PM';
    let newHour = hour;
    if (newIsPM && hour < 12) newHour = hour + 12;
    else if (!newIsPM && hour >= 12) newHour = hour - 12;
    setTime(newHour, minute);
  };

  const hours = is24h ? HOURS : Array.from({ length: 12 }, (_, i) => i + 1);

  // Compact-aware class fragments
  const triggerClassName = cn(
    isSm ? 'w-[58px] h-7 px-2 text-xs' : 'w-[70px] h-9'
  );
  const itemClassName = isSm ? 'text-xs' : undefined;

  return (
    <div
      className={cn(
        'flex items-center',
        isSm ? 'gap-2' : 'gap-3',
        className
      )}
    >
      <div
        className={cn(
          'flex items-center text-muted-foreground',
          isSm ? 'gap-1.5' : 'gap-2'
        )}
      >
        <Clock
          aria-hidden="true"
          className={isSm ? 'h-3.5 w-3.5' : 'h-4 w-4'}
        />
        <span className={isSm ? 'text-xs' : 'text-sm'}>Run at</span>
      </div>

      <div
        className={cn('flex items-center flex-1', isSm ? 'gap-1' : 'gap-1.5')}
      >
        {/* Hour */}
        <Select
          value={displayHour.toString()}
          onValueChange={handleHourChange}
          disabled={disabled}
        >
          <SelectTrigger className={triggerClassName}>
            <SelectValue>
              {displayHour.toString().padStart(2, '0')}
            </SelectValue>
          </SelectTrigger>
          <SelectContent className="max-h-48">
            {hours.map((h) => (
              <SelectItem key={h} value={h.toString()} className={itemClassName}>
                {h.toString().padStart(2, '0')}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <span className="text-muted-foreground font-medium">:</span>

        {/* Minute */}
        <Select
          value={minute.toString()}
          onValueChange={handleMinuteChange}
          disabled={disabled}
        >
          <SelectTrigger className={triggerClassName}>
            <SelectValue>
              {minute.toString().padStart(2, '0')}
            </SelectValue>
          </SelectTrigger>
          <SelectContent className="max-h-48">
            {MINUTES.map((m) => (
              <SelectItem key={m} value={m.toString()} className={itemClassName}>
                {m.toString().padStart(2, '0')}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        {/* AM/PM for 12h */}
        {!is24h && (
          <Select
            value={isPM ? 'PM' : 'AM'}
            onValueChange={handlePeriodChange}
            disabled={disabled}
          >
            <SelectTrigger className={triggerClassName}>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="AM" className={itemClassName}>AM</SelectItem>
              <SelectItem value="PM" className={itemClassName}>PM</SelectItem>
            </SelectContent>
          </Select>
        )}
      </div>
    </div>
  );
}
