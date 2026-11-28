'use client';

import React from 'react';

import { useAppT } from '@djangocfg/i18n';
import { cn } from '@djangocfg/ui-core/lib';
import { Search, X } from 'lucide-react';

import { useSettingsCopy } from '../i18n';
import { useSettingsContext } from '../context';

/**
 * Search box atop the nav rail. Filters sections by label + keywords (logic in
 * useSettingsSections). Mirrors the Claude.ai settings search affordance: a
 * quiet, rounded field with a leading magnifier and a clear button.
 */
export const SettingsSearch: React.FC = () => {
  const { query, setQuery } = useSettingsContext();
  const t = useAppT();
  const copy = useSettingsCopy();
  const placeholder = t('ui.select.search') || 'Search';

  return (
    <div className="relative">
      <Search className="pointer-events-none absolute left-2.5 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder={placeholder}
        aria-label={placeholder}
        className={cn(
          'h-8 w-full rounded-lg border border-transparent bg-foreground/[0.05] pl-8 pr-8 text-base md:text-sm',
          'text-foreground placeholder:text-muted-foreground',
          'outline-none transition-[border-color,background-color,box-shadow]',
          // Crisp thin accent outline (matches ui-core Input), no blurry halo.
          'focus-visible:border-ring focus-visible:ring-1 focus-visible:ring-ring',
        )}
      />
      {query && (
        <button
          type="button"
          onClick={() => setQuery('')}
          aria-label={copy.search.clear}
          className="absolute right-2 top-1/2 -translate-y-1/2 rounded-sm p-0.5 text-muted-foreground transition-colors hover:text-foreground"
        >
          <X className="size-3.5" />
        </button>
      )}
    </div>
  );
};
