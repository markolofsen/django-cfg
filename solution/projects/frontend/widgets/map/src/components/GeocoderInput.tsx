'use client'

/**
 * GeocoderInput — a self-contained, map-agnostic address/place autocomplete.
 *
 * A text field + a results dropdown (primary `label` + muted `secondary`),
 * with loading / empty states and keyboard nav (↑/↓ move, Enter select, Esc
 * close). Resolution is INJECTABLE: pass a `resolve` (default = public
 * Photon) — the component never hard-couples to a backend.
 *
 * Built on ui-core's `Command` primitives (cmdk). cmdk's built-in fuzzy
 * filter is DISABLED (`shouldFilter={false}`) because results already come
 * pre-ranked from the resolver — we drive selection state manually so it
 * works as a live remote-search box.
 *
 * Usable WITHOUT a map (plain forms). `GeocoderControl` is the thin map-bound
 * wrapper that flies the camera on select.
 */

import { useCallback, useEffect, useRef, useState } from 'react'

import { cn } from '@djangocfg/ui-core/lib'
import {
  Command,
  CommandEmpty,
  CommandInput,
  CommandItem,
  CommandList,
} from '@djangocfg/ui-core/components'

import { useGeocoder } from '../hooks/useGeocoder'
import type { GeocodeResult, ResolveGeocode } from '../geocode'

export interface GeocoderInputProps {
  /** Injectable resolver. Defaults to public Photon (`photonResolve`). */
  resolve?: ResolveGeocode
  /** Called with the chosen result when the user picks one. */
  onSelect?: (result: GeocodeResult) => void
  /** Input placeholder. */
  placeholder?: string
  /** Geo-bias — rank results near this point (e.g. the map center). */
  near?: { lng: number; lat: number }
  /** Minimum query length before searching. Default 3. */
  minLength?: number
  /** Max results. Default 5. */
  limit?: number
  /**
   * Focus the text field on mount (e.g. when revealed by a toolbar toggle).
   * @default false
   */
  autoFocus?: boolean
  className?: string
}

export function GeocoderInput({
  resolve,
  onSelect,
  placeholder = 'Search address or place…',
  near,
  minLength = 3,
  limit,
  autoFocus = false,
  className,
}: GeocoderInputProps) {
  const { query, setQuery, results, loading, error, select } = useGeocoder({
    resolve,
    near,
    minLength,
    limit,
  })

  // Show the dropdown only while focused with a meaningful query.
  const [open, setOpen] = useState(false)

  // Optional autofocus when revealed (e.g. by the toolbar search chip).
  // cmdk's `CommandInput` doesn't forward a ref reliably across versions, so
  // query the rendered `[cmdk-input]` element from the Command root instead.
  const rootRef = useRef<HTMLDivElement>(null)
  useEffect(() => {
    if (!autoFocus) return
    const input = rootRef.current?.querySelector<HTMLInputElement>('[cmdk-input]')
    input?.focus()
  }, [autoFocus])

  const handleSelect = useCallback(
    (result: GeocodeResult) => {
      onSelect?.(select(result))
      setOpen(false)
    },
    [onSelect, select],
  )

  const showList = open && query.trim().length >= minLength

  return (
    // The Command wrapper is a TRANSPARENT positioning context only — the
    // popover chrome (bg/border/shadow) lives on the input and on the
    // floating list separately, so nothing peeks out beneath the input when
    // the list is closed.
    <Command
      ref={rootRef}
      shouldFilter={false}
      // Esc closes the dropdown without clearing; cmdk handles ↑/↓/Enter.
      onKeyDown={(e) => {
        if (e.key === 'Escape') {
          e.preventDefault()
          setOpen(false)
        }
      }}
      className={cn(
        'relative overflow-visible bg-transparent',
        // Turn cmdk's input WRAPPER into the search field itself: a rounded
        // popover surface with its own border (drop cmdk's default bottom
        // border so no line/stub shows beneath the input when closed).
        '[&_[cmdk-input-wrapper]]:h-10 [&_[cmdk-input-wrapper]]:rounded-lg',
        '[&_[cmdk-input-wrapper]]:border [&_[cmdk-input-wrapper]]:border-border',
        '[&_[cmdk-input-wrapper]]:bg-popover [&_[cmdk-input-wrapper]]:text-popover-foreground',
        '[&_[cmdk-input-wrapper]]:shadow-sm',
        className,
      )}
    >
      <CommandInput
        value={query}
        onValueChange={(v) => {
          setQuery(v)
          setOpen(true)
        }}
        onFocus={() => setOpen(true)}
        onBlur={() => {
          // Delay so an item click registers before the list unmounts.
          window.setTimeout(() => setOpen(false), 120)
        }}
        placeholder={placeholder}
        aria-label={placeholder}
      />

      {showList ? (
        // Floating result panel — its OWN popover surface, anchored under the
        // input, shown only when there's a query (never an empty stub).
        <CommandList className="absolute inset-x-0 top-full z-10 mt-1.5 max-h-72 overflow-y-auto rounded-lg border border-border bg-popover text-popover-foreground shadow-md">
          {loading ? (
            <div
              className="px-3 py-6 text-center text-sm text-muted-foreground"
              aria-busy="true"
            >
              Searching…
            </div>
          ) : error ? (
            <div className="px-3 py-6 text-center text-sm text-destructive">
              Search failed. Try again.
            </div>
          ) : (
            <>
              <CommandEmpty className="py-6 text-center text-sm text-muted-foreground">
                No results.
              </CommandEmpty>
              {results.map((result) => (
                <CommandItem
                  key={result.id}
                  // cmdk matches `value`; keep it unique + searchable-ish.
                  value={`${result.id} ${result.label}`}
                  onSelect={() => handleSelect(result)}
                  className="flex-col items-start gap-0.5"
                >
                  <span className="truncate font-medium text-foreground">
                    {result.label}
                  </span>
                  {result.secondary ? (
                    <span className="truncate text-xs text-muted-foreground">
                      {result.secondary}
                    </span>
                  ) : null}
                </CommandItem>
              ))}
            </>
          )}
        </CommandList>
      ) : null}
    </Command>
  )
}
