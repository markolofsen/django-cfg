'use client'

import { useState, memo } from 'react'
import { createPortal } from 'react-dom'
import { useControl } from 'react-map-gl/maplibre'

import type { IControl, MapInstance } from 'react-map-gl/maplibre'
import type { CustomOverlayProps } from '../types'

class OverlayControl implements IControl {
  _map: MapInstance | null = null
  _container: HTMLElement | null = null
  _redraw: () => void

  constructor(redraw: () => void) {
    this._redraw = redraw
  }

  onAdd(map: MapInstance): HTMLElement {
    this._map = map
    map.on('move', this._redraw)
    this._container = document.createElement('div')
    this._redraw()
    return this._container
  }

  onRemove(): void {
    this._container?.remove()
    this._map?.off('move', this._redraw)
    this._map = null
  }

  getElement(): HTMLElement | null {
    return this._container
  }
}

function CustomOverlayComponent({ children }: CustomOverlayProps) {
  const [, setVersion] = useState(0)

  const ctrl = useControl<OverlayControl>(() => {
    const forceUpdate = () => setVersion((v) => v + 1)
    return new OverlayControl(forceUpdate)
  })

  const element = ctrl.getElement()

  if (!element) return null

  // Children can use useMapContext() to access the map if needed
  return createPortal(children, element)
}

export const CustomOverlay = memo(CustomOverlayComponent)
