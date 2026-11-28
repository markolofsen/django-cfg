"use client"

import React, { useCallback, useMemo } from 'react';

import {
    Select, SelectContent, SelectItem, SelectTrigger, SelectValue
} from '@djangocfg/ui-core/components';
import { EnumOptionsType, WidgetProps } from '@rjsf/utils';

import { useWidgetEnv } from './_useWidgetEnv';

/**
 * Select dropdown widget for JSON Schema Form
 * Handles enum fields
 */
export function SelectWidget(props: WidgetProps) {
  const {
    id,
    options,
    value,
    required,
    autofocus,
    onChange,
    onBlur,
    onFocus,
    placeholder,
    rawErrors,
  } = props;
  const { disabled, compact, tooltipText } = useWidgetEnv(props);

  // Safely extract and validate enum options
  const enumOptions = useMemo<EnumOptionsType[]>(() => {
    const opts = options?.enumOptions;
    if (!Array.isArray(opts)) return [];
    return opts.filter((opt) => opt && opt.value !== undefined);
  }, [options]);

  const hasError = useMemo(() => {
    return rawErrors && rawErrors.length > 0;
  }, [rawErrors]);

  // Empty-string enum values are handled by the ui-core <Select> wrapper
  // (which substitutes a Radix-safe sentinel internally), so we can pass
  // values through verbatim here.
  const safeValue = useMemo(() => {
    if (value === null || value === undefined) return '';
    return String(value);
  }, [value]);

  const handleChange = useCallback((newValue: string) => {
    onChange(newValue);
    onBlur(id, newValue);
  }, [onChange, onBlur, id]);

  // If no enum options, render a text input instead
  // This handles cases like anyOf/oneOf where RJSF might incorrectly use SelectWidget
  if (enumOptions.length === 0) {
    return (
      <input
        id={id}
        type="text"
        value={safeValue}
        onChange={(e) => onChange(e.target.value)}
        onBlur={(e) => onBlur(id, e.target.value)}
        onFocus={(e) => onFocus(id, e.target.value)}
        disabled={disabled}
        readOnly={disabled}
        title={tooltipText}
        aria-invalid={hasError || undefined}
        className={`flex h-10 w-full rounded-md border ${
          hasError ? 'border-destructive' : 'border-input'
        } bg-transparent px-3 py-2 text-base shadow-sm transition-colors placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 md:text-sm`}
        placeholder={placeholder}
      />
    );
  }

  return (
    <Select
      value={safeValue}
      onValueChange={handleChange}
      disabled={disabled}
      required={required}
    >
      <SelectTrigger
        id={id}
        className={`${hasError ? 'border-destructive' : ''} ${compact ? 'h-7 text-xs' : ''}`.trim()}
        autoFocus={autofocus}
        onFocus={() => onFocus(id, value)}
        title={tooltipText}
      >
        <SelectValue placeholder={placeholder || 'Select an option'} />
      </SelectTrigger>
      <SelectContent>
        {enumOptions.map((option) => {
          const optValue = String(option.value);
          return (
            <SelectItem key={optValue || '__empty__'} value={optValue}>
              {option.label || optValue}
            </SelectItem>
          );
        })}
      </SelectContent>
    </Select>
  );
}
