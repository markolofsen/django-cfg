import { describe, expect, it } from 'vitest';

import type { StoredThread } from '../../wire/stored';
import { filterSessions, groupSessions } from './group-sessions';

const NOW = new Date(2026, 10, 9, 15, 0).getTime();
const at = (y: number, m: number, d: number, h = 12) => new Date(y, m - 1, d, h).toISOString();
const thread = (id: string, title: string, last: string): StoredThread => ({ id, title, last_message_at: last, message_count: 1 });

describe('groupSessions', () => {
  const items = [
    thread('a', 'Hello', at(2026, 11, 9, 9)),
    thread('b', 'Yesterday talk', at(2026, 11, 8, 20)),
    thread('c', 'Earlier this month', at(2026, 11, 2)),
    thread('d', 'October', at(2026, 10, 20)),
    thread('e', 'Old', at(2025, 3, 5)),
  ];

  it('opens with Today and Yesterday, then months, newest first', () => {
    const groups = groupSessions(items, 'en', NOW);
    expect(groups.map((g) => g.key)).toEqual(['today', 'yesterday', '2026-11', '2026-10', '2025-03']);
    expect(groups[0]!.label).toBe('Today');
    expect(groups[1]!.label).toBe('Yesterday');
  });

  it('names the year only when it is not this one', () => {
    const groups = groupSessions(items, 'en', NOW);
    expect(groups[3]!.label).toBe('October');
    expect(groups[4]!.label).toBe('March 2025');
  });

  it('is written in the reader\'s language', () => {
    expect(groupSessions(items, 'ru', NOW)[0]!.label).toBe('Сегодня');
  });

  it('puts an unparseable date last in the earliest bucket instead of throwing', () => {
    expect(() => groupSessions([thread('x', 't', 'nope')], 'en', NOW)).not.toThrow();
  });
});

describe('filterSessions', () => {
  const items = [thread('a', 'Refund policy', at(2026, 11, 9)), thread('b', 'Hello', at(2026, 11, 9)), thread('c', '', at(2026, 11, 9))];
  it('keeps all for an empty query', () => expect(filterSessions(items, '  ')).toHaveLength(3));
  it('matches every word, any case', () => expect(filterSessions(items, 'POLICY refund').map((i) => i.id)).toEqual(['a']));
});
