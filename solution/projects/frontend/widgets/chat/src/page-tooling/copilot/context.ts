/**
 * What the agent is told about the page.
 *
 * Two shapes, and the difference is the whole point of the content hash: a page
 * that has not changed since the last turn is re-stated as a reference, not
 * re-serialised. A tree costs thousands of tokens; a hash costs one line, and
 * the agent's refs from that turn are still valid because the page still is.
 */

import type { PageContextPayload } from "../page-snapshot";

/** The page, in full — the first turn, or any turn after it changed. */
export interface PageSnapshotContext {
  readonly kind: "snapshot";
  readonly payload: PageContextPayload;
}

/**
 * The page, unchanged since `hash`.
 *
 * Carries no tree. A host forwarding this to a model that has not seen the
 * matching snapshot must send the full one instead — the hash names a turn in
 * this conversation, not a cache the model owns.
 */
export interface PageUnchangedContext {
  readonly kind: "unchanged";
  readonly hash: string;
}

export type PageContext = PageSnapshotContext | PageUnchangedContext;

/** Reads the live page. Satisfied by `usePageSnapshot()`. */
export interface PageSource {
  /** Capture for sending, pinning the result for directive resolution. */
  getChatMetadata: () => Record<string, unknown> | undefined;
  /** Whether the page moved since the assistant last saw it. */
  isStale: boolean;
}

/**
 * The page to send this turn, or undefined when the user has not opted in.
 *
 * `lastHash` is what was sent last time; pass the returned context's hash back
 * next turn. Kept as an argument rather than module state so two chats on one
 * page do not share a baseline.
 */
export function readPageContext(
  source: PageSource,
  lastHash: string | null
): PageContext | undefined {
  const metadata = source.getChatMetadata();
  if (!metadata) return undefined;

  const payload = metadata.pageContext as PageContextPayload | undefined;
  if (!payload) return undefined;

  const hash = payload.metadata.contentHash;
  // Same page as last turn ⇒ say so and send nothing. The agent keeps the refs
  // it already has, which still resolve, because nothing moved.
  if (lastHash !== null && hash === lastHash) {
    return { kind: "unchanged", hash };
  }
  return { kind: "snapshot", payload };
}

/** The hash a context carries, for the caller to remember. */
export function contextHash(context: PageContext): string {
  return context.kind === "snapshot" ? context.payload.metadata.contentHash : context.hash;
}
