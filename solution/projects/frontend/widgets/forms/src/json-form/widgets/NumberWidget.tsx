"use client"

import React, { useCallback, useMemo } from 'react';

import { Input } from '@djangocfg/ui-core/components';
import { cn } from '@djangocfg/ui-core/lib';
import { WidgetProps } from '@rjsf/utils';

import { useWidgetEnv } from './_useWidgetEnv';

/**
 * Number input widget for JSON Schema Form.
 * Handles `integer` and `number` fields. Honors `density` and
 * `ui:disabledWhen` via `useWidgetEnv`.
 */
export function NumberWidget(props: WidgetProps) {
  const {
    id,
    placeholder,
    required,
    autofocus,
    value,
    onChange,
    onBlur,
    onFocus,
    options,
    schema,
    rawErrors,
  } = props;
  const { disabled, compact, tooltipText } = useWidgetEnv(props);

  // Memoize widget configuration
  const config = useMemo(() => ({
    isInteger: schema.type === 'integer',
    step: schema.multipleOf ?? (schema.type === 'integer' ? 1 : 'any'),
    min: schema.minimum,
    max: schema.maximum,
    emptyValue: options?.emptyValue,
  }), [schema, options]);

  // Ensure value is valid number or empty string
  const safeValue = useMemo(() => {
    if (value === null || value === undefined || value === '') return '';
    if (typeof value === 'number' && !isNaN(value)) return value;
    const coerced = Number(value);
    return isNaN(coerced) ? '' : coerced;
  }, [value]);

  const hasError = useMemo(() => {
    return Boolean(rawErrors && rawErrors.length > 0);
  }, [rawErrors]);

  const handleChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = event.target.value;
    if (newValue === '') {
      onChange(config.emptyValue);
    } else {
      const parsedValue = config.isInteger
        ? parseInt(newValue, 10)
        : parseFloat(newValue);

      onChange(isNaN(parsedValue) ? config.emptyValue : parsedValue);
    }
  }, [onChange, config]);

  const handleBlur = useCallback((event: React.FocusEvent<HTMLInputElement>) => {
    onBlur(id, event.target.value);
  }, [id, onBlur]);

  const handleFocus = useCallback((event: React.FocusEvent<HTMLInputElement>) => {
    onFocus(id, event.target.value);
  }, [id, onFocus]);

  return (
    <Input
      id={id}
      type="number"
      placeholder={placeholder}
      disabled={disabled}
      autoFocus={autofocus}
      value={safeValue}
      required={required}
      onChange={handleChange}
      onBlur={handleBlur}
      onFocus={handleFocus}
      step={config.step}
      min={config.min}
      max={config.max}
      title={tooltipText}
      aria-invalid={hasError || undefined}
      className={cn(hasError && 'border-destructive', compact && 'h-7 text-xs')}
    />
  );
}
