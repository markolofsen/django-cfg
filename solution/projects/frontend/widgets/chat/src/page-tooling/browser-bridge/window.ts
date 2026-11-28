'use client';

/**
 * `window.__chatBridge` — exposes the bridge registry in development so
 * the commands can be driven manually without an AI / SSE round-trip.
 *
 * Run `__chatBridge.highlight(['@e4'])` in the console to see the
 * spotlight directly. A dev affordance, not a public API surface — it
 * is gated on `isDev` and is a no-op on the server and in production.
 */

import { isDev } from '@djangocfg/ui-core/lib';

import { log } from './logger';
import { registry } from './registry';
import {
  highlight,
  focus,
  clear,
  inspect,
  scrollTo,
  fill,
  click,
  sendMessage,
} from './commands';

/** Shape exposed on `window.__chatBridge`. */
export interface ChatBridge {
  highlight: typeof highlight.run;
  focus: typeof focus.run;
  scrollTo: typeof scrollTo.run;
  clear: typeof clear.run;
  inspect: typeof inspect.run;
  fill: typeof fill.run;
  click: typeof click.run;
  sendMessage: typeof sendMessage.run;
  /** List every registered command with its description. */
  help: () => void;
}

declare global {
  interface Window {
    __chatBridge?: ChatBridge;
  }
}

/**
 * Install `window.__chatBridge` for manual testing. No-op on the server
 * and in production (gated on `isDev`) — the bridge is a dev affordance,
 * not a public API surface.
 */
export function installChatBridge(): void {
  if (typeof window === 'undefined' || !isDev) return;

  window.__chatBridge = {
    highlight: highlight.run,
    focus: focus.run,
    scrollTo: scrollTo.run,
    clear: clear.run,
    inspect: inspect.run,
    fill: fill.run,
    click: click.run,
    sendMessage: sendMessage.run,
    help: () => {
      console.table(
        [...registry.values()].map((c) => ({
          command: c.name,
          mutates: c.mutates,
          description: c.description,
        })),
      );
    },
  };
  log.info('window.__chatBridge installed — run __chatBridge.help()');
}
