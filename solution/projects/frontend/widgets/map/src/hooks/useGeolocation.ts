'use client'

import { useCallback, useEffect, useRef, useState } from 'react'

/**
 * Live user position from the browser Geolocation API — independent of the
 * map (no `useMapContext`). Use it for custom "where am I" UI or logic; for
 * the on-map dot + accuracy circle + follow-mode, prefer `MapContainer`'s
 * `geolocate` chip (which wraps maplibre's `GeolocateControl`).
 *
 * Privacy: nothing happens until you call `request()` or `watch()` — those
 * trigger the OS permission prompt. Never auto-started.
 *
 * Secure context: `navigator.geolocation` requires HTTPS or localhost (it
 * works in the cmdop Wails webview). Off a secure context the status is
 * `'unavailable'` and the request methods no-op.
 */

/** A single position fix, flattened from `GeolocationCoordinates`. */
export interface GeolocationFix {
  lat: number
  lng: number
  /** Accuracy radius in meters (1σ). */
  accuracy: number
  /** Compass heading in degrees (0 = north), or null when unknown/stationary. */
  heading: number | null
  /** Ground speed in m/s, or null when unknown. */
  speed: number | null
  /** Fix timestamp (ms epoch). */
  timestamp: number
}

export type GeolocationStatus =
  | 'idle' // nothing requested yet
  | 'locating' // a request/watch is in flight, no fix yet
  | 'granted' // have a fix
  | 'denied' // user blocked the permission (PERMISSION_DENIED)
  | 'unavailable' // no secure context / no geolocation API / POSITION_UNAVAILABLE
  | 'timeout' // the request timed out

export interface UseGeolocationOptions {
  /** Higher precision (GPS) at a battery cost. @default false */
  highAccuracy?: boolean
  /** Accept a cached fix up to this age (ms). @default 0 (always fresh) */
  maximumAge?: number
  /** Give up after this long (ms). @default 10000 */
  timeout?: number
}

export interface UseGeolocationResult {
  /** Latest fix, or null until one arrives. */
  position: GeolocationFix | null
  status: GeolocationStatus
  /** The raw error from the last failure, if any. */
  error: GeolocationPositionError | null
  /** True only on HTTPS/localhost with a geolocation API present. */
  supported: boolean
  /** One-shot: request a single fix (prompts permission on first use). */
  request: () => void
  /** Continuous: start watching the position until `stop()`. */
  watch: () => void
  /** Stop an active watch and return to idle (keeps the last fix). */
  stop: () => void
}

function toFix(p: GeolocationPosition): GeolocationFix {
  const c = p.coords
  return {
    lat: c.latitude,
    lng: c.longitude,
    accuracy: c.accuracy,
    heading: c.heading != null && !Number.isNaN(c.heading) ? c.heading : null,
    speed: c.speed != null && !Number.isNaN(c.speed) ? c.speed : null,
    timestamp: p.timestamp,
  }
}

function statusForError(err: GeolocationPositionError): GeolocationStatus {
  switch (err.code) {
    case err.PERMISSION_DENIED:
      return 'denied'
    case err.TIMEOUT:
      return 'timeout'
    default:
      return 'unavailable' // POSITION_UNAVAILABLE
  }
}

export function useGeolocation(
  options: UseGeolocationOptions = {},
): UseGeolocationResult {
  const { highAccuracy = false, maximumAge = 0, timeout = 10_000 } = options

  // Secure-context + API presence. `isSecureContext` is true on
  // localhost/HTTPS (and in the Wails webview); false on plain http.
  const supported =
    typeof navigator !== 'undefined' &&
    'geolocation' in navigator &&
    (typeof window === 'undefined' || window.isSecureContext)

  const [position, setPosition] = useState<GeolocationFix | null>(null)
  const [status, setStatus] = useState<GeolocationStatus>('idle')
  const [error, setError] = useState<GeolocationPositionError | null>(null)

  const watchIdRef = useRef<number | null>(null)
  // Keep the latest options in a ref so request/watch identities stay stable.
  const posOptsRef = useRef<PositionOptions>({})
  posOptsRef.current = {
    enableHighAccuracy: highAccuracy,
    maximumAge,
    timeout,
  }

  const onSuccess = useCallback((p: GeolocationPosition) => {
    setPosition(toFix(p))
    setError(null)
    setStatus('granted')
  }, [])

  const onError = useCallback((err: GeolocationPositionError) => {
    setError(err)
    setStatus(statusForError(err))
  }, [])

  const stop = useCallback(() => {
    if (watchIdRef.current != null) {
      navigator.geolocation.clearWatch(watchIdRef.current)
      watchIdRef.current = null
    }
    setStatus((s) => (s === 'locating' || s === 'granted' ? 'idle' : s))
  }, [])

  const request = useCallback(() => {
    if (!supported) {
      setStatus('unavailable')
      return
    }
    setStatus('locating')
    navigator.geolocation.getCurrentPosition(
      onSuccess,
      onError,
      posOptsRef.current,
    )
  }, [supported, onSuccess, onError])

  const watch = useCallback(() => {
    if (!supported) {
      setStatus('unavailable')
      return
    }
    // Replace any existing watch.
    if (watchIdRef.current != null) {
      navigator.geolocation.clearWatch(watchIdRef.current)
    }
    setStatus('locating')
    watchIdRef.current = navigator.geolocation.watchPosition(
      onSuccess,
      onError,
      posOptsRef.current,
    )
  }, [supported, onSuccess, onError])

  // Clear any active watch on unmount.
  useEffect(() => {
    return () => {
      if (watchIdRef.current != null) {
        navigator.geolocation.clearWatch(watchIdRef.current)
        watchIdRef.current = null
      }
    }
  }, [])

  return { position, status, error, supported, request, watch, stop }
}
