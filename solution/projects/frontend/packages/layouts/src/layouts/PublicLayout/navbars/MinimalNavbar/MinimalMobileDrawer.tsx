'use client';

import React from 'react';

import { MobileDrawerShell, type MobileDrawerShellProps } from '../../shared';

type MinimalMobileDrawerProps = Omit<MobileDrawerShellProps, 'panelClassName' | 'outerClassName'> & {
  containerClassName?: string;
};

export function MinimalMobileDrawer({ containerClassName, ...rest }: MinimalMobileDrawerProps) {
  return (
    <MobileDrawerShell
      {...rest}
      outerClassName={containerClassName}
      panelClassName="rounded-none shadow-none border-0"
    />
  );
}
