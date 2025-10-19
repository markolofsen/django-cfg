/**
 * Knowledge Chat Module
 * Complete RAG-powered chat widget with context providers
 */

'use client';

import React from 'react';
import { KnowbaseChatProvider, KnowbaseSessionsProvider } from '@djangocfg/api/cfg/contexts';
import { ChatUIProvider } from './ChatUIContext';
import { ChatWidget } from './ChatWidget';
import type { ChatWidgetProps } from './types';

// ─────────────────────────────────────────────────────────────────────────
// Main Component with Providers
// ─────────────────────────────────────────────────────────────────────────

export const KnowledgeChat: React.FC<ChatWidgetProps> = (props) => {
  return (
    <KnowbaseChatProvider>
      <KnowbaseSessionsProvider>
        <ChatUIProvider initialState={{ isOpen: false }}>
          <ChatWidget {...props} />
        </ChatUIProvider>
      </KnowbaseSessionsProvider>
    </KnowbaseChatProvider>
  );
};

// ─────────────────────────────────────────────────────────────────────────
// Named Exports
// ─────────────────────────────────────────────────────────────────────────

export { ChatWidget } from './ChatWidget';
export { ChatUIProvider, useChatUI } from './ChatUIContext';
export { MessageList, MessageInput, SessionList } from './components';
export * from './types';

// ─────────────────────────────────────────────────────────────────────────
// Default Export
// ─────────────────────────────────────────────────────────────────────────

export default KnowledgeChat;

