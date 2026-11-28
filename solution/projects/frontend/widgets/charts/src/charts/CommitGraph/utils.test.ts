import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { formatFullDate, formatRelativeDate, initials } from './utils';

/**
 * These three feed the commit row: the avatar fallback and the two timestamps.
 * `formatRelativeDate` is the one with teeth — it is a cascade of boundary
 * comparisons, and an off-by-one at any rung reads as a plausible-but-wrong
 * age ("2h ago" on a commit from yesterday), which nobody reports as a bug.
 *
 * Time is frozen so the boundaries are exact rather than approximately right.
 */

describe('initials', () => {
  it('takes the first letter of each word, uppercased', () => {
    expect(initials('ada lovelace')).toBe('AL');
  });

  it('caps at two characters', () => {
    expect(initials('Johann Sebastian Bach')).toBe('JS');
  });

  it('handles a single name', () => {
    expect(initials('Cher')).toBe('C');
  });

  it('collapses runs of whitespace rather than emitting a blank initial', () => {
    expect(initials('Ada   Lovelace')).toBe('AL');
  });

  it('returns an empty string for an empty name, so the avatar falls through', () => {
    expect(initials('')).toBe('');
  });

  it('keeps a non-latin first letter instead of dropping it', () => {
    expect(initials('Лев Толстой')).toBe('ЛТ');
  });

  it('yields empty for whitespace only', () => {
    expect(initials('   ')).toBe('');
  });
});

describe('formatRelativeDate', () => {
  const NOW = new Date('2026-09-07T12:00:00Z');

  beforeEach(() => {
    vi.useFakeTimers();
    vi.setSystemTime(NOW);
  });
  afterEach(() => {
    vi.useRealTimers();
  });

  const ago = (ms: number) => new Date(NOW.getTime() - ms);

  it('says "just now" under a minute', () => {
    expect(formatRelativeDate(ago(0))).toBe('just now');
    expect(formatRelativeDate(ago(59_000))).toBe('just now');
  });

  it('switches to minutes exactly at 60s', () => {
    expect(formatRelativeDate(ago(60_000))).toBe('1m ago');
    expect(formatRelativeDate(ago(59 * 60_000))).toBe('59m ago');
  });

  it('switches to hours exactly at 60m', () => {
    expect(formatRelativeDate(ago(60 * 60_000))).toBe('1h ago');
    expect(formatRelativeDate(ago(23 * 3_600_000))).toBe('23h ago');
  });

  it('switches to days exactly at 24h', () => {
    expect(formatRelativeDate(ago(24 * 3_600_000))).toBe('1d ago');
    expect(formatRelativeDate(ago(6 * 86_400_000))).toBe('6d ago');
  });

  it('falls back to an absolute date at exactly 7 days', () => {
    // The cascade's last rung. Off by one here and week-old commits either
    // read "7d ago" forever or jump to a date a day early.
    //
    // The expectation is derived, not written out: the function formats the
    // LOCAL calendar date, which is right — a user reads their own dates — but
    // it means a literal 'Aug 31' only holds in some zones. At UTC+14 seven
    // days before Sep 7 12:00 UTC is already Sep 1 locally, and the test
    // failed for a correct implementation.
    const sevenDaysAgo = ago(7 * 86_400_000);
    const expected = sevenDaysAgo.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    });
    expect(formatRelativeDate(sevenDaysAgo)).toBe(expected);
    expect(expected).not.toMatch(/ago|just now/);
  });

  it('omits the year for a date in the current year', () => {
    const sameYear = new Date('2026-01-15T12:00:00Z');
    expect(formatRelativeDate(sameYear)).toBe(
      sameYear.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    );
  });

  it('includes the year once the commit is from a different year', () => {
    const otherYear = new Date('2024-03-02T12:00:00Z');
    expect(formatRelativeDate(otherYear)).toBe(
      otherYear.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
      }),
    );
  });

  it('accepts an ISO string as well as a Date', () => {
    expect(formatRelativeDate('2026-09-07T11:00:00Z')).toBe('1h ago');
  });

  it('reports a future timestamp as "just now" rather than a negative age', () => {
    // Clock skew between a CI machine and the browser makes this real. It
    // must not render "-3m ago".
    expect(formatRelativeDate(ago(-3 * 60_000))).toBe('just now');
  });
});

describe('formatFullDate', () => {
  it('renders the long form the detail popover shows', () => {
    const out = formatFullDate(new Date(2026, 8, 7, 14, 5));
    expect(out).toContain('Mon');
    expect(out).toContain('Sep 7');
    expect(out).toContain('2026');
    expect(out).toContain('05');
  });

  it('accepts an ISO string', () => {
    expect(formatFullDate('2026-09-07T14:05:00Z')).toContain('2026');
  });

  it('zero-pads the minute, so 14:05 is not shown as 14:5', () => {
    expect(formatFullDate(new Date(2026, 8, 7, 14, 5))).toMatch(/:05/);
  });
});
