'use client';

import React from 'react';

import { MobileDrawerShell, type MobileDrawerShellProps } from '../../shared';

type FlushMobileDrawerProps = Omit<MobileDrawerShellProps, 'panelClassName' | 'outerClassName'> & {
  containerClassName?: string;
};

export function FlushMobileDrawer({ containerClassName, ...rest }: FlushMobileDrawerProps) {
  return (
    <MobileDrawerShell
      {...rest}
      outerClassName={containerClassName}
      panelClassName="border border-border/40 dark:border-border/70 rounded-xl"
    />
  );
}
