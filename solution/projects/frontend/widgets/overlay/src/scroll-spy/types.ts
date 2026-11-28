'use client';

import type * as React from 'react';

export interface ScrollSpySection {
  id: string;
  label: string;
}

export interface ScrollSpyContextValue {
  activeId: string | null;
  sections: ScrollSpySection[];
  /** Px subtracted when scrolling to a section, so a sticky header cannot cover it. */
  offset: number;
  registerSection: (id: string, label: string) => void;
  unregisterSection: (id: string) => void;
  setActiveId: (id: string) => void;
}

export interface ScrollSpyProps {
  children: React.ReactNode;
  /** Offset from top when calculating active section (px) */
  offset?: number;
  /** Root margin for IntersectionObserver */
  rootMargin?: string;
  /** Called when active section changes */
  onActiveChange?: (id: string | null) => void;
}

export interface ScrollSpyNavProps extends React.HTMLAttributes<HTMLElement> {
  children: React.ReactNode;
}

export interface ScrollSpyNavItemProps extends React.HTMLAttributes<HTMLAnchorElement> {
  sectionId: string;
  children: React.ReactNode;
}

export interface ScrollSpySectionProps extends React.HTMLAttributes<HTMLDivElement> {
  id: string;
  label: string;
  children: React.ReactNode;
}
