'use client';

/**
 * inspect command — a read-only probe of ref freshness.
 */

import { log } from '../logger';
import { registerBridgeCommand } from '../registry';
import { getActiveResolver } from '../set-bridge-resolver';
import { resolveRefs } from '../overlay/resolve-ref';
import type { CSTRefId } from '../overlay/types';

/**
 * inspect — report which CST refs currently resolve to live elements.
 * A read-only probe: useful for the AI (or a tester) to confirm the
 * snapshot is still fresh before pointing at something.
 */
export const inspect = registerBridgeCommand({
  name: 'inspect',
  description: 'inspect(refs) — report which refs resolve to live elements',
  mutates: false,
  run: (refs: CSTRefId[]): { resolved: CSTRefId[]; missing: CSTRefId[] } => {
    const ok = new Set(resolveRefs(refs, getActiveResolver()).map((r) => r.ref));
    const result = {
      resolved: refs.filter((r) => ok.has(r)),
      missing: refs.filter((r) => !ok.has(r)),
    };
    log.info('bridge.inspect', result);
    return result;
  },
});
