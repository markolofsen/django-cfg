'use client';

import * as React from 'react';
import { useIsMobile } from '@djangocfg/ui-core/hooks';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  Drawer,
  DrawerContent,
  DrawerDescription,
  DrawerFooter,
  DrawerHeader,
  DrawerTitle,
} from '@djangocfg/ui-core/components';
import { ResponsiveDialogProvider, useResponsiveDialogContext } from '../context';
import type {
  ResponsiveDialogProps,
  ResponsiveDialogContentProps,
  ResponsiveDialogHeaderProps,
  ResponsiveDialogTitleProps,
  ResponsiveDialogDescriptionProps,
  ResponsiveDialogFooterProps,
} from '../types';

export function ResponsiveDialog({ open, onOpenChange, children }: ResponsiveDialogProps) {
  const isMobile = useIsMobile();

  const Root = isMobile ? Drawer : Dialog;

  return (
    <ResponsiveDialogProvider value={{ isMobile }}>
      <Root open={open} onOpenChange={onOpenChange}>
        {children}
      </Root>
    </ResponsiveDialogProvider>
  );
}
ResponsiveDialog.displayName = 'ResponsiveDialog';

export function ResponsiveDialogContent({ children, className }: ResponsiveDialogContentProps) {
  const { isMobile } = useResponsiveDialogContext();
  if (isMobile) {
    return <DrawerContent className={className} height="auto">{children}</DrawerContent>;
  }
  return <DialogContent className={className}>{children}</DialogContent>;
}
ResponsiveDialogContent.displayName = 'ResponsiveDialogContent';

export function ResponsiveDialogHeader({ className, ...props }: ResponsiveDialogHeaderProps) {
  const { isMobile } = useResponsiveDialogContext();
  if (isMobile) {
    return <DrawerHeader className={className} {...props} />;
  }
  return <DialogHeader className={className} {...props} />;
}
ResponsiveDialogHeader.displayName = 'ResponsiveDialogHeader';

export function ResponsiveDialogTitle({ className, ...props }: ResponsiveDialogTitleProps) {
  const { isMobile } = useResponsiveDialogContext();
  if (isMobile) {
    return <DrawerTitle className={className} {...props} />;
  }
  return <DialogTitle className={className} {...props} />;
}
ResponsiveDialogTitle.displayName = 'ResponsiveDialogTitle';

export function ResponsiveDialogDescription({ className, ...props }: ResponsiveDialogDescriptionProps) {
  const { isMobile } = useResponsiveDialogContext();
  if (isMobile) {
    return <DrawerDescription className={className} {...props} />;
  }
  return <DialogDescription className={className} {...props} />;
}
ResponsiveDialogDescription.displayName = 'ResponsiveDialogDescription';

export function ResponsiveDialogFooter({ className, ...props }: ResponsiveDialogFooterProps) {
  const { isMobile } = useResponsiveDialogContext();
  if (isMobile) {
    return <DrawerFooter className={className} {...props} />;
  }
  return <DialogFooter className={className} {...props} />;
}
ResponsiveDialogFooter.displayName = 'ResponsiveDialogFooter';
