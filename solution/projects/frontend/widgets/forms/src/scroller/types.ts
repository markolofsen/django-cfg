'use client';

import type * as React from 'react';

export type SnapAlign = 'start' | 'center' | 'end' | 'none';

export interface ScrollerContextValue {
  containerRef: React.RefObject<HTMLDivElement | null>;
  orientation: 'horizontal' | 'vertical';
  /** Parent default an item inherits when it declares no `snapAlign` of its own. */
  snapAlign: SnapAlign;
}

export interface ScrollerProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  /** Scroll direction */
  orientation?: 'horizontal' | 'vertical';
  /** Snap scroll to items */
  snap?: boolean;
  /** Snap alignment */
  snapAlign?: SnapAlign;
  /** Show scroll indicators (shadows/arrows) */
  showIndicators?: boolean;
  /** Hide scrollbar visually */
  hideScrollbar?: boolean;
}

export interface ScrollerItemProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  /** Snap alignment for this item (overrides parent) */
  snapAlign?: SnapAlign;
}

export interface ScrollerIndicatorProps {
  direction: 'prev' | 'next';
  onClick: () => void;
  disabled?: boolean;
  className?: string;
}
