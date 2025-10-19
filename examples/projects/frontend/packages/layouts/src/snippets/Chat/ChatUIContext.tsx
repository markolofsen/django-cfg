/**
 * Chat UI Context
 * Manages UI state for chat widget (toggle, expand, minimize)
 */

'use client';

import React, { createContext, useContext, useState, useCallback, type ReactNode } from 'react';
import type { ChatUIState } from './types';

// ─────────────────────────────────────────────────────────────────────────
// Context Type
// ─────────────────────────────────────────────────────────────────────────

export interface ChatUIContextValue {
  uiState: ChatUIState;
  toggleChat: () => void;
  openChat: () => void;
  closeChat: () => void;
  expandChat: () => void;
  collapseChat: () => void;
  minimizeChat: () => void;
  toggleSources: () => void;
  toggleTimestamps: () => void;
}

// ─────────────────────────────────────────────────────────────────────────
// Context
// ─────────────────────────────────────────────────────────────────────────

const ChatUIContext = createContext<ChatUIContextValue | undefined>(undefined);

// ─────────────────────────────────────────────────────────────────────────
// Provider
// ─────────────────────────────────────────────────────────────────────────

export interface ChatUIProviderProps {
  children: ReactNode;
  initialState?: Partial<ChatUIState>;
}

export function ChatUIProvider({ children, initialState }: ChatUIProviderProps) {
  const [uiState, setUIState] = useState<ChatUIState>({
    isOpen: false,
    isExpanded: false,
    isMinimized: false,
    showSources: true,
    showTimestamps: false,
    ...initialState,
  });

  const toggleChat = useCallback(() => {
    setUIState((prev) => ({ ...prev, isOpen: !prev.isOpen }));
  }, []);

  const openChat = useCallback(() => {
    setUIState((prev) => ({ ...prev, isOpen: true }));
  }, []);

  const closeChat = useCallback(() => {
    setUIState((prev) => ({ ...prev, isOpen: false }));
  }, []);

  const expandChat = useCallback(() => {
    setUIState((prev) => ({ ...prev, isExpanded: true, isMinimized: false }));
  }, []);

  const collapseChat = useCallback(() => {
    setUIState((prev) => ({ ...prev, isExpanded: false }));
  }, []);

  const minimizeChat = useCallback(() => {
    setUIState((prev) => ({ ...prev, isMinimized: true, isExpanded: false }));
  }, []);

  const toggleSources = useCallback(() => {
    setUIState((prev) => ({ ...prev, showSources: !prev.showSources }));
  }, []);

  const toggleTimestamps = useCallback(() => {
    setUIState((prev) => ({ ...prev, showTimestamps: !prev.showTimestamps }));
  }, []);

  const value: ChatUIContextValue = {
    uiState,
    toggleChat,
    openChat,
    closeChat,
    expandChat,
    collapseChat,
    minimizeChat,
    toggleSources,
    toggleTimestamps,
  };

  return <ChatUIContext.Provider value={value}>{children}</ChatUIContext.Provider>;
}

// ─────────────────────────────────────────────────────────────────────────
// Hook
// ─────────────────────────────────────────────────────────────────────────

export function useChatUI(): ChatUIContextValue {
  const context = useContext(ChatUIContext);
  if (!context) {
    throw new Error('useChatUI must be used within ChatUIProvider');
  }
  return context;
}

