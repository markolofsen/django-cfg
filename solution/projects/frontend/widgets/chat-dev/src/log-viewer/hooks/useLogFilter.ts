// Adapted from jalcoui (MIT) — github.com/jal-co/ui

'use client';

import * as React from 'react';
import type { LogEntry, LogLevel } from '../types';
import { stripAnsi } from '../utils/ansi';

interface UseLogFilterArgs {
  entries: LogEntry[];
  activeLevels: Set<LogLevel>;
  searchQuery: string;
}

interface UseLogFilterResult {
  filtered: LogEntry[];
  /** Counts per level for the **unfiltered** entries — feeds the filter
   * chip badges. */
  counts: Partial<Record<LogLevel, number>>;
}

/**
 * Filter + search the entry list. Both operations route through one
 * pass over `entries` so a 10k-entry list with both filters active
 * costs one iteration, not two. The result is memoized on the input
 * identity — callers that only append to `entries` get an incremental
 * O(n) re-derivation (acceptable for 10k+; if it ever bites, switch
 * to a streaming filter that reuses the prior result).
 *
 * Search is case-insensitive and strips ANSI escapes from the haystack
 * — a search for `"port 3000"` matches `\x1b[32mport 3000\x1b[0m` too.
 */
export function useLogFilter({
  entries,
  activeLevels,
  searchQuery,
}: UseLogFilterArgs): UseLogFilterResult {
  return React.useMemo(() => {
    const counts: Partial<Record<LogLevel, number>> = {};
    const filtered: LogEntry[] = [];
    const needle = searchQuery.trim().toLowerCase();
    const hasSearch = needle.length > 0;

    for (let i = 0; i < entries.length; i += 1) {
      const entry = entries[i];
      if (entry === undefined) continue;
      counts[entry.level] = (counts[entry.level] ?? 0) + 1;

      if (!activeLevels.has(entry.level)) continue;
      if (hasSearch) {
        const haystack = stripAnsi(entry.message).toLowerCase();
        if (!haystack.includes(needle)) continue;
      }
      filtered.push(entry);
    }

    return { filtered, counts };
  }, [entries, activeLevels, searchQuery]);
}
