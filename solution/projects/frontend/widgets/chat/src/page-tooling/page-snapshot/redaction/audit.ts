/**
 * Redaction audit — a record of what was scrubbed and why.
 *
 * Records only that a redaction happened — never the redacted value
 * itself, so the audit trail is safe to log.
 */

/** Why a value was redacted. */
export type RedactionReason = 'heuristic' | 'regex' | 'attribute';

/** One redaction event. */
export interface RedactionEntry {
  /** Role/tag of the element involved. */
  elementRole: string;
  /** What triggered the redaction. */
  triggerReason: RedactionReason;
  /** Ref id, if the element had one. */
  assignedRef?: string;
}

/** A full audit report for one capture. */
export interface RedactionAuditReport {
  timestamp: number;
  totalElementsScanned: number;
  totalRedactedCount: number;
  entries: RedactionEntry[];
}

/** Collects redaction events during a capture. */
export class RedactionAuditor {
  private readonly entries: RedactionEntry[] = [];
  private scanned = 0;

  /** Record one scanned element. */
  markScanned(): void {
    this.scanned++;
  }

  /** Record one redaction. */
  log(entry: RedactionEntry): void {
    this.entries.push(entry);
  }

  /** How many redactions so far. */
  get redactedCount(): number {
    return this.entries.length;
  }

  /** Produce the final report. */
  report(): RedactionAuditReport {
    return {
      timestamp: Date.now(),
      totalElementsScanned: this.scanned,
      totalRedactedCount: this.entries.length,
      entries: [...this.entries],
    };
  }
}
