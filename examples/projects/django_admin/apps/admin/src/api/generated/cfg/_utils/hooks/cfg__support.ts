/**
 * SWR Hooks for Support
 *
 * React hooks powered by SWR for data fetching with automatic caching,
 * revalidation, and optimistic updates.
 *
 * Usage:
 * ```typescript
 * // Query hooks (GET)
 * const { data, error, isLoading } = useUsers({ page: 1 })
 *
 * // Mutation hooks (POST/PUT/PATCH/DELETE)
 * const createUser = useCreateUser()
 * await createUser({ name: 'John', email: 'john@example.com' })
 * ```
 */
import useSWR from 'swr'
import { useSWRConfig } from 'swr'
import * as Fetchers from '../fetchers/cfg__support'
import type { API } from '../../index'
import type { Message } from '../schemas/Message.schema'
import type { MessageCreate } from '../schemas/MessageCreate.schema'
import type { MessageCreateRequest } from '../schemas/MessageCreateRequest.schema'
import type { MessageRequest } from '../schemas/MessageRequest.schema'
import type { PaginatedMessageList } from '../schemas/PaginatedMessageList.schema'
import type { PaginatedTicketList } from '../schemas/PaginatedTicketList.schema'
import type { PatchedMessageRequest } from '../schemas/PatchedMessageRequest.schema'
import type { PatchedTicketRequest } from '../schemas/PatchedTicketRequest.schema'
import type { Ticket } from '../schemas/Ticket.schema'
import type { TicketRequest } from '../schemas/TicketRequest.schema'

/**
 * API operation
 *
 * @method GET
 * @path /cfg/support/tickets/
 */
export function useSupportTicketsList(params?: { page?: number; page_size?: number }, client?: API): ReturnType<typeof useSWR<PaginatedTicketList>> {
  return useSWR<PaginatedTicketList>(
    params ? ['cfg-support-tickets', params] : 'cfg-support-tickets',
    () => Fetchers.getSupportTicketsList(params, client)
  )
}


/**
 * API operation
 *
 * @method POST
 * @path /cfg/support/tickets/
 */
export function useCreateSupportTicketsCreate() {
  const { mutate } = useSWRConfig()

  return async (data: TicketRequest, client?: API): Promise<Ticket> => {
    const result = await Fetchers.createSupportTicketsCreate(data, client)
    // Revalidate related queries
    mutate('cfg-support-tickets')
    return result
  }
}


/**
 * API operation
 *
 * @method GET
 * @path /cfg/support/tickets/{ticket_uuid}/messages/
 */
export function useSupportTicketsMessagesList(ticket_uuid: string, params?: { page?: number; page_size?: number }, client?: API): ReturnType<typeof useSWR<PaginatedMessageList>> {
  return useSWR<PaginatedMessageList>(
    ['cfg-support-tickets-messages', ticket_uuid],
    () => Fetchers.getSupportTicketsMessagesList(ticket_uuid, params, client)
  )
}


/**
 * API operation
 *
 * @method POST
 * @path /cfg/support/tickets/{ticket_uuid}/messages/
 */
export function useCreateSupportTicketsMessagesCreate() {
  const { mutate } = useSWRConfig()

  return async (ticket_uuid: string, data: MessageCreateRequest, client?: API): Promise<MessageCreate> => {
    const result = await Fetchers.createSupportTicketsMessagesCreate(ticket_uuid, data, client)
    // Revalidate related queries
    mutate('cfg-support-tickets-messages')
    return result
  }
}


/**
 * API operation
 *
 * @method GET
 * @path /cfg/support/tickets/{ticket_uuid}/messages/{uuid}/
 */
export function useSupportTicketsMessagesRetrieve(ticket_uuid: string, uuid: string, client?: API): ReturnType<typeof useSWR<Message>> {
  return useSWR<Message>(
    ['cfg-support-tickets-message', ticket_uuid],
    () => Fetchers.getSupportTicketsMessagesRetrieve(ticket_uuid, uuid, client)
  )
}


/**
 * API operation
 *
 * @method PUT
 * @path /cfg/support/tickets/{ticket_uuid}/messages/{uuid}/
 */
export function useUpdateSupportTicketsMessagesUpdate() {
  const { mutate } = useSWRConfig()

  return async (ticket_uuid: string, uuid: string, data: MessageRequest, client?: API): Promise<Message> => {
    const result = await Fetchers.updateSupportTicketsMessagesUpdate(ticket_uuid, uuid, data, client)
    // Revalidate related queries
    mutate('cfg-support-tickets-messages')
    mutate('cfg-support-tickets-message')
    return result
  }
}


/**
 * API operation
 *
 * @method PATCH
 * @path /cfg/support/tickets/{ticket_uuid}/messages/{uuid}/
 */
export function usePartialUpdateSupportTicketsMessagesPartialUpdate() {
  const { mutate } = useSWRConfig()

  return async (ticket_uuid: string, uuid: string, data?: PatchedMessageRequest, client?: API): Promise<Message> => {
    const result = await Fetchers.partialUpdateSupportTicketsMessagesPartialUpdate(ticket_uuid, uuid, data, client)
    // Revalidate related queries
    mutate('cfg-support-tickets-messages-partial')
    return result
  }
}


/**
 * API operation
 *
 * @method DELETE
 * @path /cfg/support/tickets/{ticket_uuid}/messages/{uuid}/
 */
export function useDeleteSupportTicketsMessagesDestroy() {
  const { mutate } = useSWRConfig()

  return async (ticket_uuid: string, uuid: string, client?: API): Promise<void> => {
    const result = await Fetchers.deleteSupportTicketsMessagesDestroy(ticket_uuid, uuid, client)
    // Revalidate related queries
    mutate('cfg-support-tickets-messages')
    mutate('cfg-support-tickets-message')
    return result
  }
}


/**
 * API operation
 *
 * @method GET
 * @path /cfg/support/tickets/{uuid}/
 */
export function useSupportTicketsRetrieve(uuid: string, client?: API): ReturnType<typeof useSWR<Ticket>> {
  return useSWR<Ticket>(
    ['cfg-support-ticket', uuid],
    () => Fetchers.getSupportTicketsRetrieve(uuid, client)
  )
}


/**
 * API operation
 *
 * @method PUT
 * @path /cfg/support/tickets/{uuid}/
 */
export function useUpdateSupportTicketsUpdate() {
  const { mutate } = useSWRConfig()

  return async (uuid: string, data: TicketRequest, client?: API): Promise<Ticket> => {
    const result = await Fetchers.updateSupportTicketsUpdate(uuid, data, client)
    // Revalidate related queries
    mutate('cfg-support-tickets')
    mutate('cfg-support-ticket')
    return result
  }
}


/**
 * API operation
 *
 * @method PATCH
 * @path /cfg/support/tickets/{uuid}/
 */
export function usePartialUpdateSupportTicketsPartialUpdate() {
  const { mutate } = useSWRConfig()

  return async (uuid: string, data?: PatchedTicketRequest, client?: API): Promise<Ticket> => {
    const result = await Fetchers.partialUpdateSupportTicketsPartialUpdate(uuid, data, client)
    // Revalidate related queries
    mutate('cfg-support-tickets-partial')
    return result
  }
}


/**
 * API operation
 *
 * @method DELETE
 * @path /cfg/support/tickets/{uuid}/
 */
export function useDeleteSupportTicketsDestroy() {
  const { mutate } = useSWRConfig()

  return async (uuid: string, client?: API): Promise<void> => {
    const result = await Fetchers.deleteSupportTicketsDestroy(uuid, client)
    // Revalidate related queries
    mutate('cfg-support-tickets')
    mutate('cfg-support-ticket')
    return result
  }
}


