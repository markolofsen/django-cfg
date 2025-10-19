/**
 * Chat Types
 * Type definitions for RAG-powered chat widget
 */

import type { ChatMessage, ChatSource } from '@djangocfg/api/cfg/contexts';

// ─────────────────────────────────────────────────────────────────────────
// Extended Message Type (for UI with sources)
// ─────────────────────────────────────────────────────────────────────────

export interface ChatMessageWithSources extends ChatMessage {
  sources?: ChatSource[];
}

// ─────────────────────────────────────────────────────────────────────────
// Widget Props
// ─────────────────────────────────────────────────────────────────────────

export interface ChatWidgetProps {
  /** Whether to auto-open on mount */
  autoOpen?: boolean;
  /** Render even when closed (for animations) */
  persistent?: boolean;
  /** Additional CSS classes */
  className?: string;
  /** Callback when toggle state changes */
  onToggle?: (isOpen: boolean) => void;
  /** Callback when message is sent */
  onMessage?: (message: ChatMessageWithSources) => void;
}

// ─────────────────────────────────────────────────────────────────────────
// UI State
// ─────────────────────────────────────────────────────────────────────────

export interface ChatUIState {
  isOpen: boolean;
  isExpanded: boolean;
  isMinimized: boolean;
  showSources: boolean;
  showTimestamps: boolean;
}

// ─────────────────────────────────────────────────────────────────────────
// Component Props
// ─────────────────────────────────────────────────────────────────────────

export interface MessageListProps {
  messages: ChatMessageWithSources[];
  isLoading?: boolean;
  showSources?: boolean;
  showTimestamps?: boolean;
  autoScroll?: boolean;
  className?: string;
}

export interface MessageInputProps {
  onSend: (message: string) => Promise<void>;
  isLoading?: boolean;
  disabled?: boolean;
  placeholder?: string;
  className?: string;
}

export interface SessionListProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectSession: (sessionId: string) => void;
  className?: string;
}

// ─────────────────────────────────────────────────────────────────────────
// Re-export types from API
// ─────────────────────────────────────────────────────────────────────────

export type { ChatSource, ChatMessage } from '@djangocfg/api/cfg/contexts';

