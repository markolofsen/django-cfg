// Adapted from jalcoui (MIT) — github.com/jal-co/ui
//
// Streaming log viewer with per-level filtering, search, ANSI rendering,
// and sticky-bottom auto-scroll. Virtualized via `react-virtuoso` (the
// same library `chat/messages/MessageList` and `data/DataGrid` build on
// — no new virt dep). Handles 10k+ entries without lag.
//
// Decomposition:
//   - components/Toolbar      header, level chips, search input
//   - components/LogRow       single row + ANSI render + search highlight
//   - hooks/useLogFilter      filter + search single-pass derivation
//   - hooks/useAutoScroll     sticky-bottom controller wrapping Virtuoso
//   - utils/ansi              SGR parser → semantic tone segments

'use client';

import * as React from 'react';
import { Virtuoso } from 'react-virtuoso';
import { cn } from '@djangocfg/ui-core/lib';

import type { LogLevel, LogViewerProps } from './types';
import { useLogFilter } from './hooks/useLogFilter';
import { useAutoScroll } from './hooks/useAutoScroll';
import { Toolbar, ScrollToBottomPill } from './components/Toolbar';
import { LogRow } from './components/LogRow';

const DEFAULT_LEVELS: LogLevel[] = ['error', 'warn', 'info', 'debug', 'verbose'];

// Threshold above which Virtuoso wins outright. Below it, the plain
// `.map()` path is fine and keeps the DOM debuggable.
const VIRTUALIZE_THRESHOLD = 100;

export function LogViewer({
  entries,
  title = 'Logs',
  maxHeight = 400,
  lineNumbers = true,
  timestamps = true,
  autoScroll = true,
  levels = DEFAULT_LEVELS,
  ansi = true,
  onClear,
  noVirtualize = false,
  className,
  ...divProps
}: LogViewerProps) {
  const [activeLevels, setActiveLevels] = React.useState<Set<LogLevel>>(
    () => new Set(levels),
  );
  const [searchQuery, setSearchQuery] = React.useState('');
  const [paused, setPaused] = React.useState(false);

  // If the caller changes the available `levels` list (e.g. story
  // toggles), reseed the active set. Compare by sorted join — a new
  // array literal of the same levels shouldn't reset user toggles.
  const levelsKey = React.useMemo(() => [...levels].sort().join(','), [levels]);
  React.useEffect(() => {
    setActiveLevels(new Set(levels));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [levelsKey]);

  const toggleLevel = React.useCallback((level: LogLevel) => {
    setActiveLevels((prev) => {
      const next = new Set(prev);
      if (next.has(level)) {
        next.delete(level);
      } else {
        next.add(level);
      }
      return next;
    });
  }, []);

  const { filtered, counts } = useLogFilter({
    entries,
    activeLevels,
    searchQuery,
  });

  const { virtuosoRef, isAtBottom, onAtBottomChange, scrollToBottom } =
    useAutoScroll(filtered.length, autoScroll && !paused);

  // Line-number gutter width — based on total count, not filtered, so the
  // gutter doesn't reflow when the user toggles a filter.
  const lineNumberWidth = Math.max(String(entries.length).length, 3);

  const shouldVirtualize = !noVirtualize && filtered.length > VIRTUALIZE_THRESHOLD;

  const renderRow = React.useCallback(
    (index: number, entry: (typeof filtered)[number]) => (
      <LogRow
        entry={entry}
        index={index}
        lineNumberWidth={lineNumberWidth}
        showLineNumbers={lineNumbers}
        showTimestamps={timestamps}
        ansi={ansi}
        searchQuery={searchQuery}
      />
    ),
    [lineNumberWidth, lineNumbers, timestamps, ansi, searchQuery],
  );

  const isEmpty = filtered.length === 0;
  const hasActiveFilter =
    searchQuery.length > 0 || activeLevels.size < levels.length;

  const resetFilters = React.useCallback(() => {
    setSearchQuery('');
    setActiveLevels(new Set(levels));
  }, [levels]);

  return (
    <div
      data-slot="log-viewer"
      className={cn(
        'flex flex-col overflow-hidden rounded-xl border border-border/60 bg-card shadow-sm',
        className,
      )}
      {...divProps}
    >
      <Toolbar
        title={title}
        totalCount={entries.length}
        filteredCount={filtered.length}
        levels={levels}
        activeLevels={activeLevels}
        toggleLevel={toggleLevel}
        levelCounts={counts}
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
        autoScrollEnabled={autoScroll}
        paused={paused}
        setPaused={setPaused}
        onClear={onClear}
      />

      <div
        className="font-mono text-xs leading-relaxed [scrollbar-width:thin]"
        style={{ height: maxHeight }}
        role="log"
        aria-live="polite"
        aria-label={title}
      >
        {isEmpty ? (
          <div className="flex h-full flex-col items-center justify-center gap-1 text-sm text-muted-foreground">
            <span>
              {entries.length === 0
                ? 'No log entries.'
                : 'No matching log entries.'}
            </span>
            {hasActiveFilter && entries.length > 0 && (
              <button
                type="button"
                onClick={resetFilters}
                className="text-xs text-muted-foreground underline underline-offset-2 hover:text-foreground"
              >
                Reset filters
              </button>
            )}
          </div>
        ) : shouldVirtualize ? (
          <Virtuoso
            ref={virtuosoRef}
            data={filtered}
            atBottomStateChange={onAtBottomChange}
            atBottomThreshold={40}
            followOutput={autoScroll && !paused ? 'auto' : false}
            itemContent={renderRow}
            increaseViewportBy={{ top: 200, bottom: 400 }}
            style={{ height: '100%' }}
          />
        ) : (
          <div className="h-full overflow-auto [scrollbar-width:thin]">
            {filtered.map((entry, i) => (
              <LogRow
                key={i}
                entry={entry}
                index={i}
                lineNumberWidth={lineNumberWidth}
                showLineNumbers={lineNumbers}
                showTimestamps={timestamps}
                ansi={ansi}
                searchQuery={searchQuery}
              />
            ))}
          </div>
        )}
      </div>

      <ScrollToBottomPill visible={!isAtBottom && !isEmpty} onClick={scrollToBottom} />
    </div>
  );
}
