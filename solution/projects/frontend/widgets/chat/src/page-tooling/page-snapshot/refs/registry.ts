/**
 * Ref registry — maps CST ref ids (`@e4`) to a way of re-finding the
 * element in the live DOM.
 *
 * The registry deliberately does NOT hold `HTMLElement` references.
 * Between snapshot capture (chat-message send) and directive
 * application (the `directive` SSE event, seconds later), React
 * re-renders the page and recreates DOM nodes — any frozen node pointer
 * is detached by then and resolves to nothing. Instead each ref stores
 * a `RefLocator` and `resolve()` runs a live-DOM query at call time.
 */

import type { CSTRefId } from '../cst/types';
import { resolveLocator, type RefLocator } from './locator';

/**
 * A per-snapshot `ref → RefLocator` map. Locators are inert data, so
 * the registry stays valid across re-renders — `resolve()` re-queries
 * the current DOM every call rather than dereferencing a stale node.
 */
export class RefRegistry {
  /** Unique id of the snapshot these refs belong to. */
  readonly snapshotId: string;

  private readonly map = new Map<CSTRefId, RefLocator>();

  constructor(snapshotId: string) {
    this.snapshotId = snapshotId;
  }

  /** Register a ref → locator pair (called during the walk). */
  set(ref: CSTRefId, locator: RefLocator): void {
    this.map.set(ref, locator);
  }

  /**
   * Resolve a ref to a live element, or null if it cannot be found in
   * the current DOM (stale). Runs a fresh query every call — safe to
   * call long after capture, across any number of re-renders.
   */
  resolve(ref: CSTRefId): HTMLElement | null {
    const locator = this.map.get(ref);
    if (!locator) return null;
    return resolveLocator(locator);
  }

  /** The stored locator for a ref, if known (mainly for diagnostics). */
  getLocator(ref: CSTRefId): RefLocator | undefined {
    return this.map.get(ref);
  }

  /** Whether a ref is known to this snapshot (regardless of liveness). */
  has(ref: CSTRefId): boolean {
    return this.map.has(ref);
  }

  /** Number of registered refs. */
  get size(): number {
    return this.map.size;
  }
}
