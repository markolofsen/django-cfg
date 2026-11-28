import * as React from 'react';

export type Side = 'left' | 'right' | 'top' | 'bottom';
export type Orientation = 'horizontal' | 'vertical';
export type Direction = 'ltr' | 'rtl';

export interface MarqueeProps extends React.ComponentProps<'div'> {
  side?: Side;
  dir?: Direction;
  speed?: number;
  delay?: number;
  loopCount?: number;
  gap?: string | number;
  autoFill?: boolean;
  pauseOnHover?: boolean;
  pauseOnKeyboard?: boolean;
  reverse?: boolean;
  asChild?: boolean;
}

export interface MarqueeContextValue {
  side: Side;
  orientation: Orientation;
  dir: Direction;
  speed: number;
  loopCount: number;
  contentRef: React.RefObject<HTMLDivElement | null>;
  rootRef: React.RefObject<HTMLDivElement | null>;
  autoFill: boolean;
  pauseOnHover: boolean;
  pauseOnKeyboard: boolean;
  reverse: boolean;
  paused: boolean;
}

export interface MarqueeEdgeProps extends React.ComponentProps<'div'> {
  side: Side;
  size?: 'default' | 'sm' | 'lg';
  asChild?: boolean;
}
