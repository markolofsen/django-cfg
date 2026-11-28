'use client';

import { useMemo, useState } from 'react';

import { useAuth } from '@djangocfg/api/auth';

import { useMcpCopy } from '../i18n';
import { readSignedRequest } from './signedRequest';

export interface UseConsentArgs {
  /** Django's origin, where `<mcpPath>oauth/approve/` lives. */
  apiUrl: string;
  mcpPath?: string;
  /** The signed request from the authorize redirect; empty when the link carried none. */
  request: string;
  /** The client's name from the query, used when the signed request has none. */
  clientHint?: string | null;
}

/** One view at a time: the card renders exactly this, never a mix. */
export type ConsentView =
  | { kind: 'invalid' }
  | { kind: 'checking' }
  | { kind: 'ready' }
  | { kind: 'sending' }
  /** The server said yes; the browser is on its way back to the assistant. */
  | { kind: 'approved' }
  /** A decision did not go through: the card stays, with the message under the buttons. */
  | { kind: 'rejected'; message: string };

/**
 * The consent flow as a state machine, shared by the page and the Settings dialog. It reads nothing from the address:
 * the surface passes the `request` in, so the same flow serves `?request=` and `#settings/mcp?request=`.
 * There is nothing to tick: the assistant already shows what it will be allowed to do.
 */
export function useConsent({ apiUrl, mcpPath = '/mcp/', request, clientHint }: UseConsentArgs) {
  const copy = useMcpCopy().consent;
  const { isAuthenticated, isLoading, user, getToken } = useAuth();
  const [decision, setDecision] = useState<{ kind: 'idle' } | { kind: 'sending' } | { kind: 'approved' } | { kind: 'rejected'; message: string }>({ kind: 'idle' });

  const approveUrl = `${apiUrl.replace(/\/$/, '')}/${mcpPath.replace(/^\/|\/$/g, '')}/oauth/approve/`;
  /* Name and destination from the signed request (display only); the query's `client` is the fallback. */
  const signed = useMemo(() => readSignedRequest(request), [request]);
  const client = (signed?.client ?? clientHint ?? copy.unknownClient).slice(0, 80);
  const host = signed?.host;

  const decide = async (allow: boolean) => {
    setDecision({ kind: 'sending' });
    try {
      const response = await fetch(approveUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${getToken() ?? ''}` },
        body: JSON.stringify({ request, allow }),
      });
      const body = (await response.json().catch(() => ({}))) as { redirect_to?: string };
      if (!response.ok || !body.redirect_to) {
        /* Only a thrown fetch is "unreachable"; any answer from the server is not a connectivity problem. */
        setDecision({ kind: 'rejected', message: response.status === 400 ? copy.expired : copy.failed });
        return;
      }
      setDecision({ kind: 'approved' });
      window.location.assign(body.redirect_to);
    } catch {
      setDecision({ kind: 'rejected', message: copy.unreachable });
    }
  };

  let view: ConsentView;
  if (!request) view = { kind: 'invalid' };
  else if (isLoading || !isAuthenticated) view = { kind: 'checking' };
  else if (decision.kind === 'sending') view = { kind: 'sending' };
  else if (decision.kind === 'approved') view = { kind: 'approved' };
  else if (decision.kind === 'rejected') view = { kind: 'rejected', message: decision.message };
  else view = { kind: 'ready' };

  return { view, client, host, email: user?.email, decide };
}
