"use client"

import * as React from 'react';

import { cn } from '../../../lib/utils';
import { InputGroup, InputGroupAddon, InputGroupInput } from '../input-group';

// =============================================================================
// Money model
// =============================================================================

/**
 * Currencies with no minor unit — ¥500 is five hundred yen, not five yen.
 *
 * Formatting one of these with two decimals inflates every amount by 100×,
 * which reads as a plausible price rather than as an error. The list mirrors
 * `@djangocfg/payments`' `domain/money.ts`; it is duplicated rather than
 * imported because `ui-core` sits BELOW `payments` and may not depend on it.
 */
const ZERO_DECIMAL_CURRENCIES = new Set([
  'BIF', 'CLP', 'DJF', 'GNF', 'JPY', 'KMF', 'KRW', 'MGA',
  'PYG', 'RWF', 'UGX', 'VND', 'VUV', 'XAF', 'XOF', 'XPF',
]);

/** Minor units per major unit for a currency — 100 for USD, 1 for JPY. */
export function minorUnitFactor(currency: string): number {
  return ZERO_DECIMAL_CURRENCIES.has(currency.toUpperCase()) ? 1 : 100;
}

/** Digits after the decimal separator for a currency. */
export function currencyFractionDigits(currency: string): number {
  return ZERO_DECIMAL_CURRENCIES.has(currency.toUpperCase()) ? 0 : 2;
}

// =============================================================================
// Locale probing
// =============================================================================

// A `localeParts()` helper used to probe the group/decimal separators by hand.
// It is gone: nothing parses separators any more. Input is digits-only
// (`parseToMinor`) and output goes straight through `Intl.NumberFormat`
// (`formatMinor`), so the locale's separators never have to be named.

/** The currency's symbol in this locale, e.g. "$", "€", "¥". */
function currencySymbol(currency: string, locale: string | undefined): string {
  try {
    const parts = new Intl.NumberFormat(locale, {
      style: 'currency',
      currency: currency.toUpperCase(),
    }).formatToParts(0);
    return parts.find((p) => p.type === 'currency')?.value ?? currency.toUpperCase();
  } catch {
    // Unknown code — show it as-is rather than throwing inside a render.
    return currency.toUpperCase();
  }
}

// =============================================================================
// Format / parse
// =============================================================================

/** Minor units per major unit for a given precision — 100 at two digits, 1 at none. */
function factorFor(digits: number): number {
  return 10 ** digits;
}

/** Format minor units for display, grouped and with the locale's separators. */
function formatMinor(
  minor: number,
  digits: number,
  locale: string | undefined,
): string {
  return new Intl.NumberFormat(locale, {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
    useGrouping: true,
  }).format(minor / factorFor(digits));
}

/**
 * Read minor units out of whatever the user typed.
 *
 * Digits-only, right-anchored: the last `fractionDigits` digits are the minor
 * part. Typing "5" in USD means $0.05, "550" means $5.50 — the till-style
 * entry people expect from a money field, and the reason the caret never has
 * to sit "before the decimal point".
 */
function parseToMinor(raw: string): number {
  const digits = raw.replace(/\D/g, '');
  if (!digits) return 0;
  // Number, not parseInt: 16 digits of cents is past MAX_SAFE_INTEGER, and
  // silently truncating someone's amount is worse than clamping it.
  const value = Number(digits);
  return Number.isFinite(value) ? value : 0;
}

/** Count digits in `text` up to `index` — the caret anchor that survives regrouping. */
function digitsBefore(text: string, index: number): number {
  let n = 0;
  for (let i = 0; i < index && i < text.length; i += 1) {
    if (text[i] !== undefined && /\d/.test(text[i] as string)) n += 1;
  }
  return n;
}

/** Inverse of `digitsBefore`: the offset just after the nth digit. */
function offsetAfterDigits(text: string, digitCount: number): number {
  if (digitCount <= 0) return 0;
  let seen = 0;
  for (let i = 0; i < text.length; i += 1) {
    if (text[i] !== undefined && /\d/.test(text[i] as string)) {
      seen += 1;
      if (seen === digitCount) return i + 1;
    }
  }
  return text.length;
}

// =============================================================================
// Component
// =============================================================================

export interface MoneyFieldProps
  extends Omit<
    React.ComponentProps<'input'>,
    'value' | 'defaultValue' | 'onChange' | 'prefix' | 'type'
  > {
  /**
   * Amount in MINOR UNITS — cents, not dollars.
   *
   * Money never crosses a boundary as a float here. `19.99` is not
   * representable in binary floating point, so a column of them drifts; `1999`
   * is exact. This matches `@djangocfg/payments`, which moves `MinorUnits`
   * for the same reason, so a value goes from this field to a charge with no
   * conversion in between.
   */
  value?: number;
  /** Uncontrolled initial amount, also in minor units. */
  defaultValue?: number;
  /** Called with the new amount in minor units. */
  onValueChange?: (minorUnits: number) => void;
  /** ISO 4217 code — drives the symbol, the decimals and the minor-unit factor. */
  currency?: string;
  /**
   * Digits after the decimal separator, overriding the currency's own.
   *
   * The default is right for money that is paid: a price, an invoice, a
   * charge. It is wrong for money that is merely large — a property asking
   * price, a valuation, a budget — where the cents are always two zeros the
   * reader has to look past and two keystrokes they have to type, since entry
   * is right-anchored.
   *
   * `0` makes the field whole-unit: `value` is then dollars rather than cents,
   * and typing "1400000" reads as 1,400,000. The unit of `value` always
   * follows this — minor units at 2, major units at 0 — so a caller that
   * changes it must change what it stores.
   */
  fractionDigits?: number;
  /** BCP 47 tag for separators and symbol placement. Defaults to the runtime's. */
  locale?: string;
  /** Show the currency symbol before the input. Set false when the label carries it. */
  showSymbol?: boolean;
  /** Largest accepted amount, in minor units. Entry beyond it is ignored. */
  max?: number;
  /** Applied to the group, so callers can size the whole control. */
  groupClassName?: string;
}

/**
 * An amount input that formats as you type and reports MINOR UNITS.
 *
 * ```tsx
 * const [price, setPrice] = React.useState(1999);   // $19.99
 * <MoneyField currency="USD" value={price} onValueChange={setPrice} />
 * ```
 *
 * Three decisions worth knowing, because each is a common way this component
 * is got wrong:
 *
 * **The value is an integer.** A money field that hands back `19.99` hands
 * back a number that does not exist in binary floating point. Totals drift by
 * a cent, and the bug surfaces in an invoice rather than in a test.
 *
 * **Entry is till-style and right-anchored.** Every keystroke rewrites the
 * whole display, so digits fill from the right: "1", "19", "199" → $1.99. The
 * caret is then restored by DIGIT COUNT, not by string offset — inserting a
 * thousands separator shifts every character after it, and an offset-based
 * restore is exactly why so many currency inputs jump the cursor when a
 * number crosses 1,000.
 *
 * **Separators come from `Intl`, not from a constant.** The decimal mark is a
 * comma across most of Europe. Guessing it means "1.234" is read as either
 * 1.234 or 1234 depending on where the user is, with nothing on screen to say
 * which happened.
 */
const MoneyField = React.forwardRef<HTMLInputElement, MoneyFieldProps>(
  (
    {
      value,
      defaultValue,
      onValueChange,
      currency = 'USD',
      fractionDigits,
      locale,
      showSymbol = true,
      max,
      className,
      groupClassName,
      onBlur,
      disabled,
      ...props
    },
    forwardedRef,
  ) => {
    const inputRef = React.useRef<HTMLInputElement>(null);
    React.useImperativeHandle(forwardedRef, () => inputRef.current as HTMLInputElement);

    const isControlled = value !== undefined;
    const [internal, setInternal] = React.useState<number>(defaultValue ?? 0);
    const minor = isControlled ? value : internal;

    const digits = fractionDigits ?? currencyFractionDigits(currency);

    const display = React.useMemo(
      () => formatMinor(minor, digits, locale),
      [minor, digits, locale],
    );
    const symbol = React.useMemo(
      () => currencySymbol(currency, locale),
      [currency, locale],
    );

    // A controlled input commits the caret to end-of-string on every rewrite,
    // so the position is recorded here during the change and applied after the
    // render lands. Same shape as `MaskInput`, for the same reason.
    const pendingCaretRef = React.useRef<number | null>(null);

    React.useLayoutEffect(() => {
      const pos = pendingCaretRef.current;
      if (pos == null) return;
      pendingCaretRef.current = null;
      inputRef.current?.setSelectionRange(pos, pos);
    });

    const commit = React.useCallback(
      (next: number) => {
        if (!isControlled) setInternal(next);
        onValueChange?.(next);
      },
      [isControlled, onValueChange],
    );

    const handleChange = React.useCallback(
      (event: React.ChangeEvent<HTMLInputElement>) => {
        const el = event.target;
        const typed = el.value;
        const caret = el.selectionStart ?? typed.length;

        let next = parseToMinor(typed);
        if (max !== undefined && next > max) next = max;

        // Anchor on digits to the LEFT of the caret, which regrouping cannot
        // move. Deleting a separator deletes nothing, so step past it and take
        // the digit instead — otherwise Backspace on "1,234" appears to do
        // nothing at all.
        let digitsLeft = digitsBefore(typed, caret);
        const deletedSeparator =
          typed.length < display.length && digitsLeft === digitsBefore(display, caret + 1);
        if (deletedSeparator && digitsLeft > 0) digitsLeft -= 1;

        const nextDisplay = formatMinor(next, digits, locale);
        pendingCaretRef.current = offsetAfterDigits(nextDisplay, digitsLeft);

        commit(next);
      },
      [commit, digits, display, locale, max],
    );

    return (
      <InputGroup className={groupClassName} data-disabled={disabled ? '' : undefined}>
        {showSymbol ? (
          // aria-hidden: the accessible name belongs on the field's label.
          // A screen reader announcing "dollar sign" on entry is noise; a
          // label reading "Price in US dollars" is what actually helps.
          <InputGroupAddon align="inline-start" aria-hidden="true">
            {symbol}
          </InputGroupAddon>
        ) : null}
        <InputGroupInput
          ref={inputRef}
          // `inputMode` rather than `type="number"`: a number input rejects
          // the grouped string this component displays, and its spinner is
          // meaningless for an amount. This still opens a numeric keypad.
          inputMode="decimal"
          autoComplete="off"
          value={display}
          onChange={handleChange}
          onBlur={onBlur}
          disabled={disabled}
          // Left-aligned, hugging the symbol. `text-right` looks correct in a
          // column of amounts and wrong in a single field: `flex-1` stretches
          // the control to the group's full width, so the symbol sits at one
          // edge and the number at the other with a gap between them. Right
          // alignment belongs to a table cell, which can set it via `className`.
          className={cn('tabular-nums', className)}
          {...props}
        />
      </InputGroup>
    );
  },
);
MoneyField.displayName = 'MoneyField';

export { MoneyField };
