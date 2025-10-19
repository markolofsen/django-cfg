/**
 * Chat Widget Component
 * RAG-powered chat interface with session management
 */

'use client';

import React, { useCallback, useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import {useRouter} from 'next/router';
import { Card, CardContent, CardHeader, Button, useIsMobile, useLocalStorage } from '@djangocfg/ui';
import {
  MessageSquare,
  X,
  Maximize2,
  Minimize2,
  Plus,
  List,
} from 'lucide-react';
import { useKnowbaseChatContext, useKnowbaseSessionsContext, type ChatSource } from '@djangocfg/api/cfg/contexts';
import { Enums } from '@djangocfg/api/cfg/generated';
import { chatLogger } from '../../utils/logger';
import { useChatUI } from './ChatUIContext';
import { MessageList, MessageInput, SessionList } from './components';
import type { ChatWidgetProps, ChatMessageWithSources } from './types';

const WIDGET_MAX_WIDTH = 800;
const WIDGET_MAX_HEIGHT = 900;

// ─────────────────────────────────────────────────────────────────────────
// Chat Widget Component
// ─────────────────────────────────────────────────────────────────────────

export const ChatWidget: React.FC<ChatWidgetProps> = ({
  autoOpen = false,
  persistent = true,
  className = '',
  onToggle,
  onMessage,
}) => {
  const { sendQuery, getChatHistory } = useKnowbaseChatContext();
  const { createSession, getSession } = useKnowbaseSessionsContext();
  const {
    uiState,
    toggleChat,
    expandChat,
    collapseChat,
    toggleSources,
    toggleTimestamps,
  } = useChatUI();

  const router = useRouter();
  const isMobile = useIsMobile();
  
  const [isLoading, setIsLoading] = useState(false);
  const [showSessions, setShowSessions] = useState(false);
  const [mounted, setMounted] = useState(false);

  // Persist session ID and messages in localStorage
  const [currentSessionId, setCurrentSessionId] = useLocalStorage<string | null>(
    'chat_session_id',
    null
  );
  const [messages, setMessages] = useLocalStorage<ChatMessageWithSources[]>(
    'chat_messages',
    []
  );

  const isSupport = router.pathname.startsWith('/private/support');
  const isContact = router.pathname.startsWith('/private/contact');

  // Mount portal target
  useEffect(() => {
    setMounted(true);
  }, []);

  // if isSupport or isContact, don't render
  useEffect(() => {
    if (isSupport || isContact) {
      setMounted(false);
    } else {
      setMounted(true);
    }
  }, [isSupport, isContact]);

  // Auto-open on mount if specified
  useEffect(() => {
    if (autoOpen && !uiState.isOpen) {
      toggleChat();
    }
  }, [autoOpen, uiState.isOpen, toggleChat]);

  // Notify parent of toggle changes
  useEffect(() => {
    if (onToggle) {
      onToggle(uiState.isOpen);
    }
  }, [uiState.isOpen, onToggle]);

  // Load chat history when session changes (only if it's different from what we had)
  useEffect(() => {
    if (currentSessionId) {
      // Only load from server if we don't have messages locally or session changed
      if (messages.length === 0) {
        loadChatHistory(currentSessionId);
      }
    }
  }, [currentSessionId]);

  // Load chat history
  const loadChatHistory = async (sessionId: string) => {
    try {
      const history = await getChatHistory(sessionId);
      if (history?.messages) {
        // Convert ChatMessage[] to ChatMessageWithSources[]
        const messagesWithSources: ChatMessageWithSources[] = history.messages.map(msg => ({
          ...msg,
          sources: undefined, // Sources come from ChatResponse, not ChatMessage
        }));
        setMessages(messagesWithSources);
      }
    } catch (error) {
      chatLogger.error('Failed to load chat history:', error);
      // If we can't load the session, clear it
      setCurrentSessionId(null);
      setMessages([]);
    }
  };

  // Handle message sending
  const handleSendMessage = useCallback(
    async (message: string) => {
      try {
        setIsLoading(true);

        // Create session if we don't have one
        let sessionId = currentSessionId;
        if (!sessionId) {
          try {
            const newSession = await createSession({
              title: message.substring(0, 50), // Use first 50 chars as title
            });
            sessionId = newSession.id;
            setCurrentSessionId(sessionId);
            chatLogger.info('Created new chat session:', sessionId);
          } catch (error) {
            chatLogger.error('Failed to create session:', error);
            // Continue without session if creation fails
          }
        }

        // Add user message to UI
        const userMessage: ChatMessageWithSources = {
          id: `temp-${Date.now()}`,
          role: Enums.ChatMessageRole.USER,
          content: message,
          cost_usd: 0,
          created_at: new Date().toISOString(),
        };
        // Don't use functional form with useLocalStorage - use direct value
        const updatedMessages = [...messages, userMessage];
        setMessages(updatedMessages);

        // Send query to backend with session ID
        const response = await sendQuery({
          query: message,
          session_id: sessionId || undefined,
        });

        // Add assistant response to UI
        if (response) {
          const assistantMessage: ChatMessageWithSources = {
            id: response.message_id,
            role: Enums.ChatMessageRole.ASSISTANT,
            content: response.content,
            cost_usd: response.cost_usd,
            tokens_used: response.tokens_used,
            processing_time_ms: response.processing_time_ms,
            created_at: new Date().toISOString(),
            sources: response.sources || undefined,
          };
          // Don't use functional form with useLocalStorage - use direct value
          const finalMessages = [...updatedMessages, assistantMessage];
          setMessages(finalMessages);

          if (onMessage) {
            onMessage(assistantMessage);
          }
        }
      } catch (error) {
        chatLogger.error('Failed to send message:', error);
        throw error;
      } finally {
        setIsLoading(false);
      }
    },
    [sendQuery, currentSessionId, createSession, setCurrentSessionId, messages, setMessages, onMessage]
  );

  // Handle new chat creation
  const handleNewChat = useCallback(() => {
    setMessages([]);
    setCurrentSessionId(null);
  }, [setMessages, setCurrentSessionId]);

  // Handle session selection
  const handleSelectSession = useCallback((sessionId: string) => {
    // Clear current messages before loading new session
    setMessages([]);
    setCurrentSessionId(sessionId);
  }, [setMessages, setCurrentSessionId]);

  // Don't render if not mounted (SSR safety)
  if (!mounted) {
    return null;
  }

  // Don't render if not open and not persistent
  if (!uiState.isOpen && !persistent) {
    return null;
  }

  // Mobile layout
  if (isMobile) {
    const mobileContent = (
      <>
        <div
          className={`fixed inset-0 z-[9999] bg-background ${
            uiState.isOpen ? 'block' : 'hidden'
          } ${className}`}
        >
          <div className="flex flex-col h-full">
            {/* Mobile header */}
            <div className="flex items-center justify-between p-4 border-b bg-background shadow-sm">
              <div className="flex items-center gap-2">
                <MessageSquare className="h-5 w-5 text-primary" />
                <h2 className="font-semibold text-foreground">Knowledge Assistant</h2>
              </div>

              <div className="flex items-center gap-2">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowSessions(true)}
                  className="text-muted-foreground hover:text-foreground"
                  title="Sessions"
                >
                  <List className="h-5 w-5" />
                </Button>

                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleNewChat}
                  className="text-muted-foreground hover:text-foreground"
                  title="New Chat"
                >
                  <Plus className="h-5 w-5" />
                </Button>

                <Button
                  variant="ghost"
                  size="sm"
                  onClick={toggleChat}
                  className="text-muted-foreground hover:text-foreground"
                >
                  <X className="h-5 w-5" />
                </Button>
              </div>
            </div>

            {/* Chat area */}
            <div className="flex-1 flex flex-col overflow-hidden">
              <MessageList
                messages={messages}
                isLoading={isLoading}
                showSources={uiState.showSources}
                showTimestamps={uiState.showTimestamps}
                autoScroll={true}
                className="flex-1"
              />

              <MessageInput
                onSend={handleSendMessage}
                isLoading={isLoading}
                placeholder="Ask me anything..."
              />
            </div>
          </div>
        </div>

        {/* Session List Drawer */}
        <SessionList
          isOpen={showSessions}
          onClose={() => setShowSessions(false)}
          onSelectSession={handleSelectSession}
        />
      </>
    );
    
    return createPortal(mobileContent, document.body);
  }

  // Desktop layout
  const widgetWidth = uiState.isExpanded ? WIDGET_MAX_WIDTH : 400;
  const widgetHeight = uiState.isExpanded ? WIDGET_MAX_HEIGHT : 600;
  
  // When expanded, add top margin; when collapsed, stick to bottom
  const widgetStyle = uiState.isExpanded
    ? {
        position: 'fixed' as const,
        top: '24px',
        bottom: '24px',
        right: '24px',
        left: 'auto',
        width: widgetWidth,
        height: 'auto',
        zIndex: 40,
        transformOrigin: 'bottom right' as const,
      }
    : {
        position: 'fixed' as const,
        bottom: '24px',
        right: '24px',
        width: widgetWidth,
        height: widgetHeight,
        zIndex: 40,
        transformOrigin: 'bottom right' as const,
      };

  const content = (
    <>
      {/* Chat Window */}
      {uiState.isOpen && (
        <div
            className="fixed z-40 
                       animate-in fade-in zoom-in-95 slide-in-from-bottom-8 
                       duration-500 ease-out"
            style={widgetStyle}
          >
        <Card className="h-full flex flex-col shadow-2xl border-2 border-primary/20">
          {/* Header */}
          <CardHeader className="flex-row items-center justify-between space-y-0 pb-3 border-b">
            <div className="flex items-center gap-2">
              <MessageSquare className="h-5 w-5 text-primary" />
              <h3 className="font-semibold text-foreground">Support</h3>
            </div>

            <div className="flex items-center gap-1">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowSessions(true)}
                className="h-8 w-8 p-0"
                title="Sessions"
              >
                <List className="h-4 w-4" />
              </Button>

              <Button
                variant="ghost"
                size="sm"
                onClick={handleNewChat}
                className="h-8 w-8 p-0"
                title="New Chat"
              >
                <Plus className="h-4 w-4" />
              </Button>

              <Button
                variant="ghost"
                size="sm"
                onClick={uiState.isExpanded ? collapseChat : expandChat}
                className="h-8 w-8 p-0"
                title={uiState.isExpanded ? 'Collapse' : 'Expand'}
              >
                {uiState.isExpanded ? (
                  <Minimize2 className="h-4 w-4" />
                ) : (
                  <Maximize2 className="h-4 w-4" />
                )}
              </Button>

              <Button
                variant="ghost"
                size="sm"
                onClick={toggleChat}
                className="h-8 w-8 p-0"
                title="Close"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          </CardHeader>

          {/* Content */}
          <CardContent className="flex-1 flex flex-col p-0 overflow-hidden">
            <MessageList
              messages={messages}
              isLoading={isLoading}
              showSources={uiState.showSources}
              showTimestamps={uiState.showTimestamps}
              autoScroll={true}
              className="flex-1"
            />

            <MessageInput
              onSend={handleSendMessage}
              isLoading={isLoading}
              placeholder="Ask me anything..."
            />
          </CardContent>
        </Card>
        </div>
      )}

      {/* Floating Action Button (when closed) */}
      {!uiState.isOpen && persistent && (
        <div
          className="fixed z-40 animate-in fade-in zoom-in-95 slide-in-from-bottom-8 duration-500"
          style={{
            bottom: '24px',
            right: '24px',
            zIndex: 40,
            width: '64px',
            height: '64px',
            borderRadius: '50%',
            animation: 'pulse-shadow 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
          }}
        >
          <style>{`
            @keyframes pulse-shadow {
              0%, 100% {
                box-shadow: 0 0 0 0 hsl(var(--primary) / 0.7);
              }
              50% {
                box-shadow: 0 0 0 20px hsl(var(--primary) / 0);
              }
            }
          `}</style>
          <Button
            onClick={toggleChat}
            className="w-full h-full rounded-full shadow-2xl 
                       hover:scale-110 hover:rotate-12 active:scale-95 
                       transition-all duration-300 ease-out
                       flex items-center justify-center
                       group"
            style={{
              backgroundColor: 'hsl(var(--primary))',
              borderRadius: '50%',
              padding: 0,
            }}
            title="Open Support Chat"
            aria-label="Open Support Chat"
          >
            <MessageSquare 
              className="h-7 w-7 text-primary-foreground group-hover:scale-110 transition-transform duration-300" 
              strokeWidth={2} 
            />
          </Button>
        </div>
      )}

      {/* Session List Drawer */}
      <SessionList
        isOpen={showSessions}
        onClose={() => setShowSessions(false)}
        onSelectSession={handleSelectSession}
      />
    </>
  );

  // Render to portal
  return createPortal(content, document.body);
};

