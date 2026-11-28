'use client'

/**
 * useDebugMode — debug mode detection.
 *
 * - development: always true
 * - production: `?debug=1` persists to localStorage (param removed from URL),
 *   `?debug=0` clears it; otherwise the stored flag decides.
 */

import { useEffect, useState } from 'react'

import { isDevelopment } from './internal'
import { CFG_KEYS } from '@djangocfg/api/storage'

const LS_KEY = CFG_KEYS.monitorDebug.key

function readStored(): boolean {
  try {
    return localStorage.getItem(LS_KEY) === '1'
  } catch {
    return false
  }
}

function consumeDebugParam(): boolean | null {
  if (typeof window === 'undefined') return null
  const params = new URLSearchParams(window.location.search)
  const value = params.get('debug')
  if (value === null) return null

  try {
    if (value === '1') localStorage.setItem(LS_KEY, '1')
    else localStorage.removeItem(LS_KEY)
  } catch {
    /* private browsing */
  }

  params.delete('debug')
  const qs = params.toString()
  window.history.replaceState(
    null,
    '',
    `${window.location.pathname}${qs ? `?${qs}` : ''}${window.location.hash}`,
  )
  return value === '1'
}

export function useDebugMode(): boolean {
  const [isDebug, setIsDebug] = useState(isDevelopment)

  useEffect(() => {
    if (isDevelopment) return
    const fromUrl = consumeDebugParam()
    setIsDebug(fromUrl ?? readStored())
  }, [])

  return isDebug
}
