'use client';

import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from 'react';

import { useAuth } from '@djangocfg/api/auth';

import { useCfgKey } from './access/useCfgKey';
import { useMcpKey, type KeyState, type McpKeyCreator, type McpKeyLoader } from './access/useMcpKey';
import { HOME, backOf, type View } from './nav';
import type { Renewal } from '../renew/McpRenew';
import { useServerInfo } from '../info/useServerInfo';

import type { McpServer } from '../install';

import type { McpConnectCopy } from '../i18n';

export type Access =
  | { kind: 'checking' }
  | { kind: 'signedOut' }
  /**
   * `create`: present when the host can mint a key (see `McpKeyCreator`); on success the key is ready for this session.
   * `renewal`: present only when the key is the user's django-cfg API key (no host `loadKey`).
   */
  | { kind: 'signedIn'; key: KeyState; retry: () => void; create?: () => Promise<void>; renewal?: Renewal };

interface McpConnectValue {
  server: McpServer;
  labels: McpConnectCopy;
  /** The cabinet page where a user creates a key; unset hides the link. */
  keysUrl?: string;
  access: Access;
  /** Which screen the visitor is on, and the moves between screens (a state machine, no router). */
  view: View;
  go: (view: View) => void;
  goBack: () => void;
}

const CHECKING: Access = { kind: 'checking' };
const SIGNED_OUT: Access = { kind: 'signedOut' };

const McpConnectContext = createContext<McpConnectValue | null>(null);

export function useMcpConnect(): McpConnectValue {
  const value = useContext(McpConnectContext);
  if (!value) throw new Error('useMcpConnect must be used inside McpConnectProvider');
  return value;
}

interface ProviderProps {
  server: McpServer;
  /** The host's own key system; absent: the user's django-cfg API key. */
  loadKey?: McpKeyLoader;
  createKey?: McpKeyCreator;
  labels: McpConnectCopy;
  keysUrl?: string;
  /** The screen to open on; home when omitted. */
  initialView?: View;
  children: ReactNode;
}

/**
 * Who is asking, and with which key. The session is `useAuth`'s; the widget
 * never asks anyone to sign in, the host decides who sees it.
 */
export function McpConnectProvider({ loadKey, createKey, ...props }: ProviderProps) {
  const { isAuthenticated, isLoading, user, getToken } = useAuth();

  if (isLoading) return <Provide {...props} access={CHECKING} />;
  if (!isAuthenticated) return <Provide {...props} access={SIGNED_OUT} />;
  return <SignedIn {...props} loadKey={loadKey} createKey={createKey} userId={String(user?.id ?? user?.email ?? '')} getToken={getToken} />;
}

/** Mounted only for a signed-in user, so the key is never requested anonymously. */
function SignedIn({ loadKey, createKey, userId, getToken, ...props }: Omit<ProviderProps, 'children'> & { children: ReactNode; userId: string; getToken: () => string | null }) {
  return loadKey ? (
    <OwnKey {...props} loadKey={loadKey} createKey={createKey} userId={userId} getToken={getToken} />
  ) : (
    <CfgKey {...props} key={userId} createKey={createKey} />
  );
}

/** The host owns the keys: its `loadKey`, optionally its `createKey`. */
function OwnKey({
  loadKey,
  createKey,
  userId,
  getToken,
  ...props
}: Omit<ProviderProps, 'children' | 'loadKey'> & { loadKey: McpKeyLoader; children: ReactNode; userId: string; getToken: () => string | null }) {
  const { state, retry, setKey } = useMcpKey({ loadKey, userId, getToken });
  const create = useMemo(
    () => (createKey ? async () => setKey(await createKey({ token: getToken(), signal: new AbortController().signal })) : undefined),
    [createKey, getToken, setKey],
  );
  const access = useMemo<Access>(() => ({ kind: 'signedIn', key: state, retry, create }), [state, retry, create]);
  return <Provide {...props} access={access} />;
}

/** django-cfg's own key; renewable unless the host also passes `createKey` (then it owns the keys after all). */
function CfgKey({ createKey, ...props }: Omit<ProviderProps, 'children' | 'loadKey'> & { children: ReactNode }) {
  const { state, retry, renewal } = useCfgKey();
  const access: Access = { kind: 'signedIn', key: state, retry, renewal: createKey ? undefined : renewal };
  return <Provide {...props} access={access} />;
}

function Provide({
  server: baseServer,
  labels,
  keysUrl,
  access,
  initialView,
  children,
}: Omit<ProviderProps, 'loadKey' | 'createKey'> & { access: Access }) {
  const [view, setView] = useState<View>(initialView ?? HOME);
  const info = useServerInfo(baseServer, access.kind === 'signedIn' && access.key.kind === 'ready' ? access.key.key : null);
  const server = useMemo(() => (info ? { ...baseServer, info } : baseServer), [baseServer, info]);
  const goBack = useCallback(() => setView((current) => backOf(current)), []);
  const value = useMemo(() => ({ server, labels, keysUrl, access, view, go: setView, goBack }), [server, labels, keysUrl, access, view, goBack]);
  return <McpConnectContext.Provider value={value}>{children}</McpConnectContext.Provider>;
}
