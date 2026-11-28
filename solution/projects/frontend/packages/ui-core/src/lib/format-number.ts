/**
 * Numbers, written the way the reader's language writes them.
 *
 * Two functions, because a figure does two different jobs and they want
 * opposite things:
 *
 * - `formatNumber` — the figure IS the information. A price, a mileage, a
 *   result count the reader may quote or compare. Grouped, never rounded.
 * - `formatCompact` — the figure is a SIZE, glanced at in chrome: a badge, a
 *   tab, a nav counter. Four digits is where a number stops being read and
 *   starts being measured, and the exact value belongs on the page it leads
 *   to, not on the label pointing at it.
 *
 * WHY `Intl` AND NOT `${Math.round(n / 1000)}k`
 *
 * Measured, not assumed — `834_763` through `notation: 'compact'`:
 *
 *     en  834.8K        ru  834,8 тыс.
 *     ko  83.5만         de  834.763
 *
 * Korean groups by TEN THOUSAND, not by thousands, so a hardcoded `k` is not
 * merely untranslated there — it states the wrong magnitude. Russian wants a
 * word and a comma decimal. Hand-rolling this means hand-rolling CLDR.
 *
 * AND WHY THE CALLER STILL CANNOT ASSUME IT IS SHORT
 *
 * Note `de` in that table: Node returns the FULL number, because compact data
 * is locale-dependent and a runtime may simply not carry it. `formatCompact`
 * is a request, not a guarantee — never size a container on the assumption
 * that it returns four characters.
 */

/** Grouped by the reader's locale. `834763` → `834,763` / `834 763`. */
export function formatNumber(value: number, locale?: string): string {
  return new Intl.NumberFormat(locale).format(value);
}

/**
 * Shortened for chrome, in the reader's own notation.
 *
 * Below `threshold` the exact figure is returned grouped — a badge reading
 * `1.2K` where it could say `1,180` has traded precision for nothing.
 */
export function formatCompact(value: number, locale?: string, threshold = 10_000): string {
  if (Math.abs(value) < threshold) return formatNumber(value, locale);

  return new Intl.NumberFormat(locale, {
    notation: 'compact',
    maximumFractionDigits: 1,
  }).format(value);
}
