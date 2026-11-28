'use client';

/**
 * Live connections handed to the bridge by the React layer.
 *
 * The bridge has no React context, so providers publish their
 * capabilities here on mount and retract them on unmount:
 *
 *  - the ref→element resolver, owned by `PageSnapshotProvider`;
 *  - the chat `sendMessage` function, owned by `ChatProvider`.
 *
 * Bridge commands read them through the getters below.
 */

import { type RefResolver } from './overlay/resolve-ref';

let activeResolver: RefResolver | null = null;

/** Called by `PageSnapshotProvider` to publish / retract its resolver. */
export function setBridgeResolver(resolver: RefResolver | null): void {
  activeResolver = resolver;
}

/** Read the resolver currently published by the provider, if any. */
export function getActiveResolver(): RefResolver | null {
  return activeResolver;
}

/** Sends a message into the chat — same path as the composer's send. */
export type BridgeSender = (content: string) => Promise<void> | void;

let activeSender: BridgeSender | null = null;

/** Called by `ChatProvider` to publish / retract its `sendMessage`. */
export function setBridgeSender(sender: BridgeSender | null): void {
  activeSender = sender;
}

/** Read the chat sender currently published by the provider, if any. */
export function getActiveSender(): BridgeSender | null {
  return activeSender;
}
