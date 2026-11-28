'use client';

/**
 * CustomInput
 *
 * Raw cron expression input with validation and help popover.
 */

import { useState, useEffect } from 'react';
import { Input } from '@djangocfg/ui-core/components';
import { cn } from '@djangocfg/ui-core/lib';
import { AlertCircle, CheckCircle2 } from 'lucide-react';
import { useCronCustom, useCronSize } from '../context/hooks';
import { isValidCron } from '../utils/cron-parser';

export interface CustomInputProps {
  disabled?: boolean;
  className?: string;
}

export function CustomInput({ disabled, className }: CustomInputProps) {
  const { customCron, isValid, setCustomCron } = useCronCustom();
  const isSm = useCronSize() === 'sm';
  const [localValue, setLocalValue] = useState(customCron);
  const [localValid, setLocalValid] = useState(isValid);

  useEffect(() => {
    setLocalValue(customCron);
    setLocalValid(isValid);
  }, [customCron, isValid]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setLocalValue(value);
    const valid = isValidCron(value);
    setLocalValid(valid);
    setCustomCron(value);
  };

  const showError = !localValid && localValue.trim().length > 0;

  return (
    <div className={cn(isSm ? 'space-y-1.5' : 'space-y-2', className)}>
      <label
        htmlFor="cron-custom-input"
        className={cn(
          'text-muted-foreground',
          isSm ? 'text-xs' : 'text-sm'
        )}
      >
        Cron expression
      </label>

      <div className="relative">
        <Input
          id="cron-custom-input"
          type="text"
          value={localValue}
          onChange={handleChange}
          disabled={disabled}
          placeholder="* * * * *"
          autoComplete="off"
          autoCapitalize="off"
          autoCorrect="off"
          spellCheck={false}
          aria-invalid={showError}
          aria-describedby={showError ? 'cron-custom-error' : undefined}
          className={cn(
            'font-mono',
            isSm ? 'text-xs h-8 pr-8' : 'text-base h-11 pr-10',
            showError && 'border-destructive focus-visible:ring-destructive/50'
          )}
        />
        <div
          className={cn(
            'absolute top-1/2 -translate-y-1/2',
            isSm ? 'right-2' : 'right-3'
          )}
        >
          {localValue.trim() && (
            localValid ? (
              <CheckCircle2
                aria-hidden="true"
                className={cn('text-success', isSm ? 'h-4 w-4' : 'h-5 w-5')}
              />
            ) : (
              <AlertCircle
                aria-hidden="true"
                className={cn('text-destructive', isSm ? 'h-4 w-4' : 'h-5 w-5')}
              />
            )
          )}
        </div>
      </div>

      {showError && (
        <p id="cron-custom-error" role="alert" className="text-xs text-destructive">
          Invalid cron expression — expected 5 fields: minute hour day month weekday.
        </p>
      )}
    </div>
  );
}
