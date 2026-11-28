// Adapted from jalcoui (MIT) — github.com/jal-co/ui

'use client';

import * as React from 'react';
import {
  ArrowDownToLine,
  Circle,
  Pause,
  Play,
  Search,
  Terminal,
  Trash2,
  X,
} from 'lucide-react';
import { cn } from '@djangocfg/ui-core/lib';
import type { LogLevel } from '../types';
import { LEVEL_LABELS, getLevelToneClasses } from '../types';

interface ToolbarButtonProps {
  onClick: () => void;
  label: string;
  active?: boolean;
  children: React.ReactNode;
}

function ToolbarButton({ onClick, label, active, children }: ToolbarButtonProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-label={label}
      aria-pressed={active}
      className={cn(
        'inline-flex size-7 items-center justify-center rounded-md outline-none transition-colors',
        'text-muted-foreground hover:bg-accent hover:text-accent-foreground',
        'focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1',
        active && 'bg-accent text-accent-foreground',
      )}
    >
      {children}
    </button>
  );
}

export interface ToolbarProps {
  title: string;
  totalCount: number;
  filteredCount: number;
  levels: LogLevel[];
  activeLevels: Set<LogLevel>;
  toggleLevel: (level: LogLevel) => void;
  levelCounts: Partial<Record<LogLevel, number>>;
  searchQuery: string;
  setSearchQuery: (q: string) => void;
  autoScrollEnabled: boolean;
  paused: boolean;
  setPaused: (p: boolean) => void;
  onClear?: () => void;
}

/**
 * Header + filter row for the LogViewer. The level chips also serve as
 * the count badges — clicking strikes them out and removes the level
 * from the active set. The search input is always visible (no expand /
 * collapse toggle) because filter and search are the two main jobs of
 * the toolbar; hiding either is friction.
 */
export function Toolbar({
  title,
  totalCount,
  filteredCount,
  levels,
  activeLevels,
  toggleLevel,
  levelCounts,
  searchQuery,
  setSearchQuery,
  autoScrollEnabled,
  paused,
  setPaused,
  onClear,
}: ToolbarProps) {
  return (
    <div className="flex flex-col gap-2 border-b border-border/40 bg-muted/30 px-3 py-2">
      <div className="flex items-center gap-2">
        <Terminal className="size-3.5 shrink-0 text-muted-foreground" />
        <span className="flex-1 truncate text-sm font-medium text-foreground">
          {title}
        </span>

        <span className="mr-1 text-[10px] tabular-nums text-muted-foreground">
          {filteredCount}
          {filteredCount !== totalCount && ` / ${totalCount}`} lines
        </span>

        <div className="flex items-center gap-0.5">
          {autoScrollEnabled && (
            <ToolbarButton
              onClick={() => setPaused(!paused)}
              label={paused ? 'Resume auto-scroll' : 'Pause auto-scroll'}
              active={paused}
            >
              {paused ? (
                <Play className="size-3.5" />
              ) : (
                <Pause className="size-3.5" />
              )}
            </ToolbarButton>
          )}

          {onClear && (
            <ToolbarButton onClick={onClear} label="Clear logs">
              <Trash2 className="size-3.5" />
            </ToolbarButton>
          )}
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <div className="flex flex-wrap items-center gap-1">
          {levels.map((level) => {
            const tone = getLevelToneClasses(level);
            const isActive = activeLevels.has(level);
            const count = levelCounts[level] ?? 0;
            return (
              <button
                key={level}
                type="button"
                onClick={() => toggleLevel(level)}
                role="checkbox"
                aria-checked={isActive}
                aria-label={`${isActive ? 'Hide' : 'Show'} ${level} logs`}
                className={cn(
                  'inline-flex items-center gap-1 rounded-md px-2 py-1 text-[11px] font-medium outline-none transition-colors',
                  'focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-1',
                  isActive
                    ? tone.badge
                    : 'bg-muted/50 text-muted-foreground/60 line-through',
                )}
              >
                <Circle
                  className={cn(
                    'size-1.5 fill-current',
                    isActive ? tone.text : 'text-muted-foreground/40',
                  )}
                />
                {LEVEL_LABELS[level]}
                {count > 0 && <span className="tabular-nums">{count}</span>}
              </button>
            );
          })}
        </div>

        <div className="ml-auto flex items-center gap-1.5 rounded-md border border-border/40 bg-background px-2 py-1">
          <Search className="size-3 text-muted-foreground" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Filter…"
            aria-label="Filter logs"
            className="w-32 bg-transparent text-xs text-foreground outline-none placeholder:text-muted-foreground sm:w-40"
          />
          {searchQuery && (
            <button
              type="button"
              onClick={() => setSearchQuery('')}
              className="inline-flex size-4 items-center justify-center rounded text-muted-foreground hover:text-foreground"
              aria-label="Clear search"
            >
              <X className="size-3" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export interface ScrollToBottomPillProps {
  visible: boolean;
  onClick: () => void;
}

export function ScrollToBottomPill({ visible, onClick }: ScrollToBottomPillProps) {
  if (!visible) return null;
  return (
    <button
      type="button"
      onClick={onClick}
      className="flex w-full items-center justify-center gap-1.5 border-t border-border/40 bg-muted/30 py-1.5 text-[10px] font-medium text-muted-foreground transition-colors hover:bg-muted/50 hover:text-foreground"
      aria-label="Scroll to latest"
    >
      <ArrowDownToLine className="size-3" />
      New logs below
    </button>
  );
}
