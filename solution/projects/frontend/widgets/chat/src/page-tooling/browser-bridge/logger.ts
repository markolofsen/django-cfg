/**
 * Browser-bridge dev logger.
 *
 * A self-contained namespaced `consola` logger for the bridge subsystem
 * (page-context `point` directives: SSE event → bus → overlay). It is a
 * sibling of `lib/page-snapshot/`, so it must NOT reach up into `tools/` —
 * the bridge is infrastructure, Chat is merely a consumer.
 *
 * Mirrors the gating of the chat logger (`tools/chat/core/logger.ts`): the
 * `chat:directives` sub-logger is silenced unless `isDev`, so noisy bridge
 * events never leak into production builds. Kept local and minimal — only
 * the `directives` scope is needed here.
 */
import { consola } from 'consola';

import { isDev } from '@djangocfg/ui-core/lib';

/**
 * Namespaced logger for bridge directives. Tagged `chat:directives` to stay
 * consistent with the chat logger's scope naming. No-ops in production.
 */
export const log = consola.withTag('chat').withTag('directives');

// Silence in production — bridge directive logs are dev-only diagnostics.
if (!isDev) {
  log.level = -999;
}
