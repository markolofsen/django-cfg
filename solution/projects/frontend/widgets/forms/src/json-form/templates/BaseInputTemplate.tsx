"use client"

import React, { ChangeEvent, FocusEvent, useCallback, useMemo } from 'react';

import { Input } from '@djangocfg/ui-core/components';
import { cn } from '@djangocfg/ui-core/lib';
import { getInputProps, WidgetProps } from '@rjsf/utils';

import { useWidgetEnv } from '../widgets/_useWidgetEnv';

/**
 * Base input template for JSON Schema Form
 *
 * This template is CRITICAL for rendering primitive types (string, number)
 * inside arrays. Without it, array items with primitive types will render
 * as empty containers.
 *
 * RJSF uses this template for:
 * - Array items with primitive types (e.g., array of strings)
 * - Fields without explicit widget mapping
 * - All text-based widgets internally
 *
 * @see https://rjsf-team.github.io/react-jsonschema-form/docs/advanced-customization/custom-templates/#baseinputtemplate
 */
export function BaseInputTemplate(props: WidgetProps) {
  const {
    id,
    type,
    value,
    autofocus,
    onBlur,
    onFocus,
    onChange,
    options,
    schema,
    rawErrors,
    placeholder,
  } = props;
  const { disabled, compact, tooltipText } = useWidgetEnv(props);

  // Get input props from RJSF utils (handles step, min, max, etc.)
  const inputProps = useMemo(() => {
    return getInputProps(schema, type, options);
  }, [schema, type, options]);

  // Safely convert value to string for input
  const safeValue = useMemo(() => {
    if (value === null || value === undefined) return '';
    return String(value);
  }, [value]);

  const hasError = useMemo(() => {
    return rawErrors && rawErrors.length > 0;
  }, [rawErrors]);

  // Handle text change - transform empty strings based on schema type
  const handleChange = useCallback((event: ChangeEvent<HTMLInputElement>) => {
    const val = event.target.value;

    // Empty value handling
    if (val === '') {
      onChange(options?.emptyValue ?? '');
      return;
    }

    // Number type conversion
    if (inputProps.type === 'number' || schema.type === 'number' || schema.type === 'integer') {
      const num = Number(val);
      onChange(isNaN(num) ? val : num);
      return;
    }

    onChange(val);
  }, [onChange, inputProps.type, schema.type, options?.emptyValue]);

  const handleBlur = useCallback((event: FocusEvent<HTMLInputElement>) => {
    onBlur(id, event.target.value);
  }, [id, onBlur]);

  const handleFocus = useCallback((event: FocusEvent<HTMLInputElement>) => {
    onFocus(id, event.target.value);
  }, [id, onFocus]);

  // Determine input type
  const inputType = useMemo(() => {
    if (inputProps.type) return inputProps.type;
    if (schema.type === 'number' || schema.type === 'integer') return 'number';
    return 'text';
  }, [inputProps.type, schema.type]);

  return (
    <Input
      id={id}
      type={inputType}
      value={safeValue}
      disabled={disabled}
      autoFocus={autofocus}
      onChange={handleChange}
      onBlur={handleBlur}
      onFocus={handleFocus}
      placeholder={placeholder}
      title={tooltipText}
      aria-invalid={hasError || undefined}
      className={cn(hasError && 'border-destructive', compact && 'h-7 text-xs')}
      step={inputProps.step}
      min={inputProps.min}
      max={inputProps.max}
    />
  );
}
