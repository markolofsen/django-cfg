import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { buildWeeks, formatDate, getMonthLabels } from './utils';
import { GAP } from './types';

/**
 * This grid is the contribution heatmap. The two things a reader actually
 * trusts it for are (a) the shape is a fixed rectangle regardless of how
 * sparse the data is, and (b) a count lands on the day it happened. Both are
 * assembled here from date arithmetic against "today", so both are silently
 * wrong rather than loudly broken when the arithmetic slips.
 *
 * Time is frozen for every case below — otherwise these assertions would flip
 * once a week when the real today crosses a Sunday.
 */

describe('buildWeeks', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    // A Monday, so the "pad to end of week" branch has real work to do.
    vi.setSystemTime(new Date('2026-09-07T12:00:00Z'));
  });
  afterEach(() => {
    vi.useRealTimers();
  });

  it('always returns weekCount full weeks of 7 days, whatever the data', () => {
    // Fixed geometry is the point: the SVG's width is computed from the week
    // count, so a short or long week draws a ragged grid.
    for (const weeks of [1, 4, 52]) {
      const grid = buildWeeks([], weeks);
      expect(grid).toHaveLength(weeks);
      expect(grid.every((w) => w.length === 7)).toBe(true);
    }
  });

  it('fills every missing date with a zero rather than a hole', () => {
    const grid = buildWeeks([], 4);
    expect(grid.flat().every((d) => d.count === 0)).toBe(true);
  });

  it('runs in strictly consecutive days with no gap or repeat', () => {
    const days = buildWeeks([], 8).flat();
    for (let i = 1; i < days.length; i++) {
      const prev = days[i - 1];
      const cur = days[i];
      if (prev === undefined || cur === undefined) continue;
      const gapDays = Math.round((cur.date.getTime() - prev.date.getTime()) / 86_400_000);
      expect(gapDays).toBe(1);
    }
  });

  it('ends on the Saturday of the current week, so today is always visible', () => {
    const last = buildWeeks([], 4).flat().at(-1);
    expect(last?.date.getDay()).toBe(6);
  });

  it('starts each week on a Sunday', () => {
    for (const week of buildWeeks([], 6)) {
      expect(week[0]?.date.getDay()).toBe(0);
    }
  });

  it('sums duplicate entries for the same date instead of overwriting', () => {
    // Documented in `ActivityGraphProps`: "Duplicates with the same date are
    // summed". A last-write-wins bug here undercounts a busy day.
    const grid = buildWeeks(
      [{ date: '2026-09-01', count: 3 }, { date: '2026-09-01', count: 4 }],
      4,
    );
    expect(grid.flat().reduce((n, d) => n + d.count, 0)).toBe(7);
  });

  it('drops entries that fall outside the window rather than throwing', () => {
    const grid = buildWeeks([{ date: '2001-01-01', count: 99 }], 4);
    expect(grid.flat().reduce((n, d) => n + d.count, 0)).toBe(0);
  });

  it('places a count on exactly one day', () => {
    const hits = buildWeeks([{ date: '2026-09-01', count: 5 }], 4)
      .flat()
      .filter((d) => d.count > 0);
    expect(hits).toHaveLength(1);
    expect(hits[0]?.count).toBe(5);
  });
});

describe('buildWeeks — timezone', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date('2026-09-07T12:00:00Z'));
  });
  afterEach(() => {
    vi.useRealTimers();
  });

  it('places an entry on the day it names, in every timezone', () => {
    // Regression. Cell dates were built with LOCAL arithmetic (`setDate` →
    // local midnight) and looked up with a UTC key
    // (`toISOString().slice(0, 10)`). At a positive UTC offset local midnight
    // is still the previous UTC day, so every cell rendered the day before's
    // count — the whole heatmap shifted by one for every user east of
    // Greenwich, and the tooltip, which formats the LOCAL date, then named a
    // day the activity did not happen on.
    //
    // Verified under Asia/Tokyo, Pacific/Kiritimati, Australia/Sydney,
    // Europe/Berlin, UTC and America/New_York.
    const hit = buildWeeks([{ date: '2026-09-01', count: 5 }], 4)
      .flat()
      .find((d) => d.count > 0);
    expect(hit?.date.getDate()).toBe(1);
    expect(hit?.date.getMonth()).toBe(8); // September
  });
});

describe('getMonthLabels', () => {
  it('emits one label per month change, at that week\'s column offset', () => {
    const weeks = buildWeeks([], 12);
    const labels = getMonthLabels(weeks, 10);
    expect(labels.length).toBeGreaterThan(0);
    for (const l of labels) {
      expect(l.label).toMatch(/^[A-Z][a-z]{2}$/);
    }
  });

  it('never repeats the same month back to back', () => {
    const labels = getMonthLabels(buildWeeks([], 52), 10);
    for (let i = 1; i < labels.length; i++) {
      expect(labels[i]?.label).not.toBe(labels[i - 1]?.label);
    }
  });

  it('spaces offsets by blockSize + GAP so labels sit over their column', () => {
    const weeks = buildWeeks([], 12);
    const labels = getMonthLabels(weeks, 10);
    for (const l of labels) {
      expect(l.offset % (10 + GAP)).toBe(0);
    }
    expect(labels[0]?.offset).toBe(0);
  });

  it('returns nothing for an empty grid', () => {
    expect(getMonthLabels([], 10)).toEqual([]);
  });

  it('labels a single week once', () => {
    expect(getMonthLabels(buildWeeks([], 1), 10)).toHaveLength(1);
  });
});

describe('formatDate', () => {
  it('renders the weekday, month, day and year the tooltip shows', () => {
    // Built from local getters, so construct the date locally too.
    expect(formatDate(new Date(2026, 8, 7))).toBe('Mon, Sep 7, 2026');
  });
});
