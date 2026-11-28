import type { StoredThread } from '../../wire/stored';

export interface SessionGroup {
  /** Stable key: `today`, `yesterday`, or `YYYY-MM`. */
  key: string;
  /** Already in the reader's language (`Intl`, so no dictionary words are needed). */
  label: string;
  items: StoredThread[];
}

const startOfDay = (ms: number): number => {
  const d = new Date(ms);
  d.setHours(0, 0, 0, 0);
  return d.getTime();
};

const capitalize = (text: string, locale: string): string => (text === '' ? text : text.charAt(0).toLocaleUpperCase(locale) + text.slice(1));

/**
 * The list the way Messages and Notes draw it: Today, Yesterday, then one heading per month (a year too when it is not this one).
 * Order inside a group and between groups is the input's (newest activity first). Headings come from `Intl`, so a new language costs no words.
 */
export function groupSessions(items: readonly StoredThread[], locale: string, now: number = Date.now()): SessionGroup[] {
  const today = startOfDay(now);
  const day = 24 * 60 * 60 * 1000;
  const relative = new Intl.RelativeTimeFormat(locale, { numeric: 'auto' });
  const thisYear = new Date(now).getFullYear();
  const groups: SessionGroup[] = [];
  const byKey = new Map<string, SessionGroup>();
  for (const item of items) {
    const at = Date.parse(item.last_message_at);
    const date = new Date(Number.isNaN(at) ? 0 : at);
    const start = startOfDay(date.getTime());
    let key: string;
    let label: string;
    if (start >= today) {
      key = 'today';
      label = capitalize(relative.format(0, 'day'), locale);
    } else if (start >= today - day) {
      key = 'yesterday';
      label = capitalize(relative.format(-1, 'day'), locale);
    } else {
      key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
      label = capitalize(
        new Intl.DateTimeFormat(locale, date.getFullYear() === thisYear ? { month: 'long' } : { month: 'long', year: 'numeric' }).format(date),
        locale,
      );
    }
    let group = byKey.get(key);
    if (group === undefined) {
      group = { key, label, items: [] };
      byKey.set(key, group);
      groups.push(group);
    }
    group.items.push(item);
  }
  return groups;
}

/** A title containing every word of the query, case-insensitively. An empty query keeps all. */
export function filterSessions(items: readonly StoredThread[], query: string): StoredThread[] {
  const words = query.toLocaleLowerCase().split(/\s+/).filter(Boolean);
  if (words.length === 0) return [...items];
  return items.filter((item) => {
    const title = (item.title || '').toLocaleLowerCase();
    return words.every((word) => title.includes(word));
  });
}
