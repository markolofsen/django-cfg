'use client';

import type * as React from 'react';

export interface ResponsiveDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  children: React.ReactNode;
}

export interface ResponsiveDialogContentProps {
  children: React.ReactNode;
  className?: string;
}

export type ResponsiveDialogHeaderProps = React.HTMLAttributes<HTMLDivElement>;

export type ResponsiveDialogTitleProps = React.HTMLAttributes<HTMLHeadingElement>;

export type ResponsiveDialogDescriptionProps = React.HTMLAttributes<HTMLParagraphElement>;

export type ResponsiveDialogFooterProps = React.HTMLAttributes<HTMLDivElement>;

export interface ResponsiveDialogContextValue {
  isMobile: boolean;
}
