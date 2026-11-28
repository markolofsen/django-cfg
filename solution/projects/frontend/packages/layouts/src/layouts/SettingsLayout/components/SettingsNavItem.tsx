'use client';

import React from 'react';

import { cn } from '@djangocfg/ui-core/lib';

import type { SettingsSection } from '../types';

interface SettingsNavItemProps {
  section: SettingsSection;
  active: boolean;
  onSelect: (id: string) => void;
}

/**
 * One row in the settings nav rail: icon + label, with a trailing badge slot.
 * Active state uses the semantic `accent` token (theme-correct in dark/light)
 * rather than a hard-coded colour, matching the rest of the design system.
 */
export const SettingsNavItem: React.FC<SettingsNavItemProps> = ({
  section,
  active,
  onSelect,
}) => {
  const Icon = section.icon;

  return (
    <button
      type="button"
      role="tab"
      aria-selected={active}
      onClick={() => onSelect(section.id)}
      className={cn(
        'group flex h-8 w-full items-center gap-2.5 rounded-lg px-2.5 text-left text-sm',
        'outline-none transition-colors',
        'focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1 focus-visible:ring-offset-background',
        active
          // Neutral foreground overlay, like the app sidebar — theme-agnostic.
          ? 'bg-foreground/10 text-foreground'
          : 'text-foreground/90 hover:bg-foreground/[0.07]',
      )}
    >
      {Icon && (
        <Icon
          className={cn(
            'size-4 shrink-0 transition-colors',
            'text-foreground/80 group-hover:text-foreground',
          )}
        />
      )}
      <span className="flex-1 truncate">{section.label}</span>
      {section.badge && <span className="shrink-0">{section.badge}</span>}
    </button>
  );
};
