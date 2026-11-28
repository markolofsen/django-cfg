// ============================================================================
// @djangocfg/payments — money helpers (framework-free)
// ============================================================================
// Amounts cross the package boundary as MinorUnits (integer cents) to avoid
// float drift. These helpers convert at the display boundary only.

import type { Currency, MinorUnits } from './types';

/** Currencies with no minor unit (amount == major unit). Extend as needed. */
const ZERO_DECIMAL_CURRENCIES = new Set([
  'bif', 'clp', 'djf', 'gnf', 'jpy', 'kmf', 'krw', 'mga',
  'pyg', 'rwf', 'ugx', 'vnd', 'vuv', 'xaf', 'xof', 'xpf',
]);

function fractionDigits(currency: Currency): number {
  return ZERO_DECIMAL_CURRENCIES.has(currency.toLowerCase()) ? 0 : 2;
}

/** Convert a decimal major-unit amount (e.g. 49.0 or "49.00") to minor units. */
export function toMinorUnits(amount: number | string, currency: Currency): MinorUnits {
  const value = typeof amount === 'string' ? Number.parseFloat(amount) : amount;
  if (!Number.isFinite(value)) return 0;
  const factor = 10 ** fractionDigits(currency);
  return Math.round(value * factor);
}

/** Convert minor units back to a major-unit number. */
export function toMajorUnits(minor: MinorUnits, currency: Currency): number {
  const factor = 10 ** fractionDigits(currency);
  return minor / factor;
}

/** Format minor units as a localized currency string (e.g. "$49.00"). */
export function formatAmount(
  minor: MinorUnits,
  currency: Currency,
  locale?: string,
): string {
  try {
    return new Intl.NumberFormat(locale, {
      style: 'currency',
      currency: currency.toUpperCase(),
    }).format(toMajorUnits(minor, currency));
  } catch {
    // Unknown currency code → fall back to a plain number + code.
    return `${toMajorUnits(minor, currency).toFixed(fractionDigits(currency))} ${currency.toUpperCase()}`;
  }
}
