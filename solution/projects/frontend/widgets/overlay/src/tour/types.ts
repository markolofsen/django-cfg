'use client';

import type * as React from 'react';

export interface TourStep {
  id: string;
  target: string;
  title: string;
  description?: string;
  placement?: 'top' | 'bottom' | 'left' | 'right';
}

export interface TourContextValue {
  isOpen: boolean;
  currentStep: number;
  steps: TourStep[];
  totalSteps: number;
  goToStep: (index: number) => void;
  nextStep: () => void;
  prevStep: () => void;
  close: () => void;
  open: () => void;
}

export interface TourProps {
  children: React.ReactNode;
  steps: TourStep[];
  /** Called when tour completes */
  onComplete?: () => void;
  /** Called when tour is dismissed */
  onDismiss?: () => void;
  /** Start open */
  defaultOpen?: boolean;
}

export interface TourPopoverProps {
  className?: string;
}

export interface TourNavigationProps {
  className?: string;
}
