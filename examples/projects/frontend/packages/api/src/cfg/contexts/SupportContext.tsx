'use client';

import React, { createContext, useContext, type ReactNode } from 'react';
import { api } from '../BaseClient';
import {
  useSupportTicketsList,
  useSupportTicketsRetrieve,
  useCreateSupportTicketsCreate,
  useUpdateSupportTicketsUpdate,
  usePartialUpdateSupportTicketsPartialUpdate,
  useDeleteSupportTicketsDestroy,
  useSupportTicketsMessagesList,
  useSupportTicketsMessagesRetrieve,
  useCreateSupportTicketsMessagesCreate,
  useUpdateSupportTicketsMessagesUpdate,
  usePartialUpdateSupportTicketsMessagesPartialUpdate,
  useDeleteSupportTicketsMessagesDestroy,
} from '../generated/_utils/hooks';
import type { API } from '../generated';
import type {
  Ticket,
  TicketRequest,
  PatchedTicketRequest,
  Message,
  MessageRequest,
  MessageCreateRequest,
  PatchedMessageRequest,
} from '../generated/_utils/schemas';

// ─────────────────────────────────────────────────────────────────────────
// Context Type
// ─────────────────────────────────────────────────────────────────────────

export interface SupportContextValue {
  // Tickets
  tickets: Ticket[] | undefined;
  isLoadingTickets: boolean;
  ticketsError: Error | undefined;
  refreshTickets: () => Promise<void>;

  // Ticket operations
  getTicket: (uuid: string) => Promise<Ticket | undefined>;
  createTicket: (data: TicketRequest) => Promise<Ticket>;
  updateTicket: (uuid: string, data: TicketRequest) => Promise<Ticket>;
  partialUpdateTicket: (uuid: string, data: PatchedTicketRequest) => Promise<Ticket>;
  deleteTicket: (uuid: string) => Promise<void>;

  // Messages
  getMessages: (ticketUuid: string) => Promise<Message[] | undefined>;
  getMessage: (ticketUuid: string, messageUuid: string) => Promise<Message | undefined>;
  createMessage: (ticketUuid: string, data: MessageCreateRequest) => Promise<Message>;
  updateMessage: (ticketUuid: string, messageUuid: string, data: MessageRequest) => Promise<Message>;
  partialUpdateMessage: (
    ticketUuid: string,
    messageUuid: string,
    data: PatchedMessageRequest
  ) => Promise<Message>;
  deleteMessage: (ticketUuid: string, messageUuid: string) => Promise<void>;
  refreshMessages: (ticketUuid: string) => Promise<void>;
}

// ─────────────────────────────────────────────────────────────────────────
// Context
// ─────────────────────────────────────────────────────────────────────────

const SupportContext = createContext<SupportContextValue | undefined>(undefined);

// ─────────────────────────────────────────────────────────────────────────
// Provider
// ─────────────────────────────────────────────────────────────────────────

export function SupportProvider({ children }: { children: ReactNode }) {
  // List tickets
  const {
    data: ticketsData,
    error: ticketsError,
    isLoading: isLoadingTickets,
    mutate: mutateTickets,
  } = useSupportTicketsList(undefined, api as unknown as API);

  const refreshTickets = async () => {
    await mutateTickets();
  };

  // Ticket mutations
  const createTicketMutation = useCreateSupportTicketsCreate();
  const updateTicketMutation = useUpdateSupportTicketsUpdate();
  const partialUpdateTicketMutation = usePartialUpdateSupportTicketsPartialUpdate();
  const deleteTicketMutation = useDeleteSupportTicketsDestroy();

  // Message mutations
  const createMessageMutation = useCreateSupportTicketsMessagesCreate();
  const updateMessageMutation = useUpdateSupportTicketsMessagesUpdate();
  const partialUpdateMessageMutation = usePartialUpdateSupportTicketsMessagesPartialUpdate();
  const deleteMessageMutation = useDeleteSupportTicketsMessagesDestroy();

  // Get single ticket
  const getTicket = async (uuid: string): Promise<Ticket | undefined> => {
    const { data } = useSupportTicketsRetrieve(uuid, api as unknown as API);
    return data;
  };

  // Create ticket
  const createTicket = async (data: TicketRequest): Promise<Ticket> => {
    const result = await createTicketMutation(data, api as unknown as API);
    await refreshTickets();
    return result as Ticket;
  };

  // Update ticket
  const updateTicket = async (uuid: string, data: TicketRequest): Promise<Ticket> => {
    const result = await updateTicketMutation(uuid, data, api as unknown as API);
    await refreshTickets();
    return result as Ticket;
  };

  // Partial update ticket (currently not supported by generated API)
  const partialUpdateTicket = async (
    uuid: string,
    data: PatchedTicketRequest
  ): Promise<Ticket> => {
    // TODO: Fix generator to include data parameter for PATCH requests
    // const result = await partialUpdateTicketMutation(uuid, data, api as unknown as API);
    // For now, fallback to full update
    const result = await updateTicketMutation(uuid, data as unknown as TicketRequest, api as unknown as API);
    await refreshTickets();
    return result as Ticket;
  };

  // Delete ticket
  const deleteTicket = async (uuid: string): Promise<void> => {
    await deleteTicketMutation(uuid, api as unknown as API);
    await refreshTickets();
  };

  // Get messages for ticket
  const getMessages = async (ticketUuid: string): Promise<Message[] | undefined> => {
    const { data } = useSupportTicketsMessagesList(ticketUuid, undefined, api as unknown as API);
    return data?.results;
  };

  // Get single message
  const getMessage = async (
    ticketUuid: string,
    messageUuid: string
  ): Promise<Message | undefined> => {
    const { data } = useSupportTicketsMessagesRetrieve(
      ticketUuid,
      messageUuid,
      api as unknown as API
    );
    return data;
  };

  // Create message
  const createMessage = async (
    ticketUuid: string,
    data: MessageCreateRequest
  ): Promise<Message> => {
    const result = await createMessageMutation(ticketUuid, data, api as unknown as API);
    return result as Message;
  };

  // Update message
  const updateMessage = async (
    ticketUuid: string,
    messageUuid: string,
    data: MessageRequest
  ): Promise<Message> => {
    const result = await updateMessageMutation(
      ticketUuid,
      messageUuid,
      data,
      api as unknown as API
    );
    return result as Message;
  };

  // Partial update message (currently not supported by generated API)
  const partialUpdateMessage = async (
    ticketUuid: string,
    messageUuid: string,
    data: PatchedMessageRequest
  ): Promise<Message> => {
    // TODO: Fix generator to include data parameter for PATCH requests
    // const result = await partialUpdateMessageMutation(ticketUuid, messageUuid, data, api as unknown as API);
    // For now, fallback to full update
    const result = await updateMessageMutation(
      ticketUuid,
      messageUuid,
      data as MessageRequest,
      api as unknown as API
    );
    return result as Message;
  };

  // Delete message
  const deleteMessage = async (ticketUuid: string, messageUuid: string): Promise<void> => {
    await deleteMessageMutation(ticketUuid, messageUuid, api as unknown as API);
  };

  // Refresh messages for specific ticket
  const refreshMessages = async (ticketUuid: string): Promise<void> => {
    // We'll use mutate from the hook, but we need to get it dynamically
    // For now, we can just refresh tickets which will update everything
    await refreshTickets();
  };

  const value: SupportContextValue = {
    tickets: ticketsData?.results,
    isLoadingTickets,
    ticketsError,
    refreshTickets,
    getTicket,
    createTicket,
    updateTicket,
    partialUpdateTicket,
    deleteTicket,
    getMessages,
    getMessage,
    createMessage,
    updateMessage,
    partialUpdateMessage,
    deleteMessage,
    refreshMessages,
  };

  return <SupportContext.Provider value={value}>{children}</SupportContext.Provider>;
}

// ─────────────────────────────────────────────────────────────────────────
// Hook
// ─────────────────────────────────────────────────────────────────────────

export function useSupportContext(): SupportContextValue {
  const context = useContext(SupportContext);
  if (!context) {
    throw new Error('useSupportContext must be used within SupportProvider');
  }
  return context;
}

// ─────────────────────────────────────────────────────────────────────────
// Re-export types for external use
// ─────────────────────────────────────────────────────────────────────────

export type {
  Ticket,
  TicketRequest,
  PatchedTicketRequest,
  Message,
  MessageRequest,
  MessageCreateRequest,
  PatchedMessageRequest,
};

