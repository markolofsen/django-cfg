'use client'

import { useState, useCallback, useMemo, useEffect, memo, type KeyboardEvent } from 'react'
import { useMapLayers } from '../hooks/useMapLayers'

import type { LayerSwitcherProps, LayerConfig } from '../types'

const positionStyles: Record<string, React.CSSProperties> = {
  'top-left': { top: 10, left: 10 },
  'top-right': { top: 10, right: 10 },
  'bottom-left': { bottom: 10, left: 10 },
  'bottom-right': { bottom: 10, right: 10 },
}

function LayerSwitcherComponent({
  layers,
  position = 'top-right',
  title = 'Layers',
  collapsible = true,
  defaultCollapsed = false,
  showToggleAll = false,
  className = '',
  style,
  onChange,
}: LayerSwitcherProps) {
  const { setLayerVisibility } = useMapLayers()
  const [collapsed, setCollapsed] = useState(defaultCollapsed)

  const initialVisibility = useMemo(() => {
    const initial: Record<string, boolean> = {}
    layers.forEach((layer) => {
      initial[layer.id] = layer.defaultVisible !== false
    })
    return initial
  }, [layers])

  const [visibility, setVisibility] = useState<Record<string, boolean>>(initialVisibility)

  // Keep visibility in sync when the `layers` prop changes: add entries for
  // new layers, drop stale ones, preserve user toggles for existing layers.
  useEffect(() => {
    setVisibility((prev) => {
      const next: Record<string, boolean> = {}
      for (const layer of layers) {
        // `in` does not narrow the index read, so take the value and fall
        // back on it being absent — the two say the same thing.
        next[layer.id] = prev[layer.id] ?? layer.defaultVisible !== false
      }
      return next
    })
  }, [layers])

  const handleToggle = useCallback(
    (layerId: string) => {
      setVisibility((prev) => {
        const newVisible = !prev[layerId]
        setLayerVisibility(layerId, newVisible)
        onChange?.(layerId, newVisible)
        return { ...prev, [layerId]: newVisible }
      })
    },
    [setLayerVisibility, onChange]
  )

  const handleToggleAll = useCallback(
    (visible: boolean) => {
      const newVisibility: Record<string, boolean> = {}
      layers.forEach((layer) => {
        newVisibility[layer.id] = visible
        setLayerVisibility(layer.id, visible)
        onChange?.(layer.id, visible)
      })
      setVisibility(newVisibility)
    },
    [layers, setLayerVisibility, onChange]
  )

  const allVisible = useMemo(() => Object.values(visibility).every(Boolean), [visibility])
  const noneVisible = useMemo(() => Object.values(visibility).every((v) => !v), [visibility])

  const containerStyle = useMemo<React.CSSProperties>(
    () => ({
      position: 'absolute',
      ...positionStyles[position],
      backgroundColor: 'var(--color-popover)',
      color: 'var(--color-popover-foreground)',
      border: '1px solid var(--color-border)',
      borderRadius: 8,
      boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
      padding: collapsed ? 8 : 12,
      minWidth: collapsed ? 'auto' : 150,
      zIndex: 1,
      ...style,
    }),
    [position, collapsed, style]
  )

  const headerStyle = useMemo<React.CSSProperties>(
    () => ({
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      gap: 8,
      cursor: collapsible ? 'pointer' : 'default',
      fontWeight: 600,
      fontSize: 12,
      color: 'var(--color-foreground)',
      marginBottom: collapsed ? 0 : 8,
    }),
    [collapsible, collapsed]
  )

  const itemStyle = useMemo<React.CSSProperties>(
    () => ({
      display: 'flex',
      alignItems: 'center',
      gap: 8,
      padding: '4px 0',
      fontSize: 12,
      color: 'var(--color-muted-foreground)',
      cursor: 'pointer',
    }),
    []
  )

  const checkboxStyle = useMemo<React.CSSProperties>(
    () => ({
      width: 14,
      height: 14,
      cursor: 'pointer',
    }),
    []
  )

  const groups = useMemo(() => {
    return layers.reduce(
      (acc, layer) => {
        const group = layer.group || ''
        if (!acc[group]) acc[group] = []
        acc[group].push(layer)
        return acc
      },
      {} as Record<string, LayerConfig[]>
    )
  }, [layers])

  const handleHeaderClick = collapsible ? () => setCollapsed((c) => !c) : undefined

  return (
    <div className={className} style={containerStyle}>
      <div
        style={headerStyle}
        onClick={handleHeaderClick}
        {...(collapsible
          ? {
              role: 'button' as const,
              tabIndex: 0,
              'aria-expanded': !collapsed,
              onKeyDown: (e: KeyboardEvent) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault()
                  setCollapsed((c) => !c)
                }
              },
            }
          : {})}
      >
        <span>{title}</span>
        {collapsible && (
          <svg
            width="12"
            height="12"
            viewBox="0 0 12 12"
            aria-hidden="true"
            style={{
              transform: collapsed ? 'rotate(-90deg)' : 'rotate(0deg)',
              transition: 'transform 0.2s',
            }}
          >
            <path d="M3 4.5L6 7.5L9 4.5" stroke="currentColor" fill="none" />
          </svg>
        )}
      </div>
      {!collapsed && (
        <div>
          {showToggleAll && (
            <div
              style={{
                ...itemStyle,
                cursor: 'default',
                borderBottom: '1px solid var(--color-border)',
                marginBottom: 4,
                paddingBottom: 8,
              }}
            >
              <button
                type="button"
                onClick={() => handleToggleAll(true)}
                disabled={allVisible}
                style={{
                  fontSize: 10,
                  padding: '2px 6px',
                  cursor: allVisible ? 'default' : 'pointer',
                  opacity: allVisible ? 0.5 : 1,
                }}
              >
                All
              </button>
              <button
                type="button"
                onClick={() => handleToggleAll(false)}
                disabled={noneVisible}
                style={{
                  fontSize: 10,
                  padding: '2px 6px',
                  cursor: noneVisible ? 'default' : 'pointer',
                  opacity: noneVisible ? 0.5 : 1,
                }}
              >
                None
              </button>
            </div>
          )}
          {Object.entries(groups).map(([group, groupLayers]) => (
            <div key={group || 'default'}>
              {group && (
                <div
                  style={{
                    fontSize: 10,
                    fontWeight: 600,
                    color: 'var(--color-muted-foreground)',
                    marginTop: 8,
                    marginBottom: 4,
                    textTransform: 'uppercase',
                  }}
                >
                  {group}
                </div>
              )}
              {groupLayers.map((layer) => (
                <label key={layer.id} style={itemStyle}>
                  <input
                    type="checkbox"
                    checked={visibility[layer.id] ?? false}
                    onChange={() => handleToggle(layer.id)}
                    style={checkboxStyle}
                  />
                  <span>{layer.label}</span>
                </label>
              ))}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export const LayerSwitcher = memo(LayerSwitcherComponent)
