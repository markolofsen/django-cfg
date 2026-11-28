/**
 * Value formatters shared by more than one widget.
 *
 * Nothing lands here on the strength of looking reusable — a second consumer is
 * the entry price. One place to look is the point: the same byte count must not
 * format differently across two surfaces.
 */

export interface FormatBytesOptions {
  /**
   * BCP-47 locale for digit grouping and the decimal separator. Omitted ⇒
   * deterministic `en-US`, so non-localized surfaces render identically
   * everywhere.
   */
  readonly locale?: string;
}

/**
 * THE byte formatter. Binary units (1024) up to TB.
 *
 * Digits: whole numbers at B and once the amount reaches 10; one decimal below
 * 10 (`4 KB`, `1.5 GB`, `15 KB`). Negative or NaN inputs collapse to `0 B`.
 */
export function formatBytes(n: number, options: FormatBytesOptions = {}): string {
  if (!Number.isFinite(n) || n < 0) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  let amount = n;
  let index = 0;
  while (amount >= 1024 && index < units.length - 1) {
    amount /= 1024;
    index += 1;
  }
  const digits = amount >= 10 || index === 0 ? 0 : 1;
  const formatted = new Intl.NumberFormat(options.locale ?? 'en-US', {
    maximumFractionDigits: digits,
  }).format(amount);
  return `${formatted} ${units[index]}`;
}

/**
 * THE media clock, and deliberately distinct from a duration: an uptime reads
 * as `3m 34s`, a track reads as `3:34`, and using either spelling for the other
 * looks wrong to anyone who has seen a player.
 *
 * A position of zero is a REAL reading — a track at its start — so it formats
 * as `0:00`. A caller that must distinguish "unknown" from "zero" (a card
 * stating a track's length, where zero means it could not be measured) checks
 * the value itself before calling; this cannot answer that for them without
 * making a playing track's clock vanish at 0:00.
 */
export function formatClock(seconds: number): string {
  if (!Number.isFinite(seconds) || seconds < 0) return '0:00';
  const total = Math.floor(seconds);
  const s = total % 60;
  const m = Math.floor(total / 60) % 60;
  const h = Math.floor(total / 3600);
  const ss = String(s).padStart(2, '0');
  return h > 0 ? `${h}:${String(m).padStart(2, '0')}:${ss}` : `${m}:${ss}`;
}

/**
 * A duration in milliseconds as `350ms` / `1.2s` / `5m 12s` / `2h 14m`.
 *
 * Distinct from {@link formatClock}: this reads as an ELAPSED amount, not as a
 * position on a timeline. An em dash for unusable input rather than `0ms`,
 * because "we did not measure this" and "this took no time" are different
 * claims and a reasoning step reports both.
 */
export function formatDurationMs(ms: number): string {
  if (!Number.isFinite(ms) || ms < 0) return '—';
  if (ms < 1000) return `${Math.round(ms)}ms`;
  const sec = Math.floor(ms / 1000);
  if (sec < 60) return `${(ms / 1000).toFixed(1)}s`;
  const min = Math.floor(sec / 60);
  const remSec = sec % 60;
  if (min < 60) return `${min}m ${remSec}s`;
  const hr = Math.floor(min / 60);
  return `${hr}h ${min % 60}m`;
}
