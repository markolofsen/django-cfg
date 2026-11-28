'use client';

import { ChevronLeft, ChevronRight, ExternalLink } from 'lucide-react';

import { Button, CopyButton } from '@djangocfg/ui-core';
import { useIsMobile } from '@djangocfg/ui-core/hooks';

import { brandById, type Action, type Mark, type Variant } from './clients';
import { useMcpConnect, type Access } from './context';
import { trail, type Crumb } from './nav';
import { HINT, NAME } from './styles';

import type { McpServer } from '../install';
import type { McpConnectCopy } from '../i18n';
import type { ReactNode } from 'react';

/** The row's action, or null while it cannot run: checking, signed out, or no key yet. */
export function actionFor(variant: Variant, server: McpServer, access: Access, isMobile: boolean): Action | null {
  if (access.kind !== 'signedIn') return null;
  /* An editor deeplink cannot open on a phone; a command can still be copied and sent on. */
  if (isMobile && variant.desktopOnly && variant.actionKind === 'link') return null;
  if (variant.auth === 'oauth') return variant.action(server);
  return access.key.kind === 'ready' ? variant.action(server, access.key.key) : null;
}

export const ACTION_LABEL: Record<Action['kind'], keyof McpConnectCopy> = {
  link: 'open',
  copy: 'copy',
  copyOpen: 'copyAndOpen',
};

const SMALL = 'mcp-connect__action h-8 shrink-0 gap-1.5 px-3';
const BIG = 'mcp-connect__action h-10 w-full gap-2 px-4';

/** Back button and breadcrumb: where the visitor is, and the way up. */
export function Header() {
  const { view, goBack, labels, go } = useMcpConnect();
  const crumbs = trail(view);
  const nameFor = (crumb: Crumb): string => {
    switch (crumb.kind) {
      case 'root':
        return labels.crumbRoot;
      case 'manual':
        return labels.otherApp;
      case 'brand':
        return brandById(crumb.id)?.name ?? crumb.id;
    }
  };
  return (
    <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
      <Button type="button" size="sm" variant="ghost" className="-ms-2 h-8 gap-1 px-2" onClick={goBack} aria-label={labels.back}>
        <ChevronLeft className="size-4 rtl:rotate-180" aria-hidden />
        {labels.back}
      </Button>
      <nav aria-label={labels.breadcrumbLabel} className="min-w-0">
        <ol className="m-0 flex list-none flex-wrap items-center gap-1 p-0 text-sm leading-5 text-muted-foreground">
          {crumbs.map((crumb, i) => {
            const last = i === crumbs.length - 1;
            return (
              <li key={i} className="flex items-center gap-1">
                {i > 0 ? <ChevronRight className="size-3.5 rtl:rotate-180" aria-hidden /> : null}
                {last ? (
                  <span aria-current="page" translate={crumb.kind === 'brand' ? 'no' : undefined} className="font-medium text-foreground">
                    {nameFor(crumb)}
                  </span>
                ) : (
                  <button
                    type="button"
                    className="rounded-sm underline-offset-2 hover:text-foreground hover:underline"
                    onClick={() => go({ kind: 'home' })}
                  >
                    {nameFor(crumb)}
                  </button>
                )}
              </li>
            );
          })}
        </ol>
      </nav>
    </div>
  );
}

/** A big tile of the home grid. */
export function Tile({ Mark, name, literal, onClick, layout }: { Mark: Mark; name: string; literal: boolean; onClick: () => void; layout: 'tile' | 'row' }) {
  const base = 'mcp-connect__tile border border-border bg-background transition-colors hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring';
  return layout === 'tile' ? (
    <button type="button" onClick={onClick} className={`${base} flex min-h-[7rem] flex-col items-center justify-center gap-3 rounded-xl p-4 text-center`}>
      <Mark width={36} height={36} className="shrink-0" aria-hidden />
      <span translate={literal ? 'no' : undefined} className={NAME}>
        {name}
      </span>
    </button>
  ) : (
    <button type="button" onClick={onClick} className={`${base} flex w-full items-center gap-3 rounded-lg px-3 py-3 text-start`}>
      <Mark width={24} height={24} className="shrink-0" aria-hidden />
      <span translate={literal ? 'no' : undefined} className={`${NAME} flex-1`}>
        {name}
      </span>
      <ChevronRight className="size-4 shrink-0 text-muted-foreground rtl:rotate-180" aria-hidden />
    </button>
  );
}

/** One value with its Copy: a label, the (masked) value, a button; disabled until `value` exists. */
export function Field({ label, shown, value }: { label: string; shown: string; value: string | null }) {
  const { labels, access } = useMcpConnect();
  const live = access.kind === 'signedIn' && value !== null;
  return (
    <div className="flex items-center gap-3 rounded-lg border border-border bg-background px-3 py-2">
      <span className="flex min-w-0 flex-1 flex-col">
        <span className={HINT}>{label}</span>
        <span translate="no" className="truncate font-mono text-sm leading-5 text-foreground">
          {shown}
        </span>
      </span>
      {live ? (
        <CopyButton value={value} size="sm" variant="outline" className={SMALL} iconClassName="size-3.5">
          {labels.copy}
        </CopyButton>
      ) : (
        <Button size="sm" variant="outline" className={SMALL} disabled>
          {labels.copy}
        </Button>
      )}
    </div>
  );
}

/** Numbered steps with a thin line between the badges; each step may carry its own content (a field). */
export function Steps({ items }: { items: { text: string; extra?: ReactNode }[] }) {
  return (
    <ol className="m-0 flex list-none flex-col p-0">
      {items.map((item, i) => (
        <li key={i} className="flex gap-3">
          <span className="flex flex-col items-center">
            <span aria-hidden className="flex size-6 shrink-0 items-center justify-center rounded-full border border-border bg-muted text-sm font-medium leading-none text-foreground">
              {i + 1}
            </span>
            {i < items.length - 1 ? <span aria-hidden className="my-1 w-px flex-1 bg-border" /> : null}
          </span>
          <span className="flex min-w-0 flex-1 flex-col gap-2 pb-4">
            <span className="pt-0.5 text-sm leading-5 text-foreground">{item.text}</span>
            {item.extra}
          </span>
        </li>
      ))}
    </ol>
  );
}

/** A client's single primary action, full width; disabled with its final label until it can run. */
export function PrimaryAction({ variant }: { variant: Variant }) {
  const { server, labels, access } = useMcpConnect();
  const isMobile = useIsMobile();
  const action = actionFor(variant, server, access, isMobile);
  const label = labels[variant.actionLabel ?? ACTION_LABEL[variant.actionKind]];
  /* ChatGPT and Perplexity have no prefill link: their settings open once the URL is copied. */
  const handleCopied = () => {
    if (action?.kind === 'copyOpen') window.open(action.href, '_blank', 'noopener');
  };
  if (action?.kind === 'link') {
    return (
      <Button asChild size="default" className={BIG}>
        <a href={action.href} {...(action.newTab ? { target: '_blank', rel: 'noopener noreferrer' } : {})}>
          <ExternalLink className="size-4" aria-hidden />
          {label}
        </a>
      </Button>
    );
  }
  if (action) {
    return (
      <CopyButton value={action.text} onCopy={handleCopied} size="default" variant="default" className={BIG} iconClassName="size-4">
        {label}
      </CopyButton>
    );
  }
  return (
    <Button size="default" className={BIG} disabled>
      {label}
    </Button>
  );
}

export { SMALL as SMALL_ACTION, BIG as BIG_ACTION };
