'use client'

import React, { useEffect, useMemo, useRef, useState } from 'react'
import { useStore } from 'zustand'

import { Badge, Button, Input } from '@djangocfg/ui-core/components'
import { cn } from '@djangocfg/ui-core/lib'
import { Copy, Trash2 } from 'lucide-react'

import { devtoolsStore } from '../store'
import type { LogEntry, LogLevel } from '../types'

const LEVELS: LogLevel[] = ['debug', 'info', 'success', 'warn', 'error']

// Log levels ARE the status vocabulary, so they read from status tokens: a
// preset that retunes "warning" retunes the warn line with it.
const LEVEL_COLORS: Record<LogLevel, string> = {
  debug: 'text-muted-foreground',
  info: 'text-info',
  success: 'text-success',
  warn: 'text-warning',
  error: 'text-destructive',
}

function formatTime(d: Date): string {
  return d.toTimeString().slice(0, 8) + '.' + String(d.getMilliseconds()).padStart(3, '0')
}

function Row({ entry }: { entry: LogEntry }) {
  const [expanded, setExpanded] = useState(false)
  const hasDetails = Boolean(entry.stack || (entry.data && Object.keys(entry.data).length > 0))

  return (
    <div
      className={cn(
        'border-b border-border/50 px-3 py-1.5 font-mono text-xs leading-relaxed',
        hasDetails && 'cursor-pointer hover:bg-muted/50',
      )}
      onClick={hasDetails ? () => setExpanded((v) => !v) : undefined}
    >
      <div className="flex items-baseline gap-2">
        <span className="shrink-0 tabular-nums text-muted-foreground/70">
          {formatTime(entry.timestamp)}
        </span>
        <span className={cn('shrink-0 font-semibold uppercase', LEVEL_COLORS[entry.level])}>
          {entry.level}
        </span>
        <span className="shrink-0 text-muted-foreground">{entry.source}</span>
        <span className="min-w-0 break-words">{entry.message}</span>
      </div>
      {expanded && (
        <div className="mt-1 space-y-1 pl-2">
          {entry.data && Object.keys(entry.data).length > 0 && (
            <pre className="overflow-x-auto rounded bg-muted/60 p-2 text-[11px]">
              {JSON.stringify(entry.data, null, 2)}
            </pre>
          )}
          {entry.stack && (
            <pre className="overflow-x-auto rounded bg-muted/60 p-2 text-[11px] text-destructive/90">
              {entry.stack}
            </pre>
          )}
        </div>
      )}
    </div>
  )
}

export function LogsTab({ isActive }: { isActive: boolean }) {
  const entries = useStore(devtoolsStore, (s) => s.entries)
  const clearEntries = useStore(devtoolsStore, (s) => s.clearEntries)

  const [levels, setLevels] = useState<Set<LogLevel>>(new Set(LEVELS))
  const [search, setSearch] = useState('')
  const scrollRef = useRef<HTMLDivElement>(null)

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase()
    return entries.filter((e) => {
      if (!levels.has(e.level)) return false
      if (!q) return true
      return (
        e.message.toLowerCase().includes(q) ||
        e.source.toLowerCase().includes(q) ||
        (e.data ? JSON.stringify(e.data).toLowerCase().includes(q) : false)
      )
    })
  }, [entries, levels, search])

  // Follow the tail while the tab is visible
  useEffect(() => {
    if (!isActive) return
    const el = scrollRef.current
    if (el) el.scrollTop = el.scrollHeight
  }, [filtered.length, isActive])

  const toggleLevel = (level: LogLevel) =>
    setLevels((prev) => {
      const next = new Set(prev)
      if (next.has(level)) next.delete(level)
      else next.add(level)
      return next
    })

  return (
    <div className="flex h-full flex-col">
      {/* Toolbar */}
      <div className="flex shrink-0 items-center gap-2 border-b border-border px-3 py-1.5">
        <div className="flex items-center gap-1">
          {LEVELS.map((level) => (
            <button
              key={level}
              type="button"
              onClick={() => toggleLevel(level)}
              className={cn(
                'rounded px-1.5 py-0.5 text-[10px] font-semibold uppercase transition-colors',
                levels.has(level)
                  ? cn('bg-muted', LEVEL_COLORS[level])
                  : 'text-muted-foreground/40 hover:text-muted-foreground',
              )}
            >
              {level}
            </button>
          ))}
        </div>
        <Input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Filter…"
          className="h-6 flex-1 text-xs"
        />
        <Badge variant="secondary" className="text-[10px] tabular-nums">
          {filtered.length}
        </Badge>
        <Button
          variant="ghost"
          size="icon"
          className="h-6 w-6"
          title="Copy visible entries as JSON"
          onClick={() => navigator.clipboard?.writeText(JSON.stringify(filtered, null, 2))}
        >
          <Copy className="h-3 w-3" />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          className="h-6 w-6"
          title="Clear"
          onClick={clearEntries}
        >
          <Trash2 className="h-3 w-3" />
        </Button>
      </div>

      {/* Entries */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto">
        {filtered.length === 0 ? (
          <div className="flex h-full items-center justify-center text-xs text-muted-foreground">
            No log entries
          </div>
        ) : (
          filtered.map((entry) => <Row key={entry.id} entry={entry} />)
        )}
      </div>
    </div>
  )
}
