/**
 * SWR Hooks for Support
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
 * @path /django_cfg_support/tickets/
 */
export function useDjangoCfgSupportTickets() {
  return useSWR<any>(
    'django-cfg-support-tickets',
    () => Fetchers.getDjangoCfgSupportTickets()
  )
}

/**
 *
 * @method GET
 * @path /django_cfg_support/tickets/{ticket_uuid}/messages/
 */
export function useDjangoCfgSupportTicketsMessages(ticket_uuid: string) {
  return useSWR<any>(
    ['django-cfg-support-tickets-messages', ticket_uuid],
    () => Fetchers.getDjangoCfgSupportTicketsMessages(ticket_uuid)
  )
}

/**
 *
 * @method GET
 * @path /django_cfg_support/tickets/{ticket_uuid}/messages/{uuid}/
 */
export function useDjangoCfgSupportTicketsMessage(ticket_uuid: string, uuid: string) {
  return useSWR<Message>(
    ['django-cfg-support-tickets-message', ticket_uuid],
    () => Fetchers.getDjangoCfgSupportTicketsMessage(ticket_uuid, uuid)
  )
}

/**
 *
 * @method GET
 * @path /django_cfg_support/tickets/{uuid}/
 */
export function useDjangoCfgSupportTicket(uuid: string) {
  return useSWR<Ticket>(
    ['django-cfg-support-ticket', uuid],
    () => Fetchers.getDjangoCfgSupportTicket(uuid)
  )
}

// ===== Mutation Hooks (POST/PUT/PATCH/DELETE) =====

/**
 *
 * @method POST
 * @path /django_cfg_support/tickets/
 */
export function useCreateDjangoCfgSupportTickets() {
  const { mutate } = useSWRConfig()

  return async (data: TicketRequest): Promise<Ticket> => {
    const result = await Fetchers.createDjangoCfgSupportTickets(data)

    // Revalidate related queries
    mutate('django-cfg-support-tickets')

    return result
  }
}

/**
 *
 * @method POST
 * @path /django_cfg_support/tickets/{ticket_uuid}/messages/
 */
export function useCreateDjangoCfgSupportTicketsMessages() {
  const { mutate } = useSWRConfig()

  return async (ticket_uuid: string, data: MessageCreateRequest): Promise<MessageCreate> => {
    const result = await Fetchers.createDjangoCfgSupportTicketsMessages(ticket_uuid, data)

    // Revalidate related queries
    mutate('django-cfg-support-tickets-messages')

    return result
  }
}

/**
 *
 * @method PUT
 * @path /django_cfg_support/tickets/{ticket_uuid}/messages/{uuid}/
 */
export function useUpdateDjangoCfgSupportTicketsMessages() {
  const { mutate } = useSWRConfig()

  return async (ticket_uuid: string, uuid: string, data: MessageRequest): Promise<Message> => {
    const result = await Fetchers.updateDjangoCfgSupportTicketsMessages(ticket_uuid, uuid, data)

    // Revalidate related queries
    mutate('django-cfg-support-tickets-messages')
    mutate('django-cfg-support-tickets-message')

    return result
  }
}

/**
 *
 * @method PATCH
 * @path /django_cfg_support/tickets/{ticket_uuid}/messages/{uuid}/
 */
export function usePartialUpdateDjangoCfgSupportTicketsMessages() {
  const { mutate } = useSWRConfig()

  return async (ticket_uuid: string, uuid: string): Promise<Message> => {
    const result = await Fetchers.partialUpdateDjangoCfgSupportTicketsMessages(ticket_uuid, uuid)

    // Revalidate related queries
    mutate('django-cfg-support-tickets-messages-partial')

    return result
  }
}

/**
 *
 * @method DELETE
 * @path /django_cfg_support/tickets/{ticket_uuid}/messages/{uuid}/
 */
export function useDeleteDjangoCfgSupportTicketsMessages() {
  const { mutate } = useSWRConfig()

  return async (ticket_uuid: string, uuid: string): Promise<void> => {
    const result = await Fetchers.deleteDjangoCfgSupportTicketsMessages(ticket_uuid, uuid)

    // Revalidate related queries
    mutate('django-cfg-support-tickets-messages')
    mutate('django-cfg-support-tickets-message')

    return result
  }
}

/**
 *
 * @method PUT
 * @path /django_cfg_support/tickets/{uuid}/
 */
export function useUpdateDjangoCfgSupportTickets() {
  const { mutate } = useSWRConfig()

  return async (uuid: string, data: TicketRequest): Promise<Ticket> => {
    const result = await Fetchers.updateDjangoCfgSupportTickets(uuid, data)

    // Revalidate related queries
    mutate('django-cfg-support-tickets')
    mutate('django-cfg-support-ticket')

    return result
  }
}

/**
 *
 * @method PATCH
 * @path /django_cfg_support/tickets/{uuid}/
 */
export function usePartialUpdateDjangoCfgSupportTickets() {
  const { mutate } = useSWRConfig()

  return async (uuid: string): Promise<Ticket> => {
    const result = await Fetchers.partialUpdateDjangoCfgSupportTickets(uuid)

    // Revalidate related queries
    mutate('django-cfg-support-tickets-partial')

    return result
  }
}

/**
 *
 * @method DELETE
 * @path /django_cfg_support/tickets/{uuid}/
 */
export function useDeleteDjangoCfgSupportTickets() {
  const { mutate } = useSWRConfig()

  return async (uuid: string): Promise<void> => {
    const result = await Fetchers.deleteDjangoCfgSupportTickets(uuid)

    // Revalidate related queries
    mutate('django-cfg-support-tickets')
    mutate('django-cfg-support-ticket')

    return result
  }
}
