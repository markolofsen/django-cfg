'use client';

/**
 * NativeFieldShell — the shared visual layer for the native-engine date/time
 * fields (`DateField`, `TimeField`, `DateTimeField`).
 *
 * The strategy (see @dev/planned/ui-core-datetime-fields/PLAN.md): the browser's
 * native `<input type="date|time|datetime-local">` is the *input engine* — it
 * gives segmented keyboard entry, locale-aware order, 12/24h, arrow-key
 * increment, screen-reader support, and OS wheels on mobile for free. This shell
 * owns everything the native input CANNOT do to our standard: the token-styled
 * box (`bg-input`, `border-border`, `--ring` focus, `--radius`), a leading
 * lucide icon, invalid/disabled states, and an OPTIONAL trailing popover trigger
 * for pointer users.
 *
 * The native browser indicator (the clock/calendar glyph) is suppressed via
 * `native-datetime-input` (see datetime-field.css) so there is exactly one
 * icon — ours — and one picker — ours. Typing in the field and opening the
 * popover both write the same value.
 */

import * as React from 'react';

import { cn } from '../../../lib/utils';
import { CONTROL_SIZE, type FieldControlSize } from '../control-size';

export interface NativeFieldShellProps {
  /** Leading icon (lucide element). */
  icon?: React.ReactNode;
  /**
   * When true, the leading icon is a real, sizeable click target that opens the
   * popover — not a decorative glyph. The field wraps the shell in a
   * `PopoverTrigger asChild` around the icon so tapping the icon (a much bigger,
   * left-edge target than the small chevron) opens the picker. The centre of the
   * field still belongs to the native `<input>` for typing.
   */
  iconOpensPopover?: boolean;
  /** Invalid state — wires `aria-invalid` and a destructive border. Usually
   *  driven by the surrounding `Field` / `Form` layer. */
  invalid?: boolean;
  disabled?: boolean;
  /** Height from the shared control ladder — same names as `Input`'s `inputSize`. */
  inputSize?: FieldControlSize;
  className?: string;
  /** The native `<input>` element, already typed and wired by the field. */
  children: React.ReactNode;
  /**
   * Optional popover affordance. When provided, a trailing chevron button is
   * shown; `open`/`onOpenChange` are controlled by the field so the icon and
   * the button share one popover.
   */
  popoverTrigger?: React.ReactNode;
}

/**
 * The class applied to the native `<input>` INSIDE the shell. Mirrors the
 * standard `Input` surface/focus (bg-input, border, --ring) but drops the
 * focus ring here — the ring is drawn on the shell so it wraps the icon and
 * popover button too, reading as one control.
 */
export const NATIVE_FIELD_INPUT_CLASS = cn(
  'native-datetime-input',
  'peer w-full bg-transparent text-base md:text-sm outline-none',
  'text-foreground placeholder:text-muted-foreground',
  'disabled:cursor-not-allowed',
  // Empty native date/time inputs render their placeholder segments muted so an
  // unset field reads like a placeholder, not a value.
  '[&:invalid]:text-muted-foreground',
);

/**
 * The outer box. Draws the token surface + the crisp `--ring` focus edge when
 * anything inside is focused (`focus-within`), matching the standard Input's
 * sharp Vercel/Linear look rather than a blurry halo.
 */
export const NativeFieldShell = React.forwardRef<HTMLDivElement, NativeFieldShellProps>(
  ({ icon, iconOpensPopover, invalid, disabled, inputSize = 'default', className, children, popoverTrigger }, ref) => {
    return (
      <div
        ref={ref}
        data-invalid={invalid ? '' : undefined}
        data-disabled={disabled ? '' : undefined}
        aria-invalid={invalid || undefined}
        className={cn(
          CONTROL_SIZE[inputSize].height,
          'flex w-full items-center gap-2 rounded-[var(--radius)] border bg-input px-3 shadow-sm',
          'transition-[color,background-color,border-color,box-shadow]',
          'border-border',
          // Crisp focus edge on the whole shell (border + 1px ring = ~2px clean
          // outline). `:focus-within` so it lights whether the user tabs into
          // the input or the popover button.
          'focus-within:border-ring focus-within:ring-1 focus-within:ring-ring',
          invalid &&
            'border-destructive focus-within:border-destructive focus-within:ring-destructive',
          disabled && 'cursor-not-allowed opacity-50',
          className,
        )}
      >
        {icon ? (
          <span
            className={cn(
              'flex shrink-0 text-muted-foreground [&_svg]:size-4',
              // Decorative by default (clicks fall through to the input). When
              // the icon is a real popover trigger, it must receive clicks.
              !iconOpensPopover && 'pointer-events-none',
            )}
          >
            {icon}
          </span>
        ) : null}
        {children}
        {popoverTrigger}
      </div>
    );
  },
);
NativeFieldShell.displayName = 'NativeFieldShell';
