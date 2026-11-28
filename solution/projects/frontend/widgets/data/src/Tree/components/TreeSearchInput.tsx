'use client';

import { Search, X } from 'lucide-react';
import { cn } from '@djangocfg/ui-core/lib';

import { useTreeContext } from '../context/TreeContext';
import { useTreeSearch } from '../context/hooks';

export interface TreeSearchInputProps {
  className?: string;
  showMatches?: boolean;
}

export function TreeSearchInput({ className, showMatches = true }: TreeSearchInputProps) {
  const { labels } = useTreeContext();
  const { query, setQuery, matchCount } = useTreeSearch();

  return (
    <div
      className={cn(
        'flex items-center gap-2 rounded-md border border-border bg-background px-2',
        className,
      )}
    >
      <Search aria-hidden className="size-3.5 shrink-0 text-muted-foreground" />
      <input
        type="search"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder={labels.searchPlaceholder}
        className="h-7 w-full bg-transparent text-sm outline-none placeholder:text-muted-foreground"
      />
      {showMatches && query.trim().length > 0 ? (
        <span className="shrink-0 text-xs text-muted-foreground">
          {labels.searchMatches(matchCount)}
        </span>
      ) : null}
      {query.length > 0 ? (
        <button
          type="button"
          onClick={() => setQuery('')}
          aria-label="Clear search"
          className="shrink-0 rounded p-1 text-muted-foreground hover:bg-accent hover:text-foreground"
        >
          <X aria-hidden className="size-3.5" />
        </button>
      ) : null}
    </div>
  );
}
