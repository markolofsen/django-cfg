"use client"

import React, { useCallback, useMemo, useRef } from 'react';

import { Input } from '@djangocfg/ui-core/components';
import { cn } from '@djangocfg/ui-core/lib';
import { useAppT } from '@djangocfg/i18n';
import { WidgetProps } from '@rjsf/utils';

import { useWidgetEnv } from './_useWidgetEnv';

/**
 * Color input widget for JSON Schema Form.
 *
 * Supports HSL format (h s% l%) and HEX format. Click on the color box
 * to open the native color picker directly. Honors `density` and
 * `ui:disabledWhen` via `useWidgetEnv`.
 */
export function ColorWidget(props: WidgetProps) {
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
    rawErrors,
  } = props;
  const { disabled, compact, tooltipText } = useWidgetEnv(props);

  const t = useAppT();
  const pickColorLabel = useMemo(() => t('tools.color.pick'), [t]);
  const colorInputRef = useRef<HTMLInputElement>(null);

  // Determine format from options or auto-detect from value
  const format = useMemo(() => {
    if (options?.format) return options.format as 'hsl' | 'hex';
    if (typeof value === 'string' && value.startsWith('#')) return 'hex';
    return 'hsl';
  }, [options?.format, value]);

  // Ensure value is always a string
  const safeValue = useMemo(() => {
    if (value === null || value === undefined) return '';
    return String(value);
  }, [value]);

  // Convert HSL string (like "217 91% 60%") to CSS hsl() value
  const hslToCss = useCallback((hslValue: string): string => {
    if (!hslValue) return 'transparent';
    if (hslValue.startsWith('#')) return hslValue;
    if (hslValue.startsWith('hsl')) return hslValue;
    // Format: "h s% l%" -> "hsl(h, s%, l%)"
    const parts = hslValue.split(' ');
    if (parts.length === 3) {
      return `hsl(${parts[0]}, ${parts[1]}, ${parts[2]})`;
    }
    return 'transparent';
  }, []);

  // Convert CSS color to preview color
  const previewColor = useMemo(() => {
    return hslToCss(safeValue);
  }, [safeValue, hslToCss]);

  // Convert hex to HSL string for internal storage
  const hexToHsl = useCallback((hex: string): string => {
    // Remove # if present
    hex = hex.replace('#', '');

    // Parse hex values
    const r = parseInt(hex.substring(0, 2), 16) / 255;
    const g = parseInt(hex.substring(2, 4), 16) / 255;
    const b = parseInt(hex.substring(4, 6), 16) / 255;

    const max = Math.max(r, g, b);
    const min = Math.min(r, g, b);
    let h = 0;
    let s = 0;
    const l = (max + min) / 2;

    if (max !== min) {
      const d = max - min;
      s = l > 0.5 ? d / (2 - max - min) : d / (max + min);

      switch (max) {
        case r:
          h = ((g - b) / d + (g < b ? 6 : 0)) / 6;
          break;
        case g:
          h = ((b - r) / d + 2) / 6;
          break;
        case b:
          h = ((r - g) / d + 4) / 6;
          break;
      }
    }

    return `${Math.round(h * 360)} ${Math.round(s * 100)}% ${Math.round(l * 100)}%`;
  }, []);

  // Convert HSL to hex
  const hslToHex = useCallback((hslValue: string): string => {
    if (!hslValue || hslValue.startsWith('#')) return hslValue || '#000000';

    const parts = hslValue.split(' ');
    if (parts.length !== 3) return '#000000';

    const [hPart, sPart, lPart] = parts;
    // Guaranteed by the length check above; the destructure just does not narrow.
    if (hPart === undefined || sPart === undefined || lPart === undefined) return '#000000';

    const h = parseInt(hPart) / 360;
    const s = parseInt(sPart.replace('%', '')) / 100;
    const l = parseInt(lPart.replace('%', '')) / 100;

    const hue2rgb = (p: number, q: number, t: number) => {
      if (t < 0) t += 1;
      if (t > 1) t -= 1;
      if (t < 1/6) return p + (q - p) * 6 * t;
      if (t < 1/2) return q;
      if (t < 2/3) return p + (q - p) * (2/3 - t) * 6;
      return p;
    };

    let r, g, b;
    if (s === 0) {
      r = g = b = l;
    } else {
      const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
      const p = 2 * l - q;
      r = hue2rgb(p, q, h + 1/3);
      g = hue2rgb(p, q, h);
      b = hue2rgb(p, q, h - 1/3);
    }

    const toHex = (x: number) => {
      const hex = Math.round(x * 255).toString(16);
      return hex.length === 1 ? '0' + hex : hex;
    };

    return `#${toHex(r)}${toHex(g)}${toHex(b)}`;
  }, []);

  const hasError = useMemo(() => {
    return rawErrors && rawErrors.length > 0;
  }, [rawErrors]);

  const handleChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = event.target.value;
    onChange(newValue);
  }, [onChange]);

  const handleColorPickerChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const hexValue = event.target.value;
    if (format === 'hsl') {
      onChange(hexToHsl(hexValue));
    } else {
      onChange(hexValue);
    }
  }, [onChange, format, hexToHsl]);

  const handleBlur = useCallback((event: React.FocusEvent<HTMLInputElement>) => {
    onBlur(id, event.target.value);
  }, [id, onBlur]);

  const handleFocus = useCallback((event: React.FocusEvent<HTMLInputElement>) => {
    onFocus(id, event.target.value);
  }, [id, onFocus]);

  // Get hex value for native color picker
  const hexValue = useMemo(() => {
    if (format === 'hex' || safeValue.startsWith('#')) {
      return safeValue || '#000000';
    }
    return hslToHex(safeValue);
  }, [safeValue, format, hslToHex]);

  // Click on color box opens native color picker
  const handleColorBoxClick = useCallback(() => {
    if (!disabled) {
      colorInputRef.current?.click();
    }
  }, [disabled]);

  return (
    <div className="flex items-center gap-2">
      {/* Color preview box - clicking opens native picker */}
      <div className="relative">
        <button
          type="button"
          onClick={handleColorBoxClick}
          disabled={disabled}
          className={cn(
            'shrink-0 rounded-md border-2 border-input cursor-pointer hover:border-ring focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
            compact ? 'h-7 w-7' : 'h-10 w-10',
          )}
          style={{ backgroundColor: previewColor }}
          aria-label={pickColorLabel}
        />
        {/* Hidden native color input */}
        <input
          ref={colorInputRef}
          type="color"
          value={hexValue}
          onChange={handleColorPickerChange}
          className="absolute inset-0 opacity-0 w-full h-full cursor-pointer"
          disabled={disabled}
          tabIndex={-1}
        />
      </div>

      {/* Text input for manual HSL/HEX entry */}
      <Input
        id={id}
        type="text"
        placeholder={placeholder || (format === 'hsl' ? '217 91% 60%' : '#3b82f6')}
        disabled={disabled}
        autoFocus={autofocus}
        value={safeValue}
        required={required}
        onChange={handleChange}
        onBlur={handleBlur}
        onFocus={handleFocus}
        title={tooltipText}
        aria-invalid={hasError || undefined}
        className={cn('flex-1 font-mono text-sm', hasError && 'border-destructive', compact && 'h-7 text-xs')}
      />
    </div>
  );
}
