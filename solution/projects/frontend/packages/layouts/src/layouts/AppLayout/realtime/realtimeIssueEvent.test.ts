import { describe, expect, it } from 'vitest';

import { realtimeIssueEvent } from './realtimeIssueEvent';

describe('realtimeIssueEvent', () => {
  it('maps a server fault to an error and a visitor-side close to a warning', () => {
    const fault = realtimeIssueEvent({ kind: 'closed', code: 4500, reason: 'boom', cid: 'c1' }, 'https://x/');
    expect(fault).toEqual({
      event_type: 'ERROR',
      level: 'error',
      message: 'Realtime closed 4500: boom',
      url: 'https://x/',
      extra: { source: 'realtime', kind: 'closed', cid: 'c1', code: 4500, reason: 'boom' },
    });
    expect(realtimeIssueEvent({ kind: 'closed', code: 4401, reason: '', cid: null }).level).toBe('warning');
    expect(realtimeIssueEvent({ kind: 'closed', code: 4403, reason: '', cid: null }).level).toBe('error');
  });

  it('keeps the message stable per kind and code so devtools can dedupe', () => {
    const a = realtimeIssueEvent({ kind: 'unreachable', attempts: 5, lastCode: 1006, lastReason: 'x', cid: null });
    const b = realtimeIssueEvent({ kind: 'unreachable', attempts: 5, lastCode: 1006, lastReason: 'y', cid: null });
    expect(a.message).toBe(b.message);
    expect(a.level).toBe('warning');
  });

  it('warns on forbidden, errors on an app bug, and carries the topic', () => {
    const forbidden = realtimeIssueEvent({ kind: 'refused', topic: 'orders:42', code: 'forbidden', cid: 'c1' });
    const unknown = realtimeIssueEvent({ kind: 'refused', topic: 'ordrs:42', code: 'unknown_topic', cid: 'c1' });
    expect(forbidden.level).toBe('warning');
    expect(unknown.level).toBe('error');
    expect(unknown.extra).toMatchObject({ topic: 'ordrs:42', code: 'unknown_topic', cid: 'c1' });
  });

  it('reports protocol errors and schema failures as errors', () => {
    expect(realtimeIssueEvent({ kind: 'protocol', code: 'rate', detail: null, cid: 'c1' }).level).toBe('error');
    const invalid = realtimeIssueEvent({ kind: 'invalid_event', topic: 'orders:42', message: 'bad', cid: 'c1' });
    expect(invalid.message).toBe('Realtime event on orders:42 does not match its schema');
    expect(invalid.extra).toMatchObject({ topic: 'orders:42', detail: 'bad' });
  });
});
