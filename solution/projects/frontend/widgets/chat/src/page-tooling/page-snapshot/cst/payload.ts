/**
 * The request-side payload: a snapshot plus its route context and
 * metadata, sent to the backend as a separate field of the chat request.
 *
 */

import type { CSTRootNode } from './types';

/** Current CST schema version. Client and server check this. */
export const CST_SCHEMA_VERSION = '1.0.0';

/** Snapshot representation tag. Only CST for now. */
export type SnapshotRepresentation = 'CST';

/** Metadata describing how a snapshot was produced. */
export interface SnapshotMetadata {
  /** Representation format. */
  representation: SnapshotRepresentation;
  /** Approximate token count of the serialized snapshot. */
  tokenEstimate: number;
  /** Epoch ms when the snapshot was captured. */
  captureTimestamp: number;
  /** CST schema version. */
  schemaVersion: string;
  /** Stable content hash — used for staleness detection. */
  contentHash: string;
  /** How many nodes/values were redacted during capture. */
  redactedCount: number;
  /** How many repetitive sibling chains were folded. */
  foldedCount: number;
}

/**
 * The full page-context payload. Travels as its own request field —
 * never concatenated into the user's message.
 */
export interface PageContextPayload {
  /** Full URL at capture time. */
  url: string;
  /** Route pathname. */
  route: string;
  /** Route params, if resolvable. */
  params: Record<string, string>;
  /** document.title. */
  title: string;
  /** The captured tree. */
  snapshot: CSTRootNode;
  /** Capture metadata. */
  metadata: SnapshotMetadata;
}
