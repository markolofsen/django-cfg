'use client';

import React from 'react';

import { cn } from '@djangocfg/ui-core/lib';

import { publicFloatingChromeClassName } from '../../publicShellShadow';
import { MobileDrawerShell, type MobileDrawerShellProps } from '../../shared';

type FloatingMobileDrawerProps = Omit<MobileDrawerShellProps, 'panelClassName' | 'outerClassName'> & {
  /** Tailwind rounding for the drawer panel. @default 'rounded-2xl' */
  rounding?: string;
  /** Outer wrapper className (e.g. `mx-auto max-w-7xl`). */
  containerClassName?: string;
};

export function FloatingMobileDrawer({
  rounding,
  containerClassName,
  ...rest
}: FloatingMobileDrawerProps) {
  return (
    <MobileDrawerShell
      {...rest}
      panelClassName={cn(publicFloatingChromeClassName, rounding ?? 'rounded-2xl')}
      outerClassName={containerClassName}
    />
  );
}
