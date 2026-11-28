/**
 * The view switcher: a row of icon buttons at the top of the menu. The active view also shows its label, so the row
 * names where you are without spending width on the others (Notion's Home / Chat / Calendar strip).
 */

'use client';

import React from 'react';

import { cn } from '@djangocfg/ui-core/lib';

import { LucideIcon } from '../../../components';
import type { SidebarViewConfig } from '../types';

interface SidebarViewsProps {
  views: SidebarViewConfig[];
  active: string;
  onChange: (id: string) => void;
}

export function SidebarViews({ views, active, onChange }: SidebarViewsProps) {
  return (
    <div role="tablist" aria-label="Sidebar views" className="mb-1 flex items-center gap-1 px-2">
      {views.map((view) => {
        const on = view.id === active;
        return (
          <button
            key={view.id}
            type="button"
            role="tab"
            aria-selected={on}
            aria-label={view.label}
            title={view.label}
            onClick={() => onChange(view.id)}
            className={cn(
              'flex h-(--sidebar-item-h) items-center gap-2 rounded-(--sidebar-item-radius) px-2 text-(length:--sidebar-item-font) transition-colors',
              '[&>svg]:size-4 [&>svg]:shrink-0',
              on ? 'bg-sidebar-accent font-medium text-sidebar-foreground' : 'text-sidebar-foreground/70 hover:bg-sidebar-accent/70 hover:text-sidebar-foreground',
            )}
          >
            <LucideIcon icon={view.icon} />
            {on ? <span>{view.label}</span> : null}
          </button>
        );
      })}
    </div>
  );
}
