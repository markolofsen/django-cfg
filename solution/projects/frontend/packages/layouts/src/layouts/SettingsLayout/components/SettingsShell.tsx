'use client';

import React from 'react';

import { useIsMobile } from '@djangocfg/ui-core/hooks';
import { cn } from '@djangocfg/ui-core/lib';

import { useSettingsContext } from '../context';
import { SettingsNav } from './SettingsNav';
import { SettingsPanel } from './SettingsPanel';
import { SettingsTabs } from './SettingsTabs';

interface SettingsShellProps {
  /** Drop the outer rounding/border when embedded in a bare dialog. */
  bare?: boolean;
  className?: string;
}

/**
 * Master/detail shell that reshapes for mobile (Claude settings pattern):
 *   - desktop (≥md): vertical nav rail on the left + detail panel on the right.
 *   - mobile  (<md): a horizontal scrollable tab strip on top + panel below.
 *
 * The breakpoint is read with `useIsMobile` (SSR-safe; false on the server,
 * re-syncs on mount) rather than CSS, because the two layouts use genuinely
 * different nav components (vertical grouped rail vs. flat horizontal strip),
 * not just a flex-direction flip.
 *
 * Height-bounded by its container (the dialog sets max-height); the panel
 * scrolls independently inside it.
 */
export const SettingsShell: React.FC<SettingsShellProps> = ({ bare = false, className }) => {
  const isMobile = useIsMobile();
  const { title } = useSettingsContext();

  const frame = cn(
    'flex h-full min-h-0 w-full flex-col overflow-hidden',
    !bare && 'rounded-[var(--radius-dialog)] border border-border bg-background',
    className,
  );

  // ── Mobile: title header + tab strip on top, panel below ──
  if (isMobile) {
    return (
      <div className={frame}>
        <div className="shrink-0 bg-background">
          {/* Title row — `pr-12` leaves room for the dialog's corner close button. */}
          <div className="flex items-center gap-3 px-4 pb-2 pt-3.5 pr-12">
            <h2 className="flex-1 truncate text-base font-semibold tracking-tight text-foreground">
              {title}
            </h2>
          </div>
          {/* Tabs on their own row (below the header), so nothing overlaps the X. */}
          <div className="border-b border-foreground/10 px-1.5 pb-2">
            <SettingsTabs />
          </div>
        </div>
        <section className="min-h-0 flex-1 bg-card">
          <SettingsPanel />
        </section>
      </div>
    );
  }

  // ── Desktop: header bar, then rail + panel on one surface ──
  return (
    <div className={frame}>
      <header className="flex h-11 shrink-0 items-center border-b border-foreground/[0.12] px-5 pr-14">
        <h2 className="truncate text-lg font-medium text-foreground">{title}</h2>
      </header>
      <div className="flex min-h-0 flex-1">
        <aside className="flex w-[13.25rem] shrink-0 flex-col border-e border-foreground/10 bg-background p-3">
          <SettingsNav />
        </aside>
        <section className="min-h-0 flex-1">
          <SettingsPanel />
        </section>
      </div>
    </div>
  );
};
