// Adapted from jalcoui (MIT) — github.com/jal-co/ui

'use client';


import * as React from 'react';
import { Popover, PopoverContent, PopoverTrigger } from '@djangocfg/ui-core';
import { alpha } from '@djangocfg/ui-core/styles/palette';
import type { Commit } from '../types';
import { formatFullDate, initials } from '../utils';

interface CommitDetailProps {
  commit: Commit;
  hashLength: number;
  railColor: string;
  children: React.ReactNode;
}

/**
 * Popover with the full commit message, refs, tag and parent hashes. The
 * trigger is the row button — the parent component owns the row markup and
 * passes it through `children`.
 *
 * Requires the host app to mount `<UiProviders>` at the root (we do not
 * remount a Popover provider here — see CONTRACT §5).
 */
export function CommitDetail({
  commit,
  hashLength,
  railColor,
  children,
}: CommitDetailProps) {
  // Pre-compute style strings outside JSX (per project rule: hoist derived
  // values into named consts before `return (...)`).
  const tagStyle = {
    backgroundColor: alpha(railColor, 0.125),
    color: railColor,
  };
  const initialsLabel = initials(commit.author.name);

  return (
    <Popover>
      <PopoverTrigger asChild>{children}</PopoverTrigger>
      <PopoverContent side="right" sideOffset={8} className="w-80 p-3">
        <div className="flex flex-col gap-2">
          <p className="text-sm font-medium leading-snug">{commit.message}</p>

          <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
            <span className="inline-flex items-center gap-1.5">
              {commit.author.avatarUrl ? (
                <img
                  src={commit.author.avatarUrl}
                  alt=""
                  width={14}
                  height={14}
                  className="size-3.5 rounded-full border border-border/60 bg-muted"
                />
              ) : (
                <span className="flex size-3.5 items-center justify-center rounded-full bg-muted text-[7px] font-bold">
                  {initialsLabel}
                </span>
              )}
              {commit.author.name}
            </span>
            <span className="text-border">·</span>
            <code className="rounded bg-muted px-1 py-0.5 font-mono text-[10px]">
              {commit.hash.slice(0, hashLength)}
            </code>
          </div>

          <div className="text-[11px] text-muted-foreground">
            {formatFullDate(commit.date)}
          </div>

          {(commit.refs || commit.tag) && (
            <div className="flex flex-wrap gap-1">
              {commit.refs?.map((ref) => (
                <span
                  key={ref}
                  className="inline-flex items-center gap-1 rounded-md border border-border/60 bg-muted/50 px-1.5 py-0.5 text-[10px] font-medium text-muted-foreground"
                >
                  {ref}
                </span>
              ))}
              {commit.tag && (
                <span
                  className="inline-flex items-center rounded-md px-1.5 py-0.5 text-[10px] font-medium"
                  style={tagStyle}
                >
                  {commit.tag}
                </span>
              )}
            </div>
          )}

          {commit.parents.length > 0 && (
            <div className="text-[10px] text-muted-foreground/60">
              {commit.parents.length === 1 ? 'Parent' : 'Parents'}:{' '}
              {commit.parents.map((p) => p.slice(0, hashLength)).join(', ')}
            </div>
          )}
        </div>
      </PopoverContent>
    </Popover>
  );
}
