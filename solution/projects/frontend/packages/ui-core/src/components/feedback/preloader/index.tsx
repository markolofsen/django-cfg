/**
 * Preloader Component
 *
 * Universal loading indicator component with multiple variants
 * Supports inline, fullscreen, and custom layouts
 */

'use client';

import { Loader2 } from 'lucide-react';
import React from 'react';

import { useAppT } from '@djangocfg/i18n';
import { cn } from '../../../lib/utils';
// Spinner is available for future use
// import { Spinner } from './spinner';

export interface PreloaderProps {
  /**
   * Loading text to display
   * @default undefined (no text)
   */
  text?: string;

  /**
   * Additional description/subtitle text
   */
  description?: string;

  /**
   * Size variant
   * @default 'md'
   */
  size?: 'sm' | 'md' | 'lg' | 'xl';

  /**
   * Variant: inline (fits container) or fullscreen (fixed overlay)
   * @default 'inline'
   */
  variant?: 'inline' | 'fullscreen';

  /**
   * Show backdrop (only for fullscreen variant)
   * @default true
   */
  backdrop?: boolean;

  /**
   * Backdrop opacity (0-100, only for fullscreen with backdrop)
   * @default 80
   */
  backdropOpacity?: number;

  /**
   * Additional CSS classes
   */
  className?: string;

  /**
   * Spinner className override
   */
  spinnerClassName?: string;
}

const sizeMap = {
  sm: 'h-4 w-4',
  md: 'h-6 w-6',
  lg: 'h-8 w-8',
  xl: 'h-12 w-12',
};

/**
 * Preloader - Universal loading indicator
 *
 * Features:
 * - Multiple size variants (sm, md, lg, xl)
 * - Inline or fullscreen variants
 * - Optional text and description
 * - Optional backdrop for fullscreen
 * - Accessible (ARIA labels)
 *
 * @example
 * ```tsx
 * // Inline loading
 * <Preloader text="Loading..." />
 *
 * // Fullscreen with backdrop
 * <Preloader variant="fullscreen" text="Loading data..." />
 *
 * // Custom size
 * <Preloader size="lg" text="Processing..." />
 *
 * // Without text
 * <Preloader />
 * ```
 */
export function Preloader({
  text,
  description,
  size = 'md',
  variant = 'inline',
  backdrop = true,
  backdropOpacity = 80,
  className,
  spinnerClassName,
}: PreloaderProps) {
  const t = useAppT()
  const loadingLabel = text || t('ui.states.loading')
  const spinnerSize = sizeMap[size];

  // Fullscreen variant
  if (variant === 'fullscreen') {
    const backdropClasses = backdrop
      ? backdropOpacity >= 90
        ? 'bg-background/95'
        : backdropOpacity >= 70
          ? 'bg-background/90'
          : backdropOpacity >= 50
            ? 'bg-background/80'
            : 'bg-background/60'
      : 'bg-transparent';

    return (
      <div
        className={cn(
          'fixed inset-0 z-50 flex items-center justify-center',
          backdropClasses,
          className
        )}
        role="status"
        aria-label={loadingLabel}
        aria-live="polite"
      >
        <div className="flex flex-col items-center gap-4 animate-in fade-in duration-300">
          {/* Spinner */}
          <Loader2
            className={cn('animate-spin text-primary', spinnerSize, spinnerClassName)}
            aria-hidden="true"
          />

          {/* Text content */}
          {(text || description) && (
            <div className="flex flex-col items-center gap-2 text-center">
              {text && (
                <p className="text-base font-medium text-foreground">{text}</p>
              )}
              {description && (
                <p className="text-sm text-muted-foreground">{description}</p>
              )}
              {/* Animated dots */}
              {text && (
                <div className="flex gap-1 mt-1">
                  <span
                    className="h-1.5 w-1.5 animate-bounce rounded-full bg-primary"
                    style={{ animationDelay: '0ms' }}
                  />
                  <span
                    className="h-1.5 w-1.5 animate-bounce rounded-full bg-primary"
                    style={{ animationDelay: '150ms' }}
                  />
                  <span
                    className="h-1.5 w-1.5 animate-bounce rounded-full bg-primary"
                    style={{ animationDelay: '300ms' }}
                  />
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    );
  }

  // Inline variant
  return (
    <div
      className={cn(
        'flex items-center justify-center',
        text || description ? 'gap-3' : '',
        className
      )}
      role="status"
      aria-label={loadingLabel}
      aria-live="polite"
    >
      <Loader2
        className={cn('animate-spin text-primary', spinnerSize, spinnerClassName)}
        aria-hidden="true"
      />
      {(text || description) && (
        <div className="flex flex-col gap-1">
          {text && (
            <p className="text-sm font-medium text-foreground">{text}</p>
          )}
          {description && (
            <p className="text-xs text-muted-foreground">{description}</p>
          )}
        </div>
      )}
    </div>
  );
}

/**
 * PreloaderSkeleton - Loading skeleton variant
 * Useful for content placeholders
 */
export interface PreloaderSkeletonProps {
  /**
   * Number of skeleton lines
   * @default 3
   */
  lines?: number;

  /**
   * Show avatar skeleton
   * @default false
   */
  showAvatar?: boolean;

  /**
   * Additional CSS classes
   */
  className?: string;
}

export function PreloaderSkeleton({
  lines = 3,
  showAvatar = false,
  className,
}: PreloaderSkeletonProps) {
  return (
    <div className={cn('space-y-3', className)}>
      {showAvatar && (
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-full bg-muted animate-pulse" />
          <div className="space-y-2 flex-1">
            <div className="h-4 w-24 rounded bg-muted animate-pulse" />
            <div className="h-3 w-32 rounded bg-muted animate-pulse" />
          </div>
        </div>
      )}
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className={cn(
            'h-4 rounded bg-muted animate-pulse',
            i === lines - 1 ? 'w-3/4' : 'w-full'
          )}
        />
      ))}
    </div>
  );
}

