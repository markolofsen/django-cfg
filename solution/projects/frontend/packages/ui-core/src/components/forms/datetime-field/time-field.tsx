'use client';

/**
 * TimeField — native `<input type="time">` in our token skin. Type `14:30`
 * straight in (segmented keyboard entry, arrow increment); on touch the OS time
 * wheel opens on tap. AM/PM vs 24-hour is decided by the browser from the user's
 * locale — we don't render our own picker, so there's nothing to desync.
 *
 * Wire value is `HH:mm` (24h) — or `HH:mm:ss` when `step` yields seconds —
 * matching the native input and the old `TimePicker` contract, so migration from
 * the click-only `TimePicker` (kept as a back-compat alias) is mechanical.
 */

import { Clock } from 'lucide-react';
import * as React from 'react';

import type { FieldControlSize } from '../control-size';
import { NativeFieldShell, NATIVE_FIELD_INPUT_CLASS } from './native-field-shell';

export interface TimeFieldProps {
  /** Value as `HH:mm` (24h). Controlled. */
  value?: string;
  /** Uncontrolled initial value. */
  defaultValue?: string;
  onChange?: (value: string) => void;
  disabled?: boolean;
  /** Invalid state — usually driven by the `Field` / `Form` layer. */
  invalid?: boolean;
  /** Native min/max (`HH:mm`). */
  min?: string;
  max?: string;
  /**
   * Native `step` in seconds. `60` (default) → HH:mm; smaller values expose a
   * seconds segment. Controls the arrow-key increment too.
   */
  step?: number;
  /** Form field name — the native input IS the form control. */
  name?: string;
  /**
   * DOM id for the native control, so an external `<label htmlFor>` binds to
   * the field a user actually focuses.
   */
  id?: string;
  /** Height from the shared control ladder — same names as `Input`'s `inputSize`. */
  inputSize?: FieldControlSize;
  className?: string;
  'aria-label'?: string;
}

export const TimeField = React.forwardRef<HTMLInputElement, TimeFieldProps>(
  (
    {
      value: controlledValue,
      defaultValue,
      onChange,
      disabled = false,
      invalid = false,
      min,
      max,
      step,
      name,
      id,
      inputSize,
      className,
      'aria-label': ariaLabel,
    },
    ref,
  ) => {
    const isControlled = controlledValue !== undefined;
    const [internal, setInternal] = React.useState(defaultValue ?? '');
    const value = isControlled ? controlledValue : internal;

    const commit = React.useCallback(
      (next: string) => {
        if (!isControlled) setInternal(next);
        onChange?.(next);
      },
      [isControlled, onChange],
    );

    return (
      <NativeFieldShell
        icon={<Clock aria-hidden />}
        invalid={invalid}
        disabled={disabled}
        inputSize={inputSize}
        className={className}
      >
        <input
          ref={ref}
          type="time"
          className={NATIVE_FIELD_INPUT_CLASS}
          value={value}
          onChange={(e) => commit(e.target.value)}
          disabled={disabled}
          min={min}
          max={max}
          step={step}
          name={name}
          id={id}
          aria-label={ariaLabel}
          aria-invalid={invalid || undefined}
        />
      </NativeFieldShell>
    );
  },
);
TimeField.displayName = 'TimeField';
