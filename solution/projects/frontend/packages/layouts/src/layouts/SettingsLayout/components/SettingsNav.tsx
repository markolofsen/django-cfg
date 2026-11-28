'use client';

import React from 'react';

import { cn } from '@djangocfg/ui-core/lib';

import { useSettingsContext } from '../context';
import { SettingsNavItem } from './SettingsNavItem';
import { SettingsSearch } from './SettingsSearch';

/**
 * Left rail: optional title, optional search, then grouped section items.
 * Groups with a label render a small muted header; the default (unlabelled)
 * group renders bare. Empty search results show a quiet "no matches" line.
 */
export const SettingsNav: React.FC = () => {
  const { groups, searchable, activeId, setActive, query } = useSettingsContext();

  const hasResults = groups.some((g) => g.sections.length > 0);

  return (
    <nav
      role="tablist"
      aria-orientation="vertical"
      className="flex h-full flex-col gap-2"
    >
      {searchable && (
        <div className="px-1">
          <SettingsSearch />
        </div>
      )}

      <div className="flex-1 space-y-4 overflow-y-auto px-1 pb-2">
        {!hasResults && query && (
          <p className="px-2.5 py-6 text-center text-xs text-muted-foreground">
            No matching settings
          </p>
        )}

        {groups.map((group) =>
          group.sections.length === 0 ? null : (
            <div key={group.id} className="space-y-0.5">
              {group.label && (
                <div
                  className={cn(
                    'px-2.5 pb-1 pt-1 text-xs',
                    'text-muted-foreground',
                  )}
                >
                  {group.label}
                </div>
              )}
              {group.sections.map((section) => (
                <SettingsNavItem
                  key={section.id}
                  section={section}
                  active={section.id === activeId}
                  onSelect={setActive}
                />
              ))}
            </div>
          ),
        )}
      </div>
    </nav>
  );
};
