"use client"

import React, { useCallback, useMemo } from 'react';

import { Label, RadioGroup, RadioGroupItem } from '@djangocfg/ui-core/components';
import { cn } from '@djangocfg/ui-core/lib';
import { WidgetProps } from '@rjsf/utils';

import { useWidgetEnv } from './_useWidgetEnv';

/**
 * Radio group widget for JSON Schema Form.
 *
 * Renders `enum` fields as a vertical list of radio buttons — an
 * alternative to `SelectWidget` for small option sets. Opt in via
 * `uiSchema`:
 *
 *     { plan: { 'ui:widget': 'radio' } }
 *
 * Set `ui:options.inline = true` to lay the options out in a row.
 * Honors `density` and `ui:disabledWhen` via `useWidgetEnv`.
 */
export function RadioWidget(props: WidgetProps) {
  const { id, value, options, onChange, onBlur, onFocus } = props;
  const { disabled, compact, tooltipText } = useWidgetEnv(props);

  const enumOptions = useMemo(() => {
    const opts = options?.enumOptions;
    if (!Array.isArray(opts)) return [];
    return opts.filter((opt) => opt && opt.value !== undefined);
  }, [options]);

  const inline = options?.inline === true;

  const safeValue = useMemo(() => {
    if (value === null || value === undefined) return '';
    return String(value);
  }, [value]);

  const handleChange = useCallback((next: string) => {
    onChange(next);
    onBlur(id, next);
  }, [onChange, onBlur, id]);

  if (enumOptions.length === 0) {
    return null;
  }

  return (
    <RadioGroup
      value={safeValue}
      onValueChange={handleChange}
      disabled={disabled}
      onFocus={() => onFocus(id, value)}
      title={tooltipText}
      className={cn(
        inline ? 'flex flex-row flex-wrap gap-x-4 gap-y-2' : 'grid gap-2',
        compact && 'gap-1.5',
      )}
    >
      {enumOptions.map((option: { value: unknown; label?: string }) => {
        const optValue = String(option.value);
        const optId = `${id}-${optValue}`;
        return (
          <div key={optValue || '__empty__'} className="flex items-center gap-2">
            <RadioGroupItem value={optValue} id={optId} disabled={disabled} />
            <Label
              htmlFor={optId}
              className={cn('cursor-pointer font-normal', compact && 'text-xs')}
            >
              {option.label || optValue}
            </Label>
          </div>
        );
      })}
    </RadioGroup>
  );
}
