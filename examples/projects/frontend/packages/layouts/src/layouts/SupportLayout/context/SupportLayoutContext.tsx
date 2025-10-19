/**
 * Support Layout Context
 * Wrapper around SupportContext with UI state, event handling and infinite scroll
 */

'use client';

import React, { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from 'react';
import { useSupportContext, type Ticket } from '@djangocfg/api/cfg/contexts';
import { CfgSupportTypes } from '@djangocfg/api';
import { supportLogger } from '../../../utils/logger';

type Message = CfgSupportTypes.Message;
type MessageCreateRequest = CfgSupportTypes.MessageCreateRequest;
import { useAuth } from '../../../auth';
import { SUPPORT_LAYOUT_EVENTS } from '../events';
import { useInfiniteMessages } from '../hooks';
import type { SupportUIState, TicketFormData } from '../types';

// ─────────────────────────────────────────────────────────────────────────
// Context Type
// ─────────────────────────────────────────────────────────────────────────

export interface SupportLayoutContextValue {
  // From API context
  tickets: Ticket[] | undefined;
  isLoadingTickets: boolean;
  ticketsError: Error | undefined;

  // Selected ticket data
  selectedTicket: Ticket | undefined;
  selectedTicketMessages: Message[] | undefined;
  isLoadingMessages: boolean;

  // Infinite scroll for messages
  isLoadingMoreMessages: boolean;
  hasMoreMessages: boolean;
  totalMessagesCount: number;
  loadMoreMessages: () => void;

  // UI state
  uiState: SupportUIState;

  // Actions
  selectTicket: (ticket: Ticket | null) => void;
  createTicket: (data: TicketFormData) => Promise<void>;
  sendMessage: (message: string) => Promise<void>;
  refreshTickets: () => Promise<void>;
  refreshMessages: () => Promise<void>;

  // Dialog actions
  openCreateDialog: () => void;
  closeCreateDialog: () => void;

  // Utilities
  getUnreadCount: () => number;
}

// ─────────────────────────────────────────────────────────────────────────
// Context
// ─────────────────────────────────────────────────────────────────────────

const SupportLayoutContext = createContext<SupportLayoutContextValue | undefined>(undefined);

// ─────────────────────────────────────────────────────────────────────────
// Provider
// ─────────────────────────────────────────────────────────────────────────

interface SupportLayoutProviderProps {
  children: ReactNode;
}

export function SupportLayoutProvider({ children }: SupportLayoutProviderProps) {
  const support = useSupportContext();
  const { user } = useAuth();

  // UI state
  const [uiState, setUIState] = useState<SupportUIState>({
    selectedTicketUuid: null,
    isCreateDialogOpen: false,
    viewMode: 'list',
  });

  // Selected ticket
  const selectedTicket = support.tickets?.find(t => t.uuid === uiState.selectedTicketUuid);

  // Use infinite scroll hook for messages
  const {
    messages: selectedTicketMessages,
    isLoading: isLoadingMessages,
    isLoadingMore: isLoadingMoreMessages,
    hasMore: hasMoreMessages,
    totalCount: totalMessagesCount,
    loadMore: loadMoreMessages,
    refresh: refreshMessages,
    addMessage: addMessageOptimistically,
  } = useInfiniteMessages(selectedTicket?.uuid || null);

  // Select ticket
  const selectTicket = useCallback(async (ticket: Ticket | null) => {
    setUIState(prev => ({ ...prev, selectedTicketUuid: ticket?.uuid || null }));

    if (ticket?.uuid) {
      // The messages will be loaded automatically by the useInfiniteMessages hook
      // when the ticket UUID changes

      // Dispatch event
      window.dispatchEvent(
        new CustomEvent(SUPPORT_LAYOUT_EVENTS.TICKET_SELECTED, { detail: { ticket } })
      );
    }
  }, []);

  // Create ticket
  const createTicket = useCallback(async (data: TicketFormData) => {
    if (!user?.id) {
      throw new Error('User must be authenticated to create tickets');
    }

    const ticket = await support.createTicket({
      user: user.id,
      subject: data.subject,
    });

    // Send initial message if provided
    if (ticket.uuid && data.message) {
      await support.createMessage(ticket.uuid, {
        text: data.message,
      });
    }

    // Close dialog first for better UX
    setUIState(prev => ({ ...prev, isCreateDialogOpen: false }));

    // Refresh tickets list to show the new ticket
    await support.refreshTickets();

    // Dispatch event
    window.dispatchEvent(
      new CustomEvent(SUPPORT_LAYOUT_EVENTS.TICKET_CREATED, { detail: { ticket } })
    );

    // Auto-select the newly created ticket after refresh
    // Use the ticket UUID directly to ensure selection works even if the ticket object changes
    setUIState(prev => ({ ...prev, selectedTicketUuid: ticket.uuid }));

    // Dispatch selection event
    window.dispatchEvent(
      new CustomEvent(SUPPORT_LAYOUT_EVENTS.TICKET_SELECTED, { detail: { ticket } })
    );
  }, [support, user]);

  // Send message
  const sendMessage = useCallback(async (message: string) => {
    if (!selectedTicket?.uuid) return;

    // Create the message object
    const messageData: MessageCreateRequest = {
      text: message,
    };

    // Send message to backend
    const newMessage = await support.createMessage(selectedTicket.uuid, messageData);

    // Add message optimistically to the UI (it will be replaced when refreshing)
    if (newMessage) {
      const fullMessage: Message = {
        uuid: newMessage.uuid || `temp-${Date.now()}`,
        ticket: selectedTicket.uuid,
        sender: {
          id: user?.id || 0,
          display_username: user?.display_username || '',
          email: user?.email || '',
          avatar: user?.avatar || null,
          initials: user?.initials || '',
          is_staff: user?.is_staff || false,
          is_superuser: user?.is_superuser || false,
        },
        is_from_author: true,
        text: message,
        created_at: new Date().toISOString(),
      };

      addMessageOptimistically(fullMessage);
    }

    // Refresh messages to get the latest state
    await refreshMessages();

    // Dispatch event
    window.dispatchEvent(
      new CustomEvent(SUPPORT_LAYOUT_EVENTS.MESSAGE_SENT, { detail: { message: newMessage } })
    );
  }, [selectedTicket, support, user, addMessageOptimistically, refreshMessages]);

  // Dialog actions
  const openCreateDialog = useCallback(() => {
    setUIState(prev => ({ ...prev, isCreateDialogOpen: true }));
  }, []);

  const closeCreateDialog = useCallback(() => {
    setUIState(prev => ({ ...prev, isCreateDialogOpen: false }));
  }, []);

  // Get unread count
  const getUnreadCount = useCallback(() => {
    return support.tickets?.reduce((count, ticket) => count + (ticket.unanswered_messages_count || 0), 0) || 0;
  }, [support.tickets]);

  // Event listeners
  useEffect(() => {
    const handleOpenDialog = () => openCreateDialog();
    const handleCloseDialog = () => closeCreateDialog();

    window.addEventListener(SUPPORT_LAYOUT_EVENTS.OPEN_CREATE_DIALOG, handleOpenDialog);
    window.addEventListener(SUPPORT_LAYOUT_EVENTS.CLOSE_CREATE_DIALOG, handleCloseDialog);

    return () => {
      window.removeEventListener(SUPPORT_LAYOUT_EVENTS.OPEN_CREATE_DIALOG, handleOpenDialog);
      window.removeEventListener(SUPPORT_LAYOUT_EVENTS.CLOSE_CREATE_DIALOG, handleCloseDialog);
    };
  }, [openCreateDialog, closeCreateDialog]);

  const value: SupportLayoutContextValue = {
    tickets: support.tickets,
    isLoadingTickets: support.isLoadingTickets,
    ticketsError: support.ticketsError,
    selectedTicket,
    selectedTicketMessages,
    isLoadingMessages,
    isLoadingMoreMessages,
    hasMoreMessages,
    totalMessagesCount,
    loadMoreMessages,
    uiState,
    selectTicket,
    createTicket,
    sendMessage,
    refreshTickets: support.refreshTickets,
    refreshMessages,
    openCreateDialog,
    closeCreateDialog,
    getUnreadCount,
  };

  return (
    <SupportLayoutContext.Provider value={value}>
      {children}
    </SupportLayoutContext.Provider>
  );
}

// ─────────────────────────────────────────────────────────────────────────
// Hook
// ─────────────────────────────────────────────────────────────────────────

export function useSupportLayoutContext(): SupportLayoutContextValue {
  const context = useContext(SupportLayoutContext);
  if (!context) {
    throw new Error('useSupportLayoutContext must be used within SupportLayoutProvider');
  }
  return context;
}