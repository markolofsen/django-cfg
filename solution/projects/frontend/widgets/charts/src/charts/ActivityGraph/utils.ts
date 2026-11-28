// Adapted from jalcoui (MIT) — github.com/jal-co/ui

import type { ActivityEntry } from './types';
import { GAP } from './types';

export interface WeekDay {
  date: Date;
  count: number;
}

/**
 * A `YYYY-MM-DD` key from a date's LOCAL components.
 *
 * `toISOString().slice(0, 10)` was used here and is a UTC key, while every
 * cell's `Date` is built by local arithmetic (`setDate` → local midnight). At
 * a positive UTC offset local midnight is still the previous UTC day, so every
 * cell read the day before's count: the whole heatmap shifted by one for every
 * user east of Greenwich, and the tooltip — which formats the local date —
 * then named a day the activity did not happen on.
 */
function localDateKey(d: Date): string {
  const month = `${d.getMonth() + 1}`.padStart(2, '0');
  const day = `${d.getDate()}`.padStart(2, '0');
  return `${d.getFullYear()}-${month}-${day}`;
}

/**
 * Bucket the supplied entries into a fixed-size grid that ends on the
 * current week and spans `weekCount` weeks. Missing dates fill with 0.
 *
 * Entry dates are read as LOCAL calendar days, matching how the grid is built
 * and how the tooltip displays them.
 */
export function buildWeeks(data: ActivityEntry[], weekCount: number): WeekDay[][] {
  const countMap = new Map<string, number>();
  for (const entry of data) {
    countMap.set(entry.date, (countMap.get(entry.date) ?? 0) + entry.count);
  }

  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const todayDay = today.getDay();

  const endOfWeek = new Date(today);
  endOfWeek.setDate(today.getDate() + (6 - todayDay));

  const totalDays = weekCount * 7;
  const startDate = new Date(endOfWeek);
  startDate.setDate(endOfWeek.getDate() - totalDays + 1);

  const weeks: WeekDay[][] = [];
  let currentWeek: WeekDay[] = [];

  for (let i = 0; i < totalDays; i++) {
    const d = new Date(startDate);
    d.setDate(startDate.getDate() + i);
    const key = localDateKey(d);
    currentWeek.push({ date: d, count: countMap.get(key) ?? 0 });

    if (currentWeek.length === 7) {
      weeks.push(currentWeek);
      currentWeek = [];
    }
  }

  if (currentWeek.length > 0) {
    weeks.push(currentWeek);
  }

  return weeks;
}

/**
 * Find the column offset for the first week of every new month. Used to
 * lay month labels along the top of the grid.
 */
export function getMonthLabels(
  weeks: WeekDay[][],
  blockSize: number,
): { label: string; offset: number }[] {
  const months: { label: string; offset: number }[] = [];
  let lastKey = '';

  for (let w = 0; w < weeks.length; w++) {
    // `buildWeeks` never emits an empty week; skip one defensively rather than throw.
    const firstDay = weeks[w]?.[0];
    if (firstDay === undefined) continue;
    const key = `${firstDay.date.getFullYear()}-${firstDay.date.getMonth()}`;

    if (key !== lastKey) {
      months.push({
        label: firstDay.date.toLocaleString('en-US', { month: 'short' }),
        offset: w * (blockSize + GAP),
      });
      lastKey = key;
    }
  }

  return months;
}

export function formatDate(date: Date): string {
  return date.toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}
