'use client'

import React, { useMemo, useState } from 'react'
import { useStore } from 'zustand'

import { Badge, Button } from '@djangocfg/ui-core/components'
import { cn } from '@djangocfg/ui-core/lib'
import { Bug, Maximize2, Minimize2, ScrollText, X } from 'lucide-react'

import { devtoolsStore } from '../store'
import type { CustomDebugTab } from '../types'
import { LogsTab } from './LogsTab'

export interface DevtoolsPanelProps {
  /** Additional app-specific tabs */
  tabs?: CustomDebugTab[]
  position?: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left'
  defaultHeight?: number
  defaultWidth?: number
}

const POSITION_STYLES: Record<NonNullable<DevtoolsPanelProps['position']>, React.CSSProperties> = {
  'bottom-right': { bottom: 16, right: 16 },
  'bottom-left': { bottom: 16, left: 16 },
  'top-right': { top: 16, right: 16 },
  'top-left': { top: 16, left: 16 },
}

export function DevtoolsPanel({
  tabs: customTabs = [],
  position = 'bottom-left',
  defaultHeight = 480,
  defaultWidth = 560,
}: DevtoolsPanelProps) {
  const isOpen = useStore(devtoolsStore, (s) => s.isOpen)
  const activeTab = useStore(devtoolsStore, (s) => s.tab)
  const setTab = useStore(devtoolsStore, (s) => s.setTab)
  const closePanel = useStore(devtoolsStore, (s) => s.closePanel)
  const errorCount = useStore(devtoolsStore, (s) =>
    s.entries.reduce((n, e) => (e.level === 'error' ? n + 1 : n), 0),
  )

  const [isMinimized, setIsMinimized] = useState(false)

  const allTabs = useMemo(
    () => [
      { id: 'logs', label: 'Logs', icon: ScrollText as React.ElementType },
      ...customTabs.map((t) => ({ id: t.id, label: t.label, icon: t.icon })),
    ],
    [customTabs],
  )

  if (!isOpen) return null

  return (
    <div
      className="fixed z-[99999] flex flex-col overflow-hidden rounded-lg border border-border bg-background shadow-xl"
      style={{
        ...POSITION_STYLES[position],
        width: defaultWidth,
        maxWidth: 'calc(100vw - 32px)',
        height: isMinimized ? 40 : defaultHeight,
        maxHeight: 'calc(100vh - 32px)',
      }}
    >
      {/* Header */}
      <div className="flex shrink-0 items-center gap-2 border-b border-border bg-muted/50 px-3 py-1.5">
        <Bug className="h-4 w-4 text-primary" />
        <span className="text-sm font-medium">Devtools</span>
        {errorCount > 0 && (
          <Badge variant="destructive" className="text-[10px]">
            {errorCount} {errorCount === 1 ? 'error' : 'errors'}
          </Badge>
        )}

        {!isMinimized && (
          <div className="ml-3 flex items-center gap-0.5">
            {allTabs.map((tab) => {
              const Icon = tab.icon as React.ComponentType<{ className?: string }>
              const isActive = activeTab === tab.id
              return (
                <button
                  key={tab.id}
                  type="button"
                  onClick={() => setTab(tab.id)}
                  className={cn(
                    'flex items-center gap-1.5 rounded px-2 py-0.5 text-xs transition-colors',
                    isActive
                      ? 'bg-background text-foreground shadow-sm'
                      : 'text-muted-foreground hover:bg-muted hover:text-foreground',
                  )}
                >
                  <Icon className="h-3 w-3" />
                  {tab.label}
                </button>
              )
            })}
          </div>
        )}

        <div className="ml-auto flex items-center gap-1">
          <Button
            variant="ghost"
            size="icon"
            className="h-6 w-6"
            tooltip={isMinimized ? 'Expand' : 'Minimize'}
            onClick={() => setIsMinimized((v) => !v)}
          >
            {isMinimized ? <Maximize2 className="h-3.5 w-3.5" /> : <Minimize2 className="h-3.5 w-3.5" />}
          </Button>
          <Button variant="ghost" size="icon" className="h-6 w-6" tooltip="Close" onClick={closePanel}>
            <X className="h-3.5 w-3.5" />
          </Button>
        </div>
      </div>

      {/* Content */}
      {!isMinimized && (
        <div className="min-h-0 flex-1">
          {activeTab === 'logs' && <LogsTab isActive />}
          {customTabs.map((tab) => {
            const Panel = tab.panel
            return (
              <div key={tab.id} className={cn('h-full', activeTab !== tab.id && 'hidden')}>
                <Panel isActive={activeTab === tab.id} />
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
