'use client'

/**
 * useGeocoder — debounced, abortable autocomplete state for an injectable
 * geocoding `resolve` function (default = public Photon).
 *
 * No UI, no map dependency. Debounces the query (~300ms), gates on a minimum
 * length, and fires ONE `AbortController` per keystroke — the previous
 * in-flight request is aborted before the next starts. Aborted requests are
 * swallowed; real failures surface via `error`.
 */

import { useCallback, useEffect, useRef, useState } from 'react'

import { photonResolve, type GeocodeResult, type ResolveGeocode } from '../geocode'

export interface UseGeocoderOptions {
  /** Injectable resolver. Defaults to public Photon (`photonResolve`). */
  resolve?: ResolveGeocode
  /** Geo-bias — results near this point rank higher (e.g. map center). */
  near?: { lng: number; lat: number }
  /** Max results per query. Default 5. */
  limit?: number
  /** Minimum query length before a request fires. Default 3. */
  minLength?: number
  /** Debounce delay in ms. Default 300. */
  debounceMs?: number
}

export interface UseGeocoderResult {
  /** Current (raw, un-debounced) query text. */
  query: string
  /** Update the query — debounced search runs after `debounceMs`. */
  setQuery: (next: string) => void
  /** Latest results for the debounced query. */
  results: GeocodeResult[]
  /** A request is in flight. */
  loading: boolean
  /** Last non-abort error, or `null`. */
  error: Error | null
  /** Reset query, results, error and abort any in-flight request. */
  clear: () => void
  /**
   * Convenience for consumers — clears the input and returns the picked
   * result so it can be wired to e.g. `flyTo`. Purely state-level; it does
   * not touch the map.
   */
  select: (result: GeocodeResult) => GeocodeResult
}

function isAbortError(err: unknown): boolean {
  return (
    err instanceof DOMException
      ? err.name === 'AbortError'
      : err instanceof Error && err.name === 'AbortError'
  )
}

export function useGeocoder(options: UseGeocoderOptions = {}): UseGeocoderResult {
  const {
    resolve = photonResolve,
    near,
    limit,
    minLength = 3,
    debounceMs = 300,
  } = options

  const [query, setQueryState] = useState('')
  const [results, setResults] = useState<GeocodeResult[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  // Keep latest resolver / bias without re-triggering the debounce effect on
  // identity churn (mirrors the link-preview resolverRef pattern).
  const resolveRef = useRef(resolve)
  resolveRef.current = resolve
  const nearRef = useRef(near)
  nearRef.current = near
  const limitRef = useRef(limit)
  limitRef.current = limit

  // One controller for the in-flight request, aborted on each new keystroke.
  const controllerRef = useRef<AbortController | null>(null)

  const setQuery = useCallback((next: string) => {
    setQueryState(next)
  }, [])

  const clear = useCallback(() => {
    controllerRef.current?.abort()
    controllerRef.current = null
    setQueryState('')
    setResults([])
    setError(null)
    setLoading(false)
  }, [])

  const select = useCallback((result: GeocodeResult) => {
    controllerRef.current?.abort()
    controllerRef.current = null
    setQueryState('')
    setResults([])
    setError(null)
    setLoading(false)
    return result
  }, [])

  useEffect(() => {
    const q = query.trim()

    // Below the min-length gate: drop stale results, cancel in-flight.
    if (q.length < minLength) {
      controllerRef.current?.abort()
      controllerRef.current = null
      setResults([])
      setLoading(false)
      setError(null)
      return
    }

    const timer = setTimeout(() => {
      controllerRef.current?.abort()
      const controller = new AbortController()
      controllerRef.current = controller

      setLoading(true)
      setError(null)

      resolveRef
        .current(q, {
          near: nearRef.current,
          limit: limitRef.current,
          signal: controller.signal,
        })
        .then((next) => {
          if (controller.signal.aborted) return
          setResults(next)
          setLoading(false)
        })
        .catch((err: unknown) => {
          if (controller.signal.aborted || isAbortError(err)) return
          setResults([])
          setError(err instanceof Error ? err : new Error(String(err)))
          setLoading(false)
        })
    }, debounceMs)

    return () => clearTimeout(timer)
  }, [query, minLength, debounceMs])

  // Abort any in-flight request on unmount.
  useEffect(() => () => controllerRef.current?.abort(), [])

  return { query, setQuery, results, loading, error, clear, select }
}
