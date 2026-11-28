"use client"

import React, { useCallback, useMemo } from 'react';

import { Input, Slider } from '@djangocfg/ui-core/components';
import { cn } from '@djangocfg/ui-core/lib';
import { WidgetProps } from '@rjsf/utils';

import { useWidgetEnv } from './_useWidgetEnv';

/**
 * Slider widget for JSON Schema Form
 *
 * Supports:
 * - number/integer types
 * - min/max from schema
 * - step from schema or options
 * - unit suffix (e.g., "rem", "px", "%")
 * - optional text input for precise values
 *
 * Usage in uiSchema:
 * ```json
 * {
 *   "radius": {
 *     "ui:widget": "slider",
 *     "ui:options": {
 *       "unit": "rem",
 *       "showInput": true,
 *       "step": 0.125
 *     }
 *   }
 * }
 * ```
 */
export function SliderWidget(props: WidgetProps) {
  const {
    id,
    value,
    onChange,
    schema,
    options,
    rawErrors,
  } = props;
  const { disabled, tooltipText } = useWidgetEnv(props);

  // Extract configuration
  const config = useMemo(() => {
    const min = schema.minimum ?? options?.min ?? 0;
    const max = schema.maximum ?? options?.max ?? 100;
    const step = options?.step ?? (schema.type === 'integer' ? 1 : 0.1);
    const unit = options?.unit as string | undefined;
    const showInput = options?.showInput !== false; // default true

    return { min, max, step, unit, showInput };
  }, [schema, options]);

  // Parse value - handle string values like "0.5rem". The result is
  // clamped to [min, max] so an out-of-range value never pushes the
  // Radix thumb off the track.
  const numericValue = useMemo(() => {
    const clamp = (n: number) => Math.min(config.max, Math.max(config.min, n));
    if (value === null || value === undefined || value === '') {
      return config.min;
    }
    if (typeof value === 'number') {
      return isNaN(value) ? config.min : clamp(value);
    }
    if (typeof value === 'string') {
      // Extract number from string like "0.5rem"
      const parsed = parseFloat(value);
      return isNaN(parsed) ? config.min : clamp(parsed);
    }
    return config.min;
  }, [value, config.min, config.max]);

  const hasError = useMemo(() => {
    return rawErrors && rawErrors.length > 0;
  }, [rawErrors]);

  // Handle slider change
  const handleSliderChange = useCallback((values: number[]) => {
    const newValue = values[0];
    if (config.unit) {
      onChange(`${newValue}${config.unit}`);
    } else {
      onChange(newValue);
    }
  }, [onChange, config.unit]);

  // Handle text input change
  const handleInputChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const inputValue = event.target.value;

    // If has unit, just store raw value with unit
    if (config.unit) {
      // Remove unit if user typed it, then add it back
      const cleanValue = inputValue.replace(config.unit, '').trim();
      const parsed = parseFloat(cleanValue);
      if (!isNaN(parsed)) {
        onChange(`${parsed}${config.unit}`);
      } else if (inputValue === '') {
        onChange(`${config.min}${config.unit}`);
      }
    } else {
      const parsed = parseFloat(inputValue);
      onChange(isNaN(parsed) ? config.min : parsed);
    }
  }, [onChange, config.unit, config.min]);

  // Display value with unit
  const displayValue = useMemo(() => {
    if (config.unit) {
      return `${numericValue}${config.unit}`;
    }
    return String(numericValue);
  }, [numericValue, config.unit]);

  return (
    <div
      className={cn('flex items-center gap-3', hasError && 'text-destructive')}
      title={tooltipText}
    >
      {/* Slider */}
      <Slider
        id={id}
        disabled={disabled}
        value={[numericValue]}
        onValueChange={handleSliderChange}
        min={config.min}
        max={config.max}
        step={config.step}
        className="flex-1"
      />

      {/* Value input or display */}
      {config.showInput ? (
        <Input
          type="text"
          value={displayValue}
          onChange={handleInputChange}
          disabled={disabled}
          readOnly={disabled}
          className={cn(
            'w-20 text-center font-mono text-sm',
            hasError && 'border-destructive'
          )}
        />
      ) : (
        <span className="w-16 text-right font-mono text-sm text-muted-foreground">
          {displayValue}
        </span>
      )}
    </div>
  );
}
