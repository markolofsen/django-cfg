import { EventLevel, EventType } from '@djangocfg/devtools';

import type { DevtoolsEvent } from '@djangocfg/devtools';
import type { ReportedIssue } from '@djangocfg/realtime';

/** Close codes that mean the deployment or the server is wrong, not the visitor. */
const SERVER_FAULT_CODES: ReadonlySet<number> = new Set([4403, 4500, 0]);

function describe(issue: ReportedIssue): { message: string; level: DevtoolsEvent['level']; fields: Record<string, unknown> } {
  switch (issue.kind) {
    case 'closed':
      return {
        message: `Realtime closed ${issue.code}${issue.reason ? `: ${issue.reason}` : ''}`,
        level: SERVER_FAULT_CODES.has(issue.code) ? EventLevel.ERROR : EventLevel.WARNING,
        fields: { code: issue.code, reason: issue.reason },
      };
    case 'unreachable':
      return {
        message: `Realtime unreachable: ${issue.attempts} attempts without hello`,
        level: EventLevel.WARNING,
        fields: { attempts: issue.attempts, code: issue.lastCode, reason: issue.lastReason },
      };
    case 'refused':
      return {
        message: `Realtime refused ${issue.topic}: ${issue.code}`,
        // `forbidden` can be a visitor's own rights; an unknown or invalid name is a bug in the app.
        level: issue.code === 'forbidden' ? EventLevel.WARNING : EventLevel.ERROR,
        fields: { topic: issue.topic, code: issue.code },
      };
    case 'protocol':
      return {
        message: `Realtime protocol error: ${issue.code}`,
        level: EventLevel.ERROR,
        fields: { code: issue.code, detail: issue.detail },
      };
    case 'invalid_event':
      return {
        message: `Realtime event on ${issue.topic} does not match its schema`,
        level: EventLevel.ERROR,
        fields: { topic: issue.topic, detail: issue.message },
      };
  }
}

/**
 * A realtime issue as a devtools event: one stable message per kind and code
 * (devtools dedupes on it), the facts in `extra`. The issue never holds a
 * token, so nothing here can leak one.
 */
export function realtimeIssueEvent(issue: ReportedIssue, url?: string): DevtoolsEvent {
  const { message, level, fields } = describe(issue);
  return {
    event_type: EventType.ERROR,
    level,
    message,
    url,
    extra: { source: 'realtime', kind: issue.kind, cid: issue.cid, ...fields },
  };
}
