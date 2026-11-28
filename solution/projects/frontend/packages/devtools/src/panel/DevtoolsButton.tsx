'use client'

import React, { useCallback, useEffect, useRef } from 'react'
import { useStore } from 'zustand'

import { TooltipHint } from '@djangocfg/ui-core/components'
import { useHotkey } from '@djangocfg/ui-core/hooks'
import { cn } from '@djangocfg/ui-core/lib'
import { Bug } from 'lucide-react'

import { isDevelopment } from '../internal'
import { devtoolsStore } from '../store'
import { useDebugMode } from '../useDebugMode'
import { DevtoolsPanel } from './DevtoolsPanel'
import type { DevtoolsPanelProps } from './DevtoolsPanel'

export interface DevtoolsButtonProps {
  className?: string
  /** Props forwarded to the panel */
  panel?: DevtoolsPanelProps
  /**
   * Explicitly disable. Default: undefined (auto — visible in dev, hidden in
   * prod, `?debug=1` always unlocks).
   */
  enabled?: boolean
}

/**
 * Floating debug button.
 *
 * Visibility:
 * 1. `enabled === false` and no `?debug=1` → renders nothing
 * 2. dev or `?debug=1` → visible button + ⌘D shortcut
 * 3. prod without `?debug=1` → invisible click trap (5 clicks in 2s unlock)
 */
export function DevtoolsButton({ className, panel = {}, enabled }: DevtoolsButtonProps) {
  const isOpen = useStore(devtoolsStore, (s) => s.isOpen)
  const togglePanel = useStore(devtoolsStore, (s) => s.togglePanel)
  const errorCount = useStore(devtoolsStore, (s) =>
    s.entries.reduce((n, e) => (e.level === 'error' ? n + 1 : n), 0),
  )
  const isDebugMode = useDebugMode()
  const unlocked = isDevelopment || isDebugMode

  useHotkey(
    'meta+d',
    (e) => {
      e.preventDefault()
      if (unlocked) togglePanel()
    },
    { preventDefault: true },
  )

  // Hide the Next.js dev indicator while the panel is open — it overlaps.
  useEffect(() => {
    if (typeof document === 'undefined') return
    const apply = () => {
      document.querySelectorAll<HTMLElement>('nextjs-portal').forEach((el) => {
        el.style.display = isOpen ? 'none' : ''
      })
    }
    apply()
    const observer = new MutationObserver(apply)
    observer.observe(document.body, { childList: true })
    return () => observer.disconnect()
  }, [isOpen])

  // Easter egg: 5 clicks in 2s on the invisible trap opens the panel.
  const clicks = useRef<number[]>([])
  const handleTrapClick = useCallback(() => {
    const now = Date.now()
    clicks.current = [...clicks.current.filter((t) => now - t < 2000), now]
    if (clicks.current.length >= 5) {
      clicks.current = []
      devtoolsStore.getState().openPanel()
    }
  }, [])

  if (enabled === false && !isDebugMode) return null

  if (!unlocked) {
    return (
      <div
        className="fixed bottom-5 left-5 z-[99999] h-9 w-9 cursor-default opacity-0"
        onClick={handleTrapClick}
      />
    )
  }

  return (
    <>
      {!isOpen && (
        // Inline position, not Tailwind: this package's utility classes aren't
        // always in the consumer app's content scan. `left: 64px` in dev
        // clears the Next.js dev indicator.
        <div className="fixed z-[99999]" style={{ bottom: 20, left: isDevelopment ? 64 : 20 }}>
          <TooltipHint tooltip={{ content: 'Devtools', hotkey: 'mod+d', side: 'right' }}>
            <button
              type="button"
              className={cn(
                'relative flex h-9 w-9 items-center justify-center rounded-full',
                'bg-black/80 backdrop-blur-xl',
                'shadow-[0_0_0_1px_#171717,inset_0_0_0_1px_hsla(0,0%,100%,0.14),0px_16px_32px_-8px_rgba(0,0,0,0.24)]',
                'transition-all duration-150 hover:scale-105',
                'focus:outline-none focus-visible:ring-2 focus-visible:ring-white/50',
                // This button deliberately sits OUTSIDE the app's theme: it
                // mimics the Next.js dev indicator it sits beside (hence
                // `bg-black/80` and the hardcoded `#171717` ring above), and
                // must look the same in light and dark. `bg-destructive`
                // would follow the host's palette and stop matching its
                // neighbour.
                // eslint-disable-next-line no-restricted-syntax
                errorCount > 0 && 'bg-red-600/90',
                className,
              )}
              onClick={togglePanel}
            >
              <Bug className={cn('h-4 w-4', errorCount > 0 ? 'text-white' : 'text-white/80')} />
              {errorCount > 0 && (
                // Same reason as the button fill: this badge is part of the
                // off-theme dev-indicator styling, and its red must match the
                // fill above.
                <span
                  className={
                    // eslint-disable-next-line no-restricted-syntax
                    'absolute -right-1 -top-1 flex h-4 min-w-4 items-center justify-center rounded-full bg-white text-[10px] font-semibold text-red-600 shadow-sm'
                  }
                >
                  {errorCount}
                </span>
              )}
            </button>
          </TooltipHint>
        </div>
      )}
      <DevtoolsPanel {...panel} />
    </>
  )
}
