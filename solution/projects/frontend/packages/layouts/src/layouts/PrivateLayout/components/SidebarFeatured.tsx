/**
 * Featured CTA tile for the sidebar — accent-tinted plate with icon, label,
 * optional inline badge, and a trailing arrow. Mailersend-style.
 */

'use client';

import { ArrowRight } from 'lucide-react';
import { Link } from '@djangocfg/ui-core/components';
import React from 'react';

import { cn } from '@djangocfg/ui-core/lib';

import { LucideIcon } from '../../../components';

import type { SidebarFeaturedConfig } from '../types';

// The accent names are the public prop's vocabulary; the status tokens they map
// to carry the meaning and already define both themes, so no `dark:` pair here.
const ACCENT_CLASS: Record<NonNullable<SidebarFeaturedConfig['accent']>, string> = {
  green: 'bg-success/10 text-success-foreground hover:bg-success/15',
  blue: 'bg-info/10 text-info-foreground hover:bg-info/15',
  amber: 'bg-warning/10 text-warning-foreground hover:bg-warning/15',
  primary: 'bg-primary/10 text-primary hover:bg-primary/15',
};

// Solid fill, so the text is the on-fill contrast color — `*-foreground` is the
// tint for the soft surface above and fails contrast on the fill.
const BADGE_ACCENT_CLASS: Record<NonNullable<SidebarFeaturedConfig['accent']>, string> = {
  green: 'bg-success text-on-success',
  blue: 'bg-info text-on-info',
  amber: 'bg-warning text-on-warning',
  primary: 'bg-primary text-primary-foreground',
};

interface SidebarFeaturedProps {
  config: SidebarFeaturedConfig;
}

export function SidebarFeatured({ config }: SidebarFeaturedProps) {
  const accent = config.accent ?? 'green';
  const tileClass = cn(
    'group/featured flex w-full items-center gap-2.5 rounded-lg px-2.5 py-2',
    'transition-colors',
    ACCENT_CLASS[accent],
  );

  const badgeNode = config.badge ? (
    <span
      className={cn(
        'inline-flex shrink-0 items-center rounded-md px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide',
        BADGE_ACCENT_CLASS[accent],
      )}
    >
      {config.badge}
    </span>
  ) : null;

  const iconNode = config.icon ? (
    <LucideIcon icon={config.icon} className="h-4 w-4 shrink-0" />
  ) : null;

  return (
    <Link href={config.href} className={tileClass}>
      {iconNode}
      {badgeNode}
      <span className="flex-1 truncate text-sm font-medium">{config.label}</span>
      <ArrowRight
        className="h-4 w-4 shrink-0 transition-transform duration-200 group-hover/featured:translate-x-0.5"
        aria-hidden
      />
    </Link>
  );
}
