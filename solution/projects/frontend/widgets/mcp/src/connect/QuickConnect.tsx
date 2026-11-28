'use client';

import { ExternalLink } from 'lucide-react';

import { Button, CopyButton } from '@djangocfg/ui-core';

import { installCommand, installCommandWithKey, maskKey, skillPrompt, skillUrl } from '../install';
import { useMcpConnect } from './context';
import { SMALL_ACTION } from './parts';
import { HINT, NAME } from './styles';

import type { ReactNode } from 'react';

/** One row: title, hint, the shown value (when it is not the title), and its actions. */
function Row({ title, hint, shown, children }: { title: string; hint: string; shown?: string; children: ReactNode }) {
  return (
    <div className="flex items-center gap-3 rounded-lg border border-border bg-background px-3 py-2.5">
      <span className="flex min-w-0 flex-1 flex-col">
        <span className={NAME}>{title}</span>
        <span className={HINT}>{hint}</span>
        {shown ? (
          <span translate="no" className="truncate font-mono text-sm leading-5 text-foreground">
            {shown}
          </span>
        ) : null}
      </span>
      <span className="flex shrink-0 items-center gap-2">{children}</span>
    </div>
  );
}

/**
 * "Quick connect": the agent request and the installer command need no key, so they work in every auth state. The key row appears
 * only once the key is ready; its text is copied whole and shown masked. The View link opens SKILL.md; no key is ever in an href.
 */
export function QuickConnect() {
  const { server, labels, access } = useMcpConnect();
  const key = access.kind === 'signedIn' && access.key.kind === 'ready' ? access.key.key : null;
  const withKey = key ? installCommandWithKey(server, key) : null;
  return (
    <section className="flex flex-col gap-2">
      <span className="flex flex-col">
        <span className={NAME}>{labels.quickTitle}</span>
        <span className={HINT}>{labels.quickLede}</span>
      </span>
      <Row title={labels.quickAgentTitle} hint={labels.quickAgentHint}>
        <Button asChild size="sm" variant="ghost" className={SMALL_ACTION}>
          <a href={skillUrl(server)} target="_blank" rel="noopener noreferrer">
            <ExternalLink className="size-3.5" aria-hidden />
            {labels.view}
          </a>
        </Button>
        <CopyButton value={skillPrompt(server, labels.quickAgentPrompt)} size="sm" variant="outline" className={SMALL_ACTION} iconClassName="size-3.5">
          {labels.copy}
        </CopyButton>
      </Row>
      <Row title={labels.quickCommandTitle} hint={labels.quickCommandHint}>
        <CopyButton value={installCommand(server)} size="sm" variant="outline" className={SMALL_ACTION} iconClassName="size-3.5">
          {labels.copy}
        </CopyButton>
      </Row>
      {key && withKey ? (
        <Row title={labels.quickKeyTitle} hint={labels.quickKeyHint} shown={maskKey(key)}>
          <CopyButton value={withKey} size="sm" variant="outline" className={SMALL_ACTION} iconClassName="size-3.5">
            {labels.copy}
          </CopyButton>
        </Row>
      ) : null}
    </section>
  );
}
