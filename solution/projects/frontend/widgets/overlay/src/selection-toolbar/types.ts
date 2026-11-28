'use client';

import type * as React from 'react';

export interface SelectionToolbarContextValue {
  isVisible: boolean;
  selectedText: string;
  selectionRect: DOMRect | null;
  hide: () => void;
}

export interface SelectionToolbarProps {
  children: React.ReactNode;
  /** Minimum characters to show toolbar */
  minSelectionLength?: number;
  /** Called when selection changes */
  onSelectionChange?: (text: string) => void;
}

export interface SelectionToolbarContentProps {
  children: React.ReactNode;
  className?: string;
  /** Offset from selection (px) */
  offset?: number;
}

export interface SelectionToolbarActionProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  /** Icon or label */
  label?: string;
}
