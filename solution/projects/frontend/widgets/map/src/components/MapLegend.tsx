'use client'

import { useState, useMemo, memo, type KeyboardEvent } from 'react'

import type { MapLegendProps, LegendItem } from '../types'

const positionStyles: Record<string, React.CSSProperties> = {
  'top-left': { top: 10, left: 10 },
  'top-right': { top: 10, right: 10 },
  'bottom-left': { bottom: 10, left: 10 },
  'bottom-right': { bottom: 10, right: 10 },
}

function LegendIcon({
  type,
  color,
}: {
  type: LegendItem['type']
  color?: string
}) {
  const fill = color || '#888'

  switch (type) {
    case 'circle':
      return (
        <svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true">
          <circle cx="8" cy="8" r="6" fill={fill} />
        </svg>
      )
    case 'line':
      return (
        <svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true">
          <line
            x1="0"
            y1="8"
            x2="16"
            y2="8"
            stroke={fill}
            strokeWidth="3"
            strokeLinecap="round"
          />
        </svg>
      )
    case 'fill':
      return (
        <svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true">
          <rect x="1" y="1" width="14" height="14" fill={fill} rx="2" />
        </svg>
      )
    case 'symbol':
    default:
      return (
        <svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true">
          <path
            d="M8 1l2.5 5 5.5.8-4 3.9.9 5.3L8 13.5l-4.9 2.5.9-5.3-4-3.9 5.5-.8z"
            fill={fill}
          />
        </svg>
      )
  }
}

function MapLegendComponent({
  items,
  position = 'bottom-right',
  title,
  collapsible = false,
  defaultCollapsed = false,
  className = '',
  style,
  onItemClick,
}: MapLegendProps) {
  const [collapsed, setCollapsed] = useState(defaultCollapsed)

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
      minWidth: collapsed ? 'auto' : 120,
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
      cursor: onItemClick ? 'pointer' : 'default',
    }),
    [onItemClick]
  )

  const handleHeaderClick = collapsible ? () => setCollapsed((c) => !c) : undefined

  return (
    <div className={className} style={containerStyle}>
      {(title || collapsible) && (
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
          {title && <span>{title}</span>}
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
      )}
      {!collapsed && (
        <ul style={{ listStyle: 'none', margin: 0, padding: 0 }}>
          {items.map((item) => (
            <li
              key={item.id}
              style={{
                ...itemStyle,
                opacity: item.visible === false ? 0.5 : 1,
              }}
              onClick={onItemClick ? () => onItemClick(item) : undefined}
              {...(onItemClick
                ? {
                    role: 'button' as const,
                    tabIndex: 0,
                    onKeyDown: (e: KeyboardEvent) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault()
                        onItemClick(item)
                      }
                    },
                  }
                : {})}
            >
              {item.icon || <LegendIcon type={item.type} color={item.color} />}
              <span>{item.label}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

export const MapLegend = memo(MapLegendComponent)
