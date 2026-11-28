'use client';

import { useEffect, useMemo, useRef, type ReactNode } from 'react';

import { normalizeMcpEndpoint, type McpServer } from '../install';
import type { View } from './nav';
import { Views } from './Views';
import { McpConnectProvider, useMcpConnect } from './context';
import type { McpKeyCreator, McpKeyLoader } from './access/useMcpKey';
import { MCP_DICTIONARIES, useMcpCopy, type McpConnectCopy } from '../i18n';
import { resolveMcpServer } from '../server';

export interface McpConnectProps {
  /** The server offered. Every field defaults from the host (API host + `/cfg/mcp/`), so a django-cfg host may omit it. */
  server?: Partial<McpServer>;
  /**
   * The signed-in user's MCP key, for a host with its OWN key system; called only when someone is signed in. Omit it and the key is the
   * user's django-cfg API key (`@djangocfg/api`), with a "Renew access" control under the panel.
   */
  loadKey?: McpKeyLoader;
  /** Creates a key and returns its secret, once: for hosts that keep only a hash. Offered when `loadKey` finds none, instead of the `keysUrl` link. */
  createKey?: McpKeyCreator;
  /** Extra host content under the panel (and under the renew section). */
  footer?: ReactNode;
  /** The page where a user creates a key; shown when `loadKey` finds none. */
  keysUrl?: string;
  /** Overrides any subset of the bundled copy, e.g. the product's own lede. */
  copy?: Partial<McpConnectCopy>;
  /** Hide the built-in title, for a host that already shows one (a settings page). The lede stays. */
  bare?: boolean;
  /** The language, when the host does not provide one through `@djangocfg/i18n`; any unbundled language falls back to English. */
  locale?: string;
  /** The screen to open on (home by default): for a deep link from the host, and for stories. */
  initialView?: View;
  className?: string;
}

/**
 * "Connect your AI assistant": the user's key on top, then one list of
 * every way to connect. Only a signed-in user can connect (the host shows it to no one else), and local
 * clients get that user's API key filled in.
 *
 * Needs a host with `@djangocfg/api` auth (`BaseApp` with auth enabled). The copy follows the `@djangocfg/i18n` locale.
 * Copy feedback is `CopyButton`'s own, no toasts.
 */
export function McpConnect({ server, loadKey, createKey, footer, keysUrl, copy, bare, locale, initialView, className }: McpConnectProps) {
  const bundled = useMcpCopy(locale).connect;
  /* English underneath: a key a dictionary lacks (a host's older dictionary) shows English, never blank. */
  const merged = useMemo(() => ({ ...MCP_DICTIONARIES.en.connect, ...bundled, ...copy }), [bundled, copy]);
  /* By value: a host passing an inline object must not reload the key. */
  const { url, alias, name } = resolveMcpServer(server);
  const normalized = useMemo(() => ({ url: normalizeMcpEndpoint(url), alias, name }), [url, alias, name]);
  return (
    <McpConnectProvider server={normalized} loadKey={loadKey} createKey={createKey} labels={merged} keysUrl={keysUrl} initialView={initialView}>
      <Panel className={className} footer={footer} bare={bare} />
    </McpConnectProvider>
  );
}

function Panel({ className, footer, bare }: { className?: string; footer?: ReactNode; bare?: boolean }) {
  const { labels, view } = useMcpConnect();
  const ref = useRef<HTMLDivElement>(null);
  const first = useRef(true);

  /* A screen change moves focus to the panel, so a keyboard or screen-reader user lands at the top of the new screen. */
  useEffect(() => {
    if (first.current) {
      first.current = false;
      return;
    }
    ref.current?.focus({ preventScroll: true });
  }, [view]);

  return (
    <div ref={ref} tabIndex={-1} className={['mcp-connect flex flex-col gap-4 outline-none', className].filter(Boolean).join(' ')}>
      {view.kind === 'home' ? (
        <div className="flex flex-col gap-1">
          {bare ? null : <span className="text-base font-semibold leading-6 text-foreground">{labels.title}</span>}
          <span className="text-sm leading-5 text-muted-foreground">{labels.lede}</span>
        </div>
      ) : null}
      <Views />
      {view.kind === 'home' ? footer : null}
    </div>
  );
}
