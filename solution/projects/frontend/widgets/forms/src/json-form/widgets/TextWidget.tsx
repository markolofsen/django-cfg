"use client"

import React, { useCallback, useMemo } from 'react';

import { Input, Textarea } from '@djangocfg/ui-core/components';
import { cn } from '@djangocfg/ui-core/lib';
import { WidgetProps } from '@rjsf/utils';

import { useWidgetEnv } from './_useWidgetEnv';

/**
 * Text input widget for JSON Schema Form.
 *
 * Handles `string` fields. Switches to a multiline `Textarea` when
 * `options.widget === 'textarea'` (see `TextareaWidget`). Maps the
 * schema `format` to a native input type (`email`, `url`, `tel`,
 * `password`, `date`, `datetime-local`, `time`). Honors `density`
 * and `ui:disabledWhen` via `useWidgetEnv`.
 */

/** Maps JSON Schema `format` values to native `<input type>` values. */
const FORMAT_INPUT_TYPE: Record<string, string> = {
  email: 'email',
  uri: 'url',
  url: 'url',
  tel: 'tel',
  phone: 'tel',
  password: 'password',
  date: 'date',
  'date-time': 'datetime-local',
  datetime: 'datetime-local',
  time: 'time',
};

export function TextWidget(props: WidgetProps) {
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
    isTextarea: options?.widget === 'textarea',
    rows: typeof options?.rows === 'number' ? options.rows : 3,
    emptyValue: options?.emptyValue,
    inputType:
      (typeof schema.format === 'string' && FORMAT_INPUT_TYPE[schema.format]) || 'text',
  }), [options, schema.format]);

  // Ensure value is always a string
  const safeValue = useMemo(() => {
    if (value === null || value === undefined) return '';
    return String(value);
  }, [value]);

  const hasError = useMemo(() => {
    return Boolean(rawErrors && rawErrors.length > 0);
  }, [rawErrors]);

  const handleChange = useCallback((event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const newValue = event.target.value;
    onChange(newValue === '' ? config.emptyValue : newValue);
  }, [onChange, config.emptyValue]);

  const handleBlur = useCallback((event: React.FocusEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    onBlur(id, event.target.value);
  }, [id, onBlur]);

  const handleFocus = useCallback((event: React.FocusEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    onFocus(id, event.target.value);
  }, [id, onFocus]);

  if (config.isTextarea) {
    return (
      <Textarea
        id={id}
        placeholder={placeholder}
        disabled={disabled}
        autoFocus={autofocus}
        value={safeValue}
        required={required}
        onChange={handleChange}
        onBlur={handleBlur}
        onFocus={handleFocus}
        rows={config.rows}
        title={tooltipText}
        aria-invalid={hasError || undefined}
        className={cn(hasError && 'border-destructive', compact && 'text-xs')}
      />
    );
  }

  return (
    <Input
      id={id}
      type={config.inputType}
      placeholder={placeholder}
      disabled={disabled}
      autoFocus={autofocus}
      value={safeValue}
      required={required}
      onChange={handleChange}
      onBlur={handleBlur}
      onFocus={handleFocus}
      title={tooltipText}
      aria-invalid={hasError || undefined}
      className={cn(hasError && 'border-destructive', compact && 'h-7 text-xs')}
    />
  );
}
