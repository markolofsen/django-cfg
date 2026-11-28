'use client';

/**
 * scroll command — bring an element into view without a spotlight.
 */

import { log } from '../logger';
import { registerBridgeCommand } from '../registry';
import { getActiveResolver } from '../set-bridge-resolver';
import { resolveRefs } from '../overlay/resolve-ref';
import type { CSTRefId } from '../overlay/types';

/**
 * scrollTo — bring an element into view without drawing a spotlight.
 * Resolves the ref directly (no overlay) and scrolls.
 */
export const scrollTo = registerBridgeCommand({
  name: 'scrollTo',
  description: 'scrollTo(ref) — scroll an element into view',
  mutates: false,
  run: (ref: CSTRefId): { ok: boolean } => {
    const [resolved] = resolveRefs([ref], getActiveResolver());
    if (!resolved) {
      log.warn('bridge.scrollTo: ref did not resolve', { ref });
      return { ok: false };
    }
    resolved.element.scrollIntoView({ behavior: 'smooth', block: 'center' });
    log.info('bridge.scrollTo', { ref });
    return { ok: true };
  },
});
