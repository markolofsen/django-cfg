'use client';

import React from 'react';

import { cn } from '@djangocfg/ui-core/lib';

import { useSettingsContext } from '../context';

/**
 * Mobile nav — a horizontal, scrollable strip of section chips (Claude's
 * phone settings pattern). Shown instead of the vertical rail below `md`.
 * Groups are flattened (a phone strip has no room for group headers); the
 * active chip is a solid pill.
 */
export const SettingsTabs: React.FC = () => {
  const { groups, activeId, setActive } = useSettingsContext();
  const sections = groups.flatMap((g) => g.sections);
  const activeRef = React.useRef<HTMLButtonElement>(null);

  // Keep the active chip in view when it changes (e.g. deep-link).
  React.useEffect(() => {
    activeRef.current?.scrollIntoView({ inline: 'center', block: 'nearest' });
  }, [activeId]);

  return (
    <div
      role="tablist"
      aria-orientation="horizontal"
      className="flex gap-1 overflow-x-auto px-1 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden"
    >
      {sections.map((section) => {
        const active = section.id === activeId;
        return (
          <button
            key={section.id}
            ref={active ? activeRef : undefined}
            type="button"
            role="tab"
            aria-selected={active}
            onClick={() => setActive(section.id)}
            // Text-only chips on mobile (no icons — keeps the strip compact, like Claude).
            className={cn(
              'rounded-control inline-flex shrink-0 items-center px-3 py-1.5 text-sm whitespace-nowrap',
              'outline-none transition-colors focus-visible:ring-1 focus-visible:ring-ring',
              active
                ? 'bg-popover font-medium text-foreground'
                : 'text-muted-foreground hover:text-foreground',
            )}
          >
            {section.label}
          </button>
        );
      })}
    </div>
  );
};
