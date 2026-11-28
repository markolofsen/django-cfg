/**
 * PageSnapshotEngine — the capture orchestrator.
 *
 * Client-side only. Walks the live DOM into a CST snapshot, folds
 * repetitive structure, enforces the token budget, and emits a
 * PageContextPayload plus a ref registry for `point` directives.
 *
 * Pipeline: scope → walk → fold → budget → serialize → metadata.
 */

import { enforceBudget, type DegradationLevel } from './capture/budget';
import { foldSiblings } from './capture/fold';
import { resolveScope, type ScopeStrategy, type ScopeTier } from './capture/scope';
import { noopRedact, walkDOM } from './capture/walk';
import type { RedactValue } from './capture/walk';
import type { CSTNode, CSTRefId, CSTRootNode } from './cst/types';
import type { PageContextPayload, SnapshotMetadata } from './cst/payload';
import { CST_SCHEMA_VERSION } from './cst/payload';
import { serializeCST } from './cst/serialize';
import { RedactionAuditor } from './redaction/audit';
import { createRedactor } from './redaction';
import { RefRegistry } from './refs/registry';
import { hashSnapshot } from './hash';
import { estimateTokens } from './tokens';

/** Default token budget — sized for real data tables. */
export const DEFAULT_TOKEN_BUDGET = 8_000;

/** Options for constructing the engine. */
export interface CaptureEngineOptions {
  /** Scope strategy (default: 'container' — auto-detect content). */
  scope?: ScopeStrategy;
  /** Token budget for the snapshot (default: DEFAULT_TOKEN_BUDGET). */
  tokenBudget?: number;
  /** Explicit target selector; overrides auto-detection. */
  targetSelector?: string;
}

/** Telemetry from one capture run. */
export interface CaptureTelemetry {
  /** Wall-clock duration of the capture, ms. */
  executionTimeMs: number;
  /** DOM elements visited. */
  nodesVisited: number;
  /** Estimated tokens of the serialized snapshot. */
  tokenEstimate: number;
  /** Redactions performed. */
  redactedCount: number;
  /** Sibling chains folded. */
  foldedCount: number;
  /** Which scope tier produced the capture root. */
  scopeTier: ScopeTier;
  /** What budget degradation, if any, was applied. */
  degradation: DegradationLevel;
}

/** Result of a capture. */
export interface CaptureResult {
  payload: PageContextPayload;
  telemetry: CaptureTelemetry;
  /**
   * Per-snapshot ref registry, for resolving `point` directives. Holds
   * re-locatable descriptors (not node pointers) so a ref still
   * resolves after React re-renders the page between capture and
   * directive application.
   */
  refs: RefRegistry;
}

/** Resolve options with defaults applied. */
function resolveOptions(
  options: CaptureEngineOptions,
): Required<Omit<CaptureEngineOptions, 'targetSelector'>> &
  Pick<CaptureEngineOptions, 'targetSelector'> {
  return {
    scope: options.scope ?? 'container',
    tokenBudget: options.tokenBudget ?? DEFAULT_TOKEN_BUDGET,
    targetSelector: options.targetSelector,
  };
}

/** Monotonic id source for snapshots within a session. */
let snapshotSeq = 0;

/**
 * The capture engine. One instance per consumer (e.g. the chat).
 */
export class PageSnapshotEngine {
  private readonly options: ReturnType<typeof resolveOptions>;

  constructor(options: CaptureEngineOptions = {}) {
    this.options = resolveOptions(options);
  }

  /**
   * Capture a snapshot of the current page.
   */
  capture(): CaptureResult {
    if (typeof window === 'undefined' || typeof document === 'undefined') {
      throw new Error(
        'PageSnapshotEngine.capture: cannot run outside a browser.',
      );
    }

    const startTime = performance.now();
    const auditor = new RedactionAuditor();
    const redactValue: RedactValue = this.buildRedactor(auditor);
    const refs = new RefRegistry(`snap-${++snapshotSeq}`);

    // Scope → walk (each root) → merge.
    const scope = resolveScope({
      strategy: this.options.scope,
      targetSelector: this.options.targetSelector,
    });

    let walked: CSTNode[] = [];
    let nodesVisited = 0;
    // Threaded across roots: the maps below merge into ONE registry, so a
    // counter restarting per root would have the second root's `@e1` overwrite
    // the first's — a ref that resolves to the wrong element.
    let startRef = 1;
    for (const root of scope.roots) {
      const result = walkDOM(root, { redactValue, startRef });
      walked = walked.concat(result.children);
      nodesVisited += result.nodesVisited;
      startRef = result.nextRef;
      // Carry the walk's ref locators into the snapshot registry.
      for (const [ref, locator] of result.refMap) {
        refs.set(ref as CSTRefId, locator);
      }
    }

    // Fold repetitive structure, then enforce the token budget.
    const folded = foldSiblings(walked);
    const budgeted = enforceBudget(folded.children, this.options.tokenBudget);

    const root: CSTRootNode = {
      type: 'root',
      title: document.title,
      url: window.location.href,
      children: budgeted.children,
    };

    const serialized = serializeCST(root);
    const tokenEstimate = estimateTokens(serialized);
    const executionTimeMs = performance.now() - startTime;

    const metadata: SnapshotMetadata = {
      representation: 'CST',
      tokenEstimate,
      captureTimestamp: Date.now(),
      schemaVersion: CST_SCHEMA_VERSION,
      contentHash: hashSnapshot(serialized),
      redactedCount: auditor.redactedCount,
      foldedCount: folded.foldedCount,
    };

    const payload: PageContextPayload = {
      url: window.location.href,
      route: window.location.pathname,
      params: {},
      title: document.title,
      snapshot: root,
      metadata,
    };

    return {
      payload,
      refs,
      telemetry: {
        executionTimeMs,
        nodesVisited,
        tokenEstimate,
        redactedCount: auditor.redactedCount,
        foldedCount: folded.foldedCount,
        scopeTier: scope.tier,
        degradation: budgeted.degradation,
      },
    };
  }

  /** Build the redaction function bound to this run's auditor. */
  private buildRedactor(auditor: RedactionAuditor): RedactValue {
    return createRedactor(auditor) ?? noopRedact;
  }
}
