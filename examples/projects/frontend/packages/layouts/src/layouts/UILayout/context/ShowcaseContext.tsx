/**
 * Showcase Context
 * Manages navigation state for ComponentShowcaseLayout
 */

'use client';

import React, { createContext, useContext, useState, ReactNode } from 'react';

interface ShowcaseContextValue {
  currentCategory: string;
  setCurrentCategory: (category: string) => void;
  isSidebarOpen: boolean;
  toggleSidebar: () => void;
  closeSidebar: () => void;
}

const ShowcaseContext = createContext<ShowcaseContextValue | undefined>(undefined);

interface ShowcaseProviderProps {
  children: ReactNode;
  defaultCategory?: string;
}

export function ShowcaseProvider({ children, defaultCategory = 'overview' }: ShowcaseProviderProps) {
  const [currentCategory, setCurrentCategory] = useState(defaultCategory);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const toggleSidebar = () => setIsSidebarOpen(prev => !prev);
  const closeSidebar = () => setIsSidebarOpen(false);

  return (
    <ShowcaseContext.Provider
      value={{
        currentCategory,
        setCurrentCategory,
        isSidebarOpen,
        toggleSidebar,
        closeSidebar,
      }}
    >
      {children}
    </ShowcaseContext.Provider>
  );
}

export function useShowcase() {
  const context = useContext(ShowcaseContext);
  if (!context) {
    throw new Error('useShowcase must be used within ShowcaseProvider');
  }
  return context;
}
