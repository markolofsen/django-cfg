'use client'

import { memo } from 'react'
import { cn } from '@djangocfg/ui-core/lib'

export interface ImageSpinnerProps {
  /** Size variant */
  size?: 'sm' | 'md' | 'lg'
  /** Additional class */
  className?: string
}

const SIZE_CLASSES = {
  sm: 'w-4 h-4 border-[1.5px]',
  md: 'w-6 h-6 border-2',
  lg: 'w-8 h-8 border-2',
} as const

/**
 * Minimal loading spinner for images
 * Adapts to dark/light theme via muted-foreground
 */
export const ImageSpinner = memo(function ImageSpinner({
  size = 'md',
  className,
}: ImageSpinnerProps) {
  return (
    <div
      className={cn(
        'rounded-full animate-spin',
        'border-muted-foreground/20 border-t-muted-foreground/60',
        SIZE_CLASSES[size],
        className
      )}
    />
  )
})
