'use client';

/**
 * Chat commands — drive the chat conversation from the bridge.
 *
 * `sendMessage` posts a message exactly as if typed into the composer
 * (same transport, same SSE response). Useful for testing the chat —
 * incl. the page-context highlight flow — from the devtools console
 * without retyping prompts.
 */

import { log } from '../logger';
import { registerBridgeCommand } from '../registry';
import { getActiveSender } from '../set-bridge-resolver';

/**
 * sendMessage — send a chat message programmatically.
 *
 * Goes through the same `sendMessage` the composer uses, so the full
 * round-trip runs (transport, streamed reply, any directives). Resolves
 * when the send is dispatched; the reply streams asynchronously after.
 */
export const sendMessage = registerBridgeCommand({
  name: 'sendMessage',
  description: 'sendMessage(text) — send a chat message as if typed',
  mutates: true,
  run: async (text: string): Promise<{ sent: boolean }> => {
    const sender = getActiveSender();
    if (!sender) {
      log.warn('bridge.sendMessage: no chat sender registered');
      return { sent: false };
    }
    const content = String(text ?? '').trim();
    if (!content) {
      log.warn('bridge.sendMessage: empty message');
      return { sent: false };
    }
    log.info('bridge.sendMessage', { chars: content.length });
    await sender(content);
    return { sent: true };
  },
});
