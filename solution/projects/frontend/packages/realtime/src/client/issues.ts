import type { SubErrorCode } from '../protocol';

/**
 * A realtime problem worth a report: something a person has to fix or at least
 * know about. Normal weather (1006/1011/1012/1013 drops, a 4419 refresh, a
 * `sub_err timeout`) is never an issue. An issue never carries a token.
 */
export type RealtimeIssue =
  /** 4401, 4403 or 4500, or a stop the client decided itself (no WebSocket, bad URL, protocol version). */
  | { kind: 'closed'; code: number; reason: string }
  /** This many connection attempts in a row ended without `hello`; reported once per streak. */
  | { kind: 'unreachable'; attempts: number; lastCode: number; lastReason: string }
  /** `sub_err` forbidden, invalid or unknown_topic. */
  | { kind: 'refused'; topic: string; code: SubErrorCode }
  /** A protocol `error` frame, or a frame the client could not parse. */
  | { kind: 'protocol'; code: string; detail: string | null }
  /** An event failed its typed topic's schema (development only). */
  | { kind: 'invalid_event'; topic: string; message: string };

/** The issue plus the live connection's id when there was one. */
export type ReportedIssue = RealtimeIssue & { cid: string | null };

export type IssueSink = (issue: RealtimeIssue) => void;

export const UNREACHABLE_AFTER_ATTEMPTS = 5;

const REPORTED_REFUSALS: ReadonlySet<SubErrorCode> = new Set<SubErrorCode>(['forbidden', 'invalid', 'unknown_topic']);

export function isReportedRefusal(code: SubErrorCode): boolean {
  return REPORTED_REFUSALS.has(code);
}

/** 4500 is the server failing; 4401/4403 are terminal. Everything else is weather. */
export function isReportedClose(code: number): boolean {
  return code === 4401 || code === 4403 || code === 4500;
}
