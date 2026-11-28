"use client"
import * as React from 'react';
import * as ResizablePrimitive from 'react-resizable-panels';

import { DragHandleDots2Icon } from '@radix-ui/react-icons';

import { cn } from '../../../lib/utils';

// Context to share dragging state across panel group
const ResizableDraggingContext = React.createContext<{
  isDragging: boolean
  setIsDragging: (value: boolean) => void
}>({ isDragging: false, setIsDragging: () => {} })

// Hook to check if panel group is being resized
export const useResizableDragging = () => React.useContext(ResizableDraggingContext)

const ResizablePanelGroup = ({
  className,
  ...props
}: React.ComponentProps<typeof ResizablePrimitive.PanelGroup>) => {
  const [mounted, setMounted] = React.useState(false)
  const [isDragging, setIsDragging] = React.useState(false)

  React.useEffect(() => {
    setMounted(true)
  }, [])

  // SSR fallback - render static flex container
  if (!mounted) {
    return (
      <div
        className={cn(
          "flex h-full w-full data-[panel-group-direction=vertical]:flex-col",
          className
        )}
      >
        {props.children}
      </div>
    )
  }

  return (
    <ResizableDraggingContext.Provider value={{ isDragging, setIsDragging }}>
      <ResizablePrimitive.PanelGroup
        className={cn(
          "flex h-full w-full data-[panel-group-direction=vertical]:flex-col",
          className
        )}
        data-dragging={isDragging ? "true" : undefined}
        {...props}
      />
    </ResizableDraggingContext.Provider>
  )
}

const ResizablePanel = React.forwardRef<
  React.ElementRef<typeof ResizablePrimitive.Panel>,
  React.ComponentPropsWithoutRef<typeof ResizablePrimitive.Panel>
>(({ className, defaultSize, minSize, maxSize, children, ...props }, ref) => {
  const [mounted, setMounted] = React.useState(false)

  React.useEffect(() => {
    setMounted(true)
  }, [])

  // SSR fallback - render static div with default size
  if (!mounted) {
    // `data-*` attributes are not part of the typed prop surface, so the read
    // needs a cast. Narrowed to the one attribute rather than `any` on `props`:
    // this opens exactly the key it uses and leaves the rest checked.
    const direction = (props as { 'data-panel-group-direction'?: string })[
      'data-panel-group-direction'
    ]
    const sizeStyle = defaultSize
      ? direction === 'vertical'
        ? { height: `${defaultSize}%` }
        : { width: `${defaultSize}%` }
      : { flex: 1 }

    return (
      <div className={cn("overflow-hidden", className)} style={sizeStyle}>
        {children}
      </div>
    )
  }

  return (
    <ResizablePrimitive.Panel
      ref={ref}
      className={cn("overflow-hidden", className)}
      defaultSize={defaultSize}
      minSize={minSize}
      maxSize={maxSize}
      {...props}
    >
      {children}
    </ResizablePrimitive.Panel>
  )
})
ResizablePanel.displayName = "ResizablePanel"

export interface ResizableHandleProps extends React.ComponentProps<typeof ResizablePrimitive.PanelResizeHandle> {
  withHandle?: boolean;
  size?: 'sm' | 'md' | 'lg';
  showIndicator?: boolean;
  indicatorHeight?: number;
}

const ResizableHandle = ({
  withHandle,
  className,
  size = 'md',
  showIndicator = false,
  indicatorHeight = 32,
  onDragging,
  ...props
}: ResizableHandleProps) => {
  const [mounted, setMounted] = React.useState(false)
  const { setIsDragging } = React.useContext(ResizableDraggingContext)

  React.useEffect(() => {
    setMounted(true)
  }, [])

  // Handle drag state change - update context and call user callback
  const handleDragging = React.useCallback((isDragging: boolean) => {
    setIsDragging(isDragging)
    onDragging?.(isDragging)
  }, [setIsDragging, onDragging])

  // Size variants for hit area
  const sizeClasses = {
    sm: 'after:w-0.5',
    md: 'after:w-1',
    lg: 'after:w-1.5',
  }

  // SSR fallback - render static border
  if (!mounted) {
    return (
      <div
        className={cn(
          // Separator between panels → `bg-divider` (soft hairline), not the
          // opaque `bg-border` outline weight, so a resize seam stays quiet.
          "bg-divider w-px",
          "data-[panel-group-direction=vertical]:h-px data-[panel-group-direction=vertical]:w-full",
          className
        )}
      />
    )
  }

  return (
    <ResizablePrimitive.PanelResizeHandle
      className={cn(
        "relative flex items-center justify-center bg-divider",
        "w-px h-full",
        "hover:bg-primary/60 active:bg-primary",
        "transition-colors",
        // Touch handling for better drag performance
        "touch-none select-none",
        // Invisible hit area for easier dragging
        "after:absolute after:inset-y-0 after:left-1/2 after:-translate-x-1/2",
        sizeClasses[size],
        "data-[panel-group-direction=vertical]:w-full data-[panel-group-direction=vertical]:h-px",
        "data-[panel-group-direction=vertical]:after:left-0 data-[panel-group-direction=vertical]:after:inset-x-0",
        "data-[panel-group-direction=vertical]:after:top-1/2 data-[panel-group-direction=vertical]:after:-translate-y-1/2",
        "data-[panel-group-direction=vertical]:after:h-0.5 data-[panel-group-direction=vertical]:after:w-full",
        "data-[panel-group-direction=vertical]:after:translate-x-0",
        "focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring",
        className
      )}
      style={{ touchAction: 'none' }}
      onDragging={handleDragging}
      {...props}
    >
      {/* Optional pill indicator */}
      {showIndicator && (
        <div
          className={cn(
            "absolute z-10 rounded-full bg-border opacity-0 hover:opacity-100 transition-opacity",
            "w-1 data-[panel-group-direction=vertical]:w-auto data-[panel-group-direction=vertical]:h-1"
          )}
          style={{
            height: `${indicatorHeight}px`,
            width: '4px',
          }}
        />
      )}

      {/* Optional dots handle */}
      {withHandle && (
        <div className="z-10 flex h-4 w-3 items-center justify-center rounded-sm border bg-border">
          <DragHandleDots2Icon className="h-2.5 w-2.5" />
        </div>
      )}
    </ResizablePrimitive.PanelResizeHandle>
  )
}

export { ResizablePanelGroup, ResizablePanel, ResizableHandle }

// Re-export types from react-resizable-panels for imperative panel control
export type { ImperativePanelHandle } from 'react-resizable-panels'
