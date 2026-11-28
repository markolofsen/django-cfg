'use client';

import * as React from 'react';
import { Search, X } from 'lucide-react';

import { Input } from '@djangocfg/ui-core/components';
import { cn } from '@djangocfg/ui-core/lib';

import { LocaleCard } from './LocaleCard';
import { getLocaleMeta, type LocaleMeta } from './localeMeta';

export interface LocaleGridProps {
  locale: string;
  locales: string[];
  onSelect: (locale: string) => void;
  labels?: Record<string, string>;
  searchPlaceholder?: string;
  emptyResults?: string;
  /** Force compact (single-column list) layout. @default false (grid on ≥sm) */
  compact?: boolean;
  /** Search input visibility. Auto-shown when more than `searchThreshold` locales. */
  searchThreshold?: number;
}

interface LocaleEntry {
  code: string;
  meta: LocaleMeta;
}

const DEFAULT_SEARCH_THRESHOLD = 8;

export function LocaleGrid({
  locale,
  locales,
  onSelect,
  labels,
  searchPlaceholder = 'Search language…',
  emptyResults = 'No languages found',
  compact = false,
  searchThreshold = DEFAULT_SEARCH_THRESHOLD,
}: LocaleGridProps) {
  const [query, setQuery] = React.useState('');

  const entries = React.useMemo<LocaleEntry[]>(
    () =>
      locales.map((code) => ({
        code,
        meta: getLocaleMeta(code, labels),
      })),
    [locales, labels],
  );

  const showSearch = entries.length > searchThreshold;

  const filtered = React.useMemo(() => {
    if (!query.trim()) return entries;
    const q = query.trim().toLowerCase();
    return entries.filter(
      (e) =>
        e.code.toLowerCase().includes(q) ||
        e.meta.native.toLowerCase().includes(q) ||
        e.meta.english.toLowerCase().includes(q),
    );
  }, [entries, query]);

  return (
    <div className="flex h-full min-h-0 flex-col gap-4">
      {showSearch && (
        // `p-px` reserves the focus-ring offset so it isn't clipped by the
        // scroll container below.
        <div className="relative shrink-0 p-px">
          <Search
            className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground"
            aria-hidden
          />
          <Input
            type="search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={searchPlaceholder}
            className="h-11 rounded-xl pl-10 pr-9"
            // Avoid forcing the keyboard open on mobile.
            autoFocus={false}
          />
          {query && (
            <button
              type="button"
              onClick={() => setQuery('')}
              aria-label="Clear search"
              className="absolute right-2.5 top-1/2 inline-flex h-7 w-7 -translate-y-1/2 cursor-pointer items-center justify-center rounded-full text-muted-foreground hover:bg-muted hover:text-foreground"
            >
              <X className="h-3.5 w-3.5" />
            </button>
          )}
        </div>
      )}

      {/* `p-px` reserves the focus / active ring offset around cards. */}
      <div className="flex-1 min-h-0 overflow-y-auto p-px">
        {filtered.length === 0 ? (
          <div className="flex h-full items-center justify-center py-12 text-sm text-muted-foreground">
            {emptyResults}
          </div>
        ) : (
          <div
            className={cn(
              'grid gap-2.5',
              compact
                ? 'grid-cols-1'
                : 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4',
            )}
          >
            {filtered.map(({ code, meta }) => (
              <LocaleCard
                key={code}
                code={code}
                meta={meta}
                active={code === locale}
                onSelect={onSelect}
                compact={compact}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
