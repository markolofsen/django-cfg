'use client';

/**
 * DateTimeField — the combined date+time field that ui-core was missing. Native
 * `<input type="datetime-local">` engine + our skin; the popover pairs the
 * `Calendar` grid with the time columns so a scheduler UI is one control, not a
 * hand-wired DatePicker + TimePicker.
 *
 * Wire value is `YYYY-MM-DDTHH:mm` (native `datetime-local` semantics,
 * timezone-less wall-clock).
 */

import { CalendarClock, Clock } from 'lucide-react';
import * as React from 'react';

import { cn } from '../../../lib/utils';
import { CONTROL_SIZE, type FieldControlSize } from '../control-size';
import { useIsTouch } from '../../../hooks/media';
import { Popover, PopoverContent, PopoverTrigger } from '../../overlay/popover';
import { Calendar } from '../../data/calendar/calendar';
import {
  formatDateString,
  joinDateTime,
  parseDateString,
  splitDateTime,
} from './date-time-utils';
import { NativeFieldShell, NATIVE_FIELD_INPUT_CLASS } from './native-field-shell';
import { IconTrigger, PopoverChevron } from './popover-chevron';

export interface DateTimeFieldProps {
  /** Value as `YYYY-MM-DDTHH:mm`. Controlled. */
  value?: string;
  /** Uncontrolled initial value. */
  defaultValue?: string;
  onChange?: (value: string) => void;
  disabled?: boolean;
  /** Invalid state — usually driven by the `Field` / `Form` layer. */
  invalid?: boolean;
  /** Native min/max (`YYYY-MM-DDTHH:mm`). */
  min?: string;
  max?: string;
  /**
   * Show the popover chevron + combined calendar/time picker.
   *
   * Default `undefined` = AUTO: shown on fine-pointer (mouse) devices, hidden on
   * coarse-pointer (touch) ones. On touch the native `datetime-local` input
   * opens the OS date+time wheel — a better tap target than our tall combined
   * grid, which is also the hardest of the three to fit on a small screen. Pass
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

export const DateTimeField = React.forwardRef<HTMLInputElement, DateTimeFieldProps>(
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

    // AUTO popover — see the showPopover prop doc. Touch → OS date+time wheel.
    const isTouch = useIsTouch();
    const withPopover = showPopover ?? !isTouch;

    const commit = React.useCallback(
      (next: string) => {
        if (!isControlled) setInternal(next);
        onChange?.(next);
      },
      [isControlled, onChange],
    );

    const { date, time } = splitDateTime(value);
    const selected = parseDateString(date);

    return (
      <Popover open={open} onOpenChange={setOpen}>
        <NativeFieldShell
          icon={
            withPopover ? (
              <PopoverTrigger asChild>
                <IconTrigger disabled={disabled} label="Open date & time picker">
                  <CalendarClock aria-hidden />
                </IconTrigger>
              </PopoverTrigger>
            ) : (
              <CalendarClock aria-hidden />
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
                <PopoverChevron disabled={disabled} label="Open date & time picker" />
              </PopoverTrigger>
            ) : null
          }
        >
          <input
            ref={ref}
            type="datetime-local"
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
          // The official shadcn-2026 shape: the popover holds ONLY the calendar
          // (date), and time is a small NATIVE `<input type="time">` beneath it.
          // No scroll columns — those were the source of the pill/height/width
          // churn. `align="start"` (not `align` default center) is what stops
          // the popover sliding off the right edge on a narrow surface; Radix
          // still auto-flips on collision. `w-auto p-0` sizes to the calendar.
          <PopoverContent
            // `w-auto` sizes to the calendar; `align="start"` keeps it under the
            // left edge so it doesn't slide off-screen. NO `maxHeight` cap here:
            // the calendar + time input is a SHORT popover, and
            // `--radix-popover-content-available-height` is the gap from the
            // trigger to the viewport edge — when the field sits low on screen
            // that gap is tiny, so the cap was CLIPPING the calendar (and the
            // time row under it). Instead we let Radix's default avoidCollisions
            // flip the whole popover ABOVE the field when there's no room below.
            // `collisionPadding` just keeps it off the very edge.
            className="w-auto p-0"
            align={align}
            collisionPadding={12}
          >
            <Calendar
              mode="single"
              selected={selected}
              onSelect={(picked) => {
                // Keep the time; swap the date. Default to 00:00 on a first pick
                // of an empty field so the result is a valid datetime.
                const nextDate = picked ? formatDateString(picked) : '';
                commit(joinDateTime(nextDate, time || '00:00'));
              }}
              disabled={disabled}
              initialFocus
            />
            {/* Time row: a full, comfortable field — not a cramped chip. The
              * label + clock icon sit left; the native time input fills the
              * rest at the default control height so it's an easy
              * tap/click target and reads as a real input. */}
            <div className="flex items-center gap-2 border-t p-3">
              <Clock className="size-4 shrink-0 text-muted-foreground" aria-hidden />
              <span className="text-sm font-medium text-muted-foreground">Time</span>
              <input
                type="time"
                aria-label="Time"
                // Explicit width, not min-w on a flex — a native `<input>` is a
                // replaced element and won't reliably grow to a flex min-width,
                // which is why the earlier `min-w-[8rem]` did nothing. A fixed
                // width + centered segments gives the value real breathing room.
                style={{ width: '8.5rem' }}
                className={cn(
                  // `--center` variant centers the native segments (see
                  // datetime-field.css); it sets its own display/justify.
                  'native-datetime-input native-datetime-input--center ml-auto rounded-[var(--radius)]',
                  CONTROL_SIZE.default.height,
                  'border border-border bg-input px-4 text-base tabular-nums text-foreground shadow-sm md:text-sm',
                  'focus-visible:border-ring focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring',
                  'disabled:cursor-not-allowed disabled:opacity-50',
                )}
                value={time}
                onChange={(e) => commit(joinDateTime(date, e.target.value))}
                disabled={disabled}
              />
            </div>
          </PopoverContent>
        ) : null}
      </Popover>
    );
  },
);
DateTimeField.displayName = 'DateTimeField';
