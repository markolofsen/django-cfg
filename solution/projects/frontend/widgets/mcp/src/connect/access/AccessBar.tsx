'use client';

import { useState, type ReactNode } from 'react';

import { Button, CopyButton } from '@djangocfg/ui-core';

import { maskKey } from '../../install';
import { useMcpConnect } from '../context';

/** Why the actions are off and the control that turns them on; once ready, the user's key at hand. */
export function AccessBar() {
  const { labels, access, keysUrl } = useMcpConnect();

  /* Signed out: nothing here. The dialog opens only for a signed-in user; anywhere else the rows stay disabled. */
  if (access.kind !== 'signedIn') return null;

  const { key, retry, create } = access;
  /* Loading is silent: the actions are disabled for a moment, and a bar that
     flashes in and out would shift the panel. */
  if (key.kind === 'loading') return null;
  if (key.kind === 'error') {
    return (
      <Bar text={labels.keyError}>
        <Button size="sm" variant="outline" onClick={retry}>
          {labels.retry}
        </Button>
      </Bar>
    );
  }
  if (key.kind === 'missing' && create) {
    return <CreateBar create={create} />;
  }
  if (key.kind === 'missing' && keysUrl) {
    return (
      <Bar text={labels.keyMissing}>
        <Button asChild size="sm" variant="outline" className="mcp-connect__action">
          <a href={keysUrl} target="_blank" rel="noopener noreferrer">
            {labels.createKey}
          </a>
        </Button>
      </Bar>
    );
  }
  return key.kind === 'missing' ? <Bar text={labels.keyMissing} /> : <KeyLine apiKey={key.key} once={create !== undefined} />;
}

/** No key yet and the host can mint one: one button; a failure shows the error bar and the button again. */
function CreateBar({ create }: { create: () => Promise<void> }) {
  const { labels } = useMcpConnect();
  const [state, setState] = useState<'idle' | 'busy' | 'error'>('idle');
  const press = () => {
    setState('busy');
    create().catch(() => setState('error'));
  };
  return (
    <Bar text={state === 'error' ? labels.keyError : labels.keyMissing}>
      <Button size="sm" variant="outline" className="mcp-connect__action" disabled={state === 'busy'} onClick={press}>
        {labels.createKey}
      </Button>
    </Bar>
  );
}

/** The key for anything the list does not cover: masked on screen, copied whole. */
function KeyLine({ apiKey, once }: { apiKey: string; once: boolean }) {
  const { labels } = useMcpConnect();

  return (
    <div className="flex flex-col gap-1.5">
      <div className="flex items-center justify-between gap-3 rounded-lg border border-border bg-muted/40 px-3 py-2">
        <span className="flex min-w-0 flex-col">
          <span className="text-sm leading-5 text-muted-foreground">{labels.yourKey}</span>
          <span translate="no" className="truncate font-mono text-sm leading-5 text-foreground">
            {maskKey(apiKey)}
          </span>
        </span>
        <CopyButton value={apiKey} size="sm" variant="outline" className="mcp-connect__action h-8 shrink-0 gap-1.5 px-3" iconClassName="size-3.5">
          {labels.copy}
        </CopyButton>
      </div>
      {once ? <span className="px-1 text-sm leading-5 text-muted-foreground">{labels.keyOnce}</span> : null}
    </div>
  );
}

function Bar({ text, children }: { text: string; children?: ReactNode }) {
  return (
    <div role="status" className="flex items-center justify-between gap-3 rounded-lg bg-muted px-3 py-2">
      <span className="text-sm leading-5 text-foreground">{text}</span>
      {children}
    </div>
  );
}
