// @vitest-environment jsdom
import { describe, expect, it } from 'vitest';

import { PageSnapshotEngine } from './engine';
import { CST_SCHEMA_VERSION } from './cst/payload';

describe('PageSnapshotEngine (P0 skeleton)', () => {
  it('returns a schema-valid empty snapshot', () => {
    const { payload, telemetry } = new PageSnapshotEngine({
      scope: 'full',
    }).capture();

    expect(payload.snapshot.type).toBe('root');
    expect(payload.snapshot.children).toEqual([]);
    expect(payload.title).toBe(document.title);
    expect(payload.url).toBe(window.location.href);
    expect(payload.route).toBe(window.location.pathname);

    expect(payload.metadata.schemaVersion).toBe(CST_SCHEMA_VERSION);
    expect(payload.metadata.representation).toBe('CST');
    expect(payload.metadata.contentHash).toMatch(/^[0-9a-f]{8}$/);
    expect(payload.metadata.tokenEstimate).toBeGreaterThan(0);
    expect(payload.metadata.redactedCount).toBe(0);
    expect(payload.metadata.foldedCount).toBe(0);

    expect(telemetry.nodesVisited).toBe(0);
    expect(telemetry.executionTimeMs).toBeGreaterThanOrEqual(0);
  });

  it('produces a stable content hash across repeated captures', () => {
    const engine = new PageSnapshotEngine();
    const a = engine.capture().payload.metadata.contentHash;
    const b = engine.capture().payload.metadata.contentHash;
    expect(a).toBe(b);
  });

  /**
   * Tier 1 returns EVERY visible `[data-ai-context]` element, so a page
   * annotating two panels is captured from two roots. Refs must stay unique
   * across them: the tree and the registry are one snapshot, and a duplicate
   * resolves to whichever root was walked last — a wrong element, not a
   * missing one.
   */
  it('assigns unique refs across multiple capture roots', () => {
    document.body.innerHTML =
      '<section data-ai-context><button>First</button></section>' +
      '<section data-ai-context><button>Second</button></section>';

    const { payload } = new PageSnapshotEngine().capture();

    const refs: string[] = [];
    const collect = (node: unknown): void => {
      if (!node || typeof node !== 'object') return;
      const n = node as { ref?: string; children?: unknown[] };
      if (typeof n.ref === 'string') refs.push(n.ref);
      for (const child of n.children ?? []) collect(child);
    };
    collect(payload.snapshot);

    expect(refs).toHaveLength(2);
    expect(new Set(refs).size).toBe(2);
  });
});
