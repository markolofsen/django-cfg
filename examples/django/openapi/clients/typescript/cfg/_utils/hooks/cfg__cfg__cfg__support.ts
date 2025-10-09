/**
 * SWR Hooks for Cfg Support
 *
 * Auto-generated React hooks for data fetching with SWR.
 *
 * Setup:
 * ```typescript
 * // Configure API once (in your app root)
 * import { configureAPI } from '../../api-instance'
 * configureAPI({ baseUrl: 'https://api.example.com' })
 * ```
 *
 * Usage:
 * ```typescript
 * // Query hook
 * const { data, error, mutate } = useShopProducts({ page: 1 })
 *
 * // Mutation hook
 * const createProduct = useCreateShopProduct()
 * await createProduct({ name: 'Product', price: 99 })
 * ```
 */
import type { Message } from '../schemas/Message.schema'
import type { MessageCreate } from '../schemas/MessageCreate.schema'
import type { MessageCreateRequest } from '../schemas/MessageCreateRequest.schema'
import type { MessageRequest } from '../schemas/MessageRequest.schema'
import type { PatchedMessageRequest } from '../schemas/PatchedMessageRequest.schema'
import type { PatchedTicketRequest } from '../schemas/PatchedTicketRequest.schema'
import type { Ticket } from '../schemas/Ticket.schema'
import type { TicketRequest } from '../schemas/TicketRequest.schema'
import useSWR from 'swr'
import { useSWRConfig } from 'swr'
import * as Fetchers from '../fetchers'

// ===== Query Hooks (GET) =====

/**
 *
 * @method GET
 * @path /cfg/support/tickets/
 */
export function useCfgSupportTicketsList() {
  return useSWR<any>(
    'cfg-support-tickets',
    () => Fetchers.getCfgSupportTicketsList()
  )
}

/**
 *
 * @method GET
 * @path /cfg/support/tickets/{ticket_uuid}/messages/
 */
export function useCfgSupportTicketsMessagesList(ticket_uuid: string) {
  return useSWR<any>(
    ['cfg-support-tickets-messages', ticket_uuid],
    () => Fetchers.getCfgSupportTicketsMessagesList(ticket_uuid)
  )
}

/**
 *
 * @method GET
 * @path /cfg/support/tickets/{ticket_uuid}/messages/{uuid}/
 */
export function useCfgSupportTicketsMessagesById(ticket_uuid: string, uuid: string) {
  return useSWR<Message>(
    ['cfg-support-tickets-message', ticket_uuid],
    () => Fetchers.getCfgSupportTicketsMessagesById(ticket_uuid, uuid)
  )
}

/**
 *
 * @method GET
 * @path /cfg/support/tickets/{uuid}/
 */
export function useCfgSupportTicketsById(uuid: string) {
  return useSWR<Ticket>(
    ['cfg-support-ticket', uuid],
    () => Fetchers.getCfgSupportTicketsById(uuid)
  )
}

// ===== Mutation Hooks (POST/PUT/PATCH/DELETE) =====

/**
 *
 * @method POST
 * @path /cfg/support/tickets/
 */
export function useCreateCfgSupportTickets() {
  const { mutate } = useSWRConfig()

  return async (data: TicketRequest): Promise<Ticket> => {
    const result = await Fetchers.createCfgSupportTickets(data)

    // Revalidate related queries
    mutate('cfg-support-tickets')

    return result
  }
}

/**
 *
 * @method POST
 * @path /cfg/support/tickets/{ticket_uuid}/messages/
 */
export function useCreateCfgSupportTicketsMessages() {
  const { mutate } = useSWRConfig()

  return async (ticket_uuid: string, data: MessageCreateRequest): Promise<MessageCreate> => {
    const result = await Fetchers.createCfgSupportTicketsMessages(ticket_uuid, data)

    // Revalidate related queries
    mutate('cfg-support-tickets-messages')

    return result
  }
}

/**
 *
 * @method PUT
 * @path /cfg/support/tickets/{ticket_uuid}/messages/{uuid}/
 */
export function useUpdateCfgSupportTicketsMessages() {
  const { mutate } = useSWRConfig()

  return async (ticket_uuid: string, uuid: string, data: MessageRequest): Promise<Message> => {
    const result = await Fetchers.updateCfgSupportTicketsMessages(ticket_uuid, uuid, data)

    // Revalidate related queries
    mutate('cfg-support-tickets-messages')
    mutate('cfg-support-tickets-message')

    return result
  }
}

/**
 *
 * @method PATCH
 * @path /cfg/support/tickets/{ticket_uuid}/messages/{uuid}/
 */
export function usePartialUpdateCfgSupportTicketsMessages() {
  const { mutate } = useSWRConfig()

  return async (ticket_uuid: string, uuid: string): Promise<Message> => {
    const result = await Fetchers.partialUpdateCfgSupportTicketsMessages(ticket_uuid, uuid)

    // Revalidate related queries
    mutate('cfg-support-tickets-messages-partial')

    return result
  }
}

/**
 *
 * @method DELETE
 * @path /cfg/support/tickets/{ticket_uuid}/messages/{uuid}/
 */
export function useDeleteCfgSupportTicketsMessages() {
  const { mutate } = useSWRConfig()

  return async (ticket_uuid: string, uuid: string): Promise<void> => {
    const result = await Fetchers.deleteCfgSupportTicketsMessages(ticket_uuid, uuid)

    // Revalidate related queries
    mutate('cfg-support-tickets-messages')
    mutate('cfg-support-tickets-message')

    return result
  }
}

/**
 *
 * @method PUT
 * @path /cfg/support/tickets/{uuid}/
 */
export function useUpdateCfgSupportTickets() {
  const { mutate } = useSWRConfig()

  return async (uuid: string, data: TicketRequest): Promise<Ticket> => {
    const result = await Fetchers.updateCfgSupportTickets(uuid, data)

    // Revalidate related queries
    mutate('cfg-support-tickets')
    mutate('cfg-support-ticket')

    return result
  }
}

/**
 *
 * @method PATCH
 * @path /cfg/support/tickets/{uuid}/
 */
export function usePartialUpdateCfgSupportTickets() {
  const { mutate } = useSWRConfig()

  return async (uuid: string): Promise<Ticket> => {
    const result = await Fetchers.partialUpdateCfgSupportTickets(uuid)

    // Revalidate related queries
    mutate('cfg-support-tickets-partial')

    return result
  }
}

/**
 *
 * @method DELETE
 * @path /cfg/support/tickets/{uuid}/
 */
export function useDeleteCfgSupportTickets() {
  const { mutate } = useSWRConfig()

  return async (uuid: string): Promise<void> => {
    const result = await Fetchers.deleteCfgSupportTickets(uuid)

    // Revalidate related queries
    mutate('cfg-support-tickets')
    mutate('cfg-support-ticket')

    return result
  }
}
