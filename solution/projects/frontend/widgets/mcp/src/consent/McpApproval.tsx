'use client';

import { useEffect, useRef } from 'react';
import { Check, Loader2 } from 'lucide-react';

import { useMcpCopy } from '../i18n';
import { resolveMcpServer } from '../server';
import type { McpServer } from '../install';
import { useConsent } from './useConsent';

const BAR = 'flex items-center gap-2 rounded-lg border border-border bg-muted/40 px-3 py-2 text-sm';

export interface McpApprovalProps {
  request: string;
  server?: Partial<McpServer>;
}

/**
 * An assistant's request (`#settings/mcp?request=…`) is approved the moment the signed-in user lands here: the user
 * already asked their assistant to connect, so there is nothing to answer. It renders one status line above the list and
 * sends the browser back to the assistant. Once per `request`; a failure stays as a line, the list below keeps working.
 */
export function McpApproval({ request, server }: McpApprovalProps) {
  const copy = useMcpCopy().consent;
  const { url } = resolveMcpServer(server);
  const { origin, pathname } = new URL(url);
  const { view, client, decide } = useConsent({ apiUrl: origin, mcpPath: pathname, request });
  const sent = useRef('');

  useEffect(() => {
    if (view.kind !== 'ready' || sent.current === request) return;
    sent.current = request;
    void decide(true);
  }, [view.kind, request, decide]);

  if (view.kind === 'invalid') return null;
  if (view.kind === 'rejected') {
    return (
      <span role="alert" className={`${BAR} text-destructive`}>
        {view.message}
      </span>
    );
  }
  const done = view.kind === 'approved';
  return (
    <span role="status" className={BAR}>
      {done ? <Check className="size-4 text-foreground" aria-hidden /> : <Loader2 className="size-4 animate-spin" aria-hidden />}
      {(done ? copy.connected : copy.connecting).replace('{client}', client)}
    </span>
  );
}
