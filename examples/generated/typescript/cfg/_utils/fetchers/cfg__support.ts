/**
 * Typed fetchers for Support
 *
 * Universal functions that work in any environment:
 * - Next.js (App Router / Pages Router / Server Components)
 * - React Native
 * - Node.js backend
 *
 * These fetchers use Zod schemas for runtime validation.
 *
 * Usage:
 * ```typescript
 * // Configure API once (in your app entry point)
 * import { configureAPI } from '../../api-instance'
 * configureAPI({ baseUrl: 'https://api.example.com' })
 *
 * // Then use fetchers anywhere
 * const users = await getUsers({ page: 1 })
 *
 * // With SWR
 * const { data } = useSWR(['users', params], () => getUsers(params))
 *
 * // With React Query
 * const { data } = useQuery(['users', params], () => getUsers(params))
 *
 * // In Server Component or SSR (pass custom client)
 * import { API } from '../../index'
 * const api = new API('https://api.example.com')
 * const users = await getUsers({ page: 1 }, api)
 * ```
 */
import { MessageSchema, type Message } from '../schemas/Message.schema'
import { MessageCreateSchema, type MessageCreate } from '../schemas/MessageCreate.schema'
import { MessageCreateRequestSchema, type MessageCreateRequest } from '../schemas/MessageCreateRequest.schema'
import { MessageRequestSchema, type MessageRequest } from '../schemas/MessageRequest.schema'
import { TicketSchema, type Ticket } from '../schemas/Ticket.schema'
import { TicketRequestSchema, type TicketRequest } from '../schemas/TicketRequest.schema'
import { getAPIInstance } from '../../api-instance'
import type { API } from '../../index'

/**
 * getDjangoCfgSupportTicketsList
 *
 * ViewSet for managing support tickets.
 *
 * @method GET
 * @path /django_cfg_support/tickets/
 */
export async function getDjangoCfgSupportTicketsList(
  client?: API
): Promise<any> {
  const api = client || getAPIInstance()

  const response = await api.cfg_support.ticketsList()
  return response
}

/**
 * createDjangoCfgSupportTickets
 *
 * ViewSet for managing support tickets.
 *
 * @method POST
 * @path /django_cfg_support/tickets/
 */
export async function createDjangoCfgSupportTickets(
  data: TicketRequest,
  client?: API
): Promise<Ticket> {
  const api = client || getAPIInstance()

  const response = await api.cfg_support.ticketsCreate(data)
  return TicketSchema.parse(response)
}

/**
 * getDjangoCfgSupportTicketsMessagesList
 *
 * ViewSet for managing support messages.
 *
 * @method GET
 * @path /django_cfg_support/tickets/{ticket_uuid}/messages/
 */
export async function getDjangoCfgSupportTicketsMessagesList(
  ticket_uuid: string,
  client?: API
): Promise<any> {
  const api = client || getAPIInstance()

  const response = await api.cfg_support.ticketsMessagesList(ticket_uuid)
  return response
}

/**
 * createDjangoCfgSupportTicketsMessages
 *
 * ViewSet for managing support messages.
 *
 * @method POST
 * @path /django_cfg_support/tickets/{ticket_uuid}/messages/
 */
export async function createDjangoCfgSupportTicketsMessages(
  ticket_uuid: string, data: MessageCreateRequest,
  client?: API
): Promise<MessageCreate> {
  const api = client || getAPIInstance()

  const response = await api.cfg_support.ticketsMessagesCreate(ticket_uuid, data)
  return MessageCreateSchema.parse(response)
}

/**
 * getDjangoCfgSupportTicketsMessagesById
 *
 * ViewSet for managing support messages.
 *
 * @method GET
 * @path /django_cfg_support/tickets/{ticket_uuid}/messages/{uuid}/
 */
export async function getDjangoCfgSupportTicketsMessagesById(
  ticket_uuid: string, uuid: string,
  client?: API
): Promise<Message> {
  const api = client || getAPIInstance()

  const response = await api.cfg_support.ticketsMessagesRetrieve(ticket_uuid, uuid)
  return MessageSchema.parse(response)
}

/**
 * updateDjangoCfgSupportTicketsMessages
 *
 * ViewSet for managing support messages.
 *
 * @method PUT
 * @path /django_cfg_support/tickets/{ticket_uuid}/messages/{uuid}/
 */
export async function updateDjangoCfgSupportTicketsMessages(
  ticket_uuid: string, uuid: string, data: MessageRequest,
  client?: API
): Promise<Message> {
  const api = client || getAPIInstance()

  const response = await api.cfg_support.ticketsMessagesUpdate(ticket_uuid, uuid, data)
  return MessageSchema.parse(response)
}

/**
 * partialUpdateDjangoCfgSupportTicketsMessages
 *
 * ViewSet for managing support messages.
 *
 * @method PATCH
 * @path /django_cfg_support/tickets/{ticket_uuid}/messages/{uuid}/
 */
export async function partialUpdateDjangoCfgSupportTicketsMessages(
  ticket_uuid: string, uuid: string,
  client?: API
): Promise<Message> {
  const api = client || getAPIInstance()

  const response = await api.cfg_support.ticketsMessagesPartialUpdate(ticket_uuid, uuid)
  return MessageSchema.parse(response)
}

/**
 * deleteDjangoCfgSupportTicketsMessages
 *
 * ViewSet for managing support messages.
 *
 * @method DELETE
 * @path /django_cfg_support/tickets/{ticket_uuid}/messages/{uuid}/
 */
export async function deleteDjangoCfgSupportTicketsMessages(
  ticket_uuid: string, uuid: string,
  client?: API
): Promise<void> {
  const api = client || getAPIInstance()

  const response = await api.cfg_support.ticketsMessagesDestroy(ticket_uuid, uuid)
  return response
}

/**
 * getDjangoCfgSupportTicketsById
 *
 * ViewSet for managing support tickets.
 *
 * @method GET
 * @path /django_cfg_support/tickets/{uuid}/
 */
export async function getDjangoCfgSupportTicketsById(
  uuid: string,
  client?: API
): Promise<Ticket> {
  const api = client || getAPIInstance()

  const response = await api.cfg_support.ticketsRetrieve(uuid)
  return TicketSchema.parse(response)
}

/**
 * updateDjangoCfgSupportTickets
 *
 * ViewSet for managing support tickets.
 *
 * @method PUT
 * @path /django_cfg_support/tickets/{uuid}/
 */
export async function updateDjangoCfgSupportTickets(
  uuid: string, data: TicketRequest,
  client?: API
): Promise<Ticket> {
  const api = client || getAPIInstance()

  const response = await api.cfg_support.ticketsUpdate(uuid, data)
  return TicketSchema.parse(response)
}

/**
 * partialUpdateDjangoCfgSupportTickets
 *
 * ViewSet for managing support tickets.
 *
 * @method PATCH
 * @path /django_cfg_support/tickets/{uuid}/
 */
export async function partialUpdateDjangoCfgSupportTickets(
  uuid: string,
  client?: API
): Promise<Ticket> {
  const api = client || getAPIInstance()

  const response = await api.cfg_support.ticketsPartialUpdate(uuid)
  return TicketSchema.parse(response)
}

/**
 * deleteDjangoCfgSupportTickets
 *
 * ViewSet for managing support tickets.
 *
 * @method DELETE
 * @path /django_cfg_support/tickets/{uuid}/
 */
export async function deleteDjangoCfgSupportTickets(
  uuid: string,
  client?: API
): Promise<void> {
  const api = client || getAPIInstance()

  const response = await api.cfg_support.ticketsDestroy(uuid)
  return response
}

