'use client';

/**
 * Bridge command registry — the named, callable capabilities the chat
 * assistant can run against the user's live page.
 *
 * The registry is the core of the bridge: directives, the dev
 * `window.__chatBridge`, and e2e tests all dispatch the same commands
 * through it, so a new capability is added without touching any caller.
 */

/** One bridge command — a named, documented, callable capability. */
export interface BridgeCommand<A extends unknown[] = unknown[], R = unknown> {
  /** Invocation name, also the `window.__chatBridge` key. */
  name: string;
  /** One-line human description — shown by `__chatBridge.help()`. */
  description: string;
  /** Whether the command mutates the user's data (vs read-only). */
  mutates: boolean;
  /** The implementation. */
  run: (...args: A) => R;
}

/** Every registered command, keyed by name. */
export const registry = new Map<string, BridgeCommand>();

/**
 * Register (or replace) a bridge command. Returns the command so it can
 * be exported directly. Replacing is allowed — handy for HMR.
 */
export function registerBridgeCommand<A extends unknown[], R>(
  cmd: BridgeCommand<A, R>,
): BridgeCommand<A, R> {
  registry.set(cmd.name, cmd as BridgeCommand);
  return cmd;
}

/** Look up a registered command by name. */
export function getBridgeCommand(name: string): BridgeCommand | undefined {
  return registry.get(name);
}
