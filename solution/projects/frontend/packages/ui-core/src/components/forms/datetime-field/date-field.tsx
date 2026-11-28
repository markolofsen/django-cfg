'use client';

/**
 * DateField — native `<input type="date">` engine + our skin + optional
 * `Calendar` popover. Type the date, or click the chevron to pick from the grid.
 * Wire value is `YYYY-MM-DD` (native semantics, timezone-less).
 *
 * Replaces the click-only `DatePicker` (kept as a back-compat alias).
 */

import { CalendarIcon } from 'lucide-react';
import * as React from 'react';

import { useIsTouch } from '../../../hooks/media';
import { Popover, PopoverContent, PopoverTrigger } from '../../overlay/popover';
import { Calendar } from '../../data/calendar/calendar';
import { formatDateString, parseDateString } from './date-time-utils';
import type { FieldControlSize } from '../control-size';
import { NativeFieldShell, NATIVE_FIELD_INPUT_CLASS } from './native-field-shell';
import { IconTrigger, PopoverChevron } from './popover-chevron';

export interface DateFieldProps {
  /** Value as `YYYY-MM-DD`. Controlled. */
  value?: string;
  /** Uncontrolled initial value. */
  defaultValue?: string;
  onChange?: (value: string) => void;
  disabled?: boolean;
  /** Invalid state — usually driven by the `Field` / `Form` layer. */
  invalid?: boolean;
  /** Native min/max (`YYYY-MM-DD`); also bound the calendar grid. */
  min?: string;
  max?: string;
  /**
   * Show the calendar chevron + grid.
   *
   * Default `undefined` = AUTO: shown on fine-pointer (mouse) devices, hidden on
   * coarse-pointer (touch) ones, which get the OS date wheel from the native
   * input instead — a bigger, better tap target than our mouse-first grid. Pass
   * an explicit `true`/`false` to force it.
   */
  showPopover?: boolean;
  /** Form field name — the native input IS the form control. */
  name?: string;
  /**
   * DOM id for the native control, so an external `<label htmlFor>` binds to
   * the field a user actually focuses. Without it a caller replacing a bare
   * `<input id=…>` with this component silently breaks its own label: the
   * text still renders, but clicking it focuses nothing.
   */
  id?: string;

  /** Height from the shared control ladder — same names as `Input`'s `inputSize`. */
  inputSize?: FieldControlSize;
  className?: string;
  align?: 'start' | 'center' | 'end';
  'aria-label'?: string;
}

export const DateField = React.forwardRef<HTMLInputElement, DateFieldProps>(
  (
    {
      value: controlledValue,
      defaultValue,
      onChange,
      disabled = false,
      invalid = false,
      min,
      max,
      showPopover,
      name,
      id,
      inputSize,
      className,
      align = 'start',
      'aria-label': ariaLabel,
    },
    ref,
  ) => {
    const isControlled = controlledValue !== undefined;
    const [internal, setInternal] = React.useState(defaultValue ?? '');
    const value = isControlled ? controlledValue : internal;

    const [open, setOpen] = React.useState(false);

    // AUTO popover — see the showPopover prop doc. Touch → OS date wheel.
    const isTouch = useIsTouch();
    const withPopover = showPopover ?? !isTouch;

    const commit = React.useCallback(
      (next: string) => {
        if (!isControlled) setInternal(next);
        onChange?.(next);
      },
      [isControlled, onChange],
    );

    const selected = parseDateString(value);
    const fromDate = min ? parseDateString(min) : undefined;
    const toDate = max ? parseDateString(max) : undefined;

    return (
      <Popover open={open} onOpenChange={setOpen}>
        <NativeFieldShell
          icon={
            withPopover ? (
              <PopoverTrigger asChild>
                <IconTrigger disabled={disabled} label="Open calendar">
                  <CalendarIcon aria-hidden />
                </IconTrigger>
              </PopoverTrigger>
            ) : (
              <CalendarIcon aria-hidden />
            )
          }
          iconOpensPopover={withPopover}
          invalid={invalid}
          disabled={disabled}
          inputSize={inputSize}
          className={className}
          popoverTrigger={
            withPopover ? (
              <PopoverTrigger asChild>
                <PopoverChevron disabled={disabled} label="Open calendar" />
              </PopoverTrigger>
            ) : null
          }
        >
          <input
            ref={ref}
            type="date"
            className={NATIVE_FIELD_INPUT_CLASS}
            value={value}
            onChange={(e) => commit(e.target.value)}
            disabled={disabled}
            min={min}
            max={max}
            name={name}
            id={id}
            aria-label={ariaLabel}
            aria-invalid={invalid || undefined}
          />
        </NativeFieldShell>
        {withPopover ? (
          <PopoverContent
            // Short popover (calendar only) → no height cap; let Radix flip it
            // above the field when there's no room below, rather than clipping.
            className="w-auto p-0"
            align={align}
            collisionPadding={12}
          >
            <Calendar
              mode="single"
              selected={selected}
              onSelect={(date) => {
                commit(date ? formatDateString(date) : '');
                setOpen(false);
              }}
              disabled={disabled}
              fromDate={fromDate}
              toDate={toDate}
              initialFocus
            />
          </PopoverContent>
        ) : null}
      </Popover>
    );
  },
);
DateField.displayName = 'DateField';
