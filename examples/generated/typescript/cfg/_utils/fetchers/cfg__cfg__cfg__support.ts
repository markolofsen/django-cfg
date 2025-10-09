/**
 * Typed fetchers for Cfg Support
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
 * getCfgSupportTicketsList
 *
 * ViewSet for managing support tickets.
 *
 * @method GET
 * @path /cfg/support/tickets/
 */
export async function getCfgSupportTicketsList(
  client?: API
): Promise<any> {
  const api = client || getAPIInstance()

  const response = await api.cfg__support.cfgSupportTicketsList()
  return response
}

/**
 * createCfgSupportTickets
 *
 * ViewSet for managing support tickets.
 *
 * @method POST
 * @path /cfg/support/tickets/
 */
export async function createCfgSupportTickets(
  data: TicketRequest,
  client?: API
): Promise<Ticket> {
  const api = client || getAPIInstance()

  const response = await api.cfg__support.cfgSupportTicketsCreate(data)
  return TicketSchema.parse(response)
}

/**
 * getCfgSupportTicketsMessagesList
 *
 * ViewSet for managing support messages.
 *
 * @method GET
 * @path /cfg/support/tickets/{ticket_uuid}/messages/
 */
export async function getCfgSupportTicketsMessagesList(
  ticket_uuid: string,
  client?: API
): Promise<any> {
  const api = client || getAPIInstance()

  const response = await api.cfg__support.cfgSupportTicketsMessagesList(ticket_uuid)
  return response
}

/**
 * createCfgSupportTicketsMessages
 *
 * ViewSet for managing support messages.
 *
 * @method POST
 * @path /cfg/support/tickets/{ticket_uuid}/messages/
 */
export async function createCfgSupportTicketsMessages(
  ticket_uuid: string, data: MessageCreateRequest,
  client?: API
): Promise<MessageCreate> {
  const api = client || getAPIInstance()

  const response = await api.cfg__support.cfgSupportTicketsMessagesCreate(ticket_uuid, data)
  return MessageCreateSchema.parse(response)
}

/**
 * getCfgSupportTicketsMessagesById
 *
 * ViewSet for managing support messages.
 *
 * @method GET
 * @path /cfg/support/tickets/{ticket_uuid}/messages/{uuid}/
 */
export async function getCfgSupportTicketsMessagesById(
  ticket_uuid: string, uuid: string,
  client?: API
): Promise<Message> {
  const api = client || getAPIInstance()

  const response = await api.cfg__support.cfgSupportTicketsMessagesRetrieve(ticket_uuid, uuid)
  return MessageSchema.parse(response)
}

/**
 * updateCfgSupportTicketsMessages
 *
 * ViewSet for managing support messages.
 *
 * @method PUT
 * @path /cfg/support/tickets/{ticket_uuid}/messages/{uuid}/
 */
export async function updateCfgSupportTicketsMessages(
  ticket_uuid: string, uuid: string, data: MessageRequest,
  client?: API
): Promise<Message> {
  const api = client || getAPIInstance()

  const response = await api.cfg__support.cfgSupportTicketsMessagesUpdate(ticket_uuid, uuid, data)
  return MessageSchema.parse(response)
}

/**
 * partialUpdateCfgSupportTicketsMessages
 *
 * ViewSet for managing support messages.
 *
 * @method PATCH
 * @path /cfg/support/tickets/{ticket_uuid}/messages/{uuid}/
 */
export async function partialUpdateCfgSupportTicketsMessages(
  ticket_uuid: string, uuid: string,
  client?: API
): Promise<Message> {
  const api = client || getAPIInstance()

  const response = await api.cfg__support.cfgSupportTicketsMessagesPartialUpdate(ticket_uuid, uuid)
  return MessageSchema.parse(response)
}

/**
 * deleteCfgSupportTicketsMessages
 *
 * ViewSet for managing support messages.
 *
 * @method DELETE
 * @path /cfg/support/tickets/{ticket_uuid}/messages/{uuid}/
 */
export async function deleteCfgSupportTicketsMessages(
  ticket_uuid: string, uuid: string,
  client?: API
): Promise<void> {
  const api = client || getAPIInstance()

  const response = await api.cfg__support.cfgSupportTicketsMessagesDestroy(ticket_uuid, uuid)
  return response
}

/**
 * getCfgSupportTicketsById
 *
 * ViewSet for managing support tickets.
 *
 * @method GET
 * @path /cfg/support/tickets/{uuid}/
 */
export async function getCfgSupportTicketsById(
  uuid: string,
  client?: API
): Promise<Ticket> {
  const api = client || getAPIInstance()

  const response = await api.cfg__support.cfgSupportTicketsRetrieve(uuid)
  return TicketSchema.parse(response)
}

/**
 * updateCfgSupportTickets
 *
 * ViewSet for managing support tickets.
 *
 * @method PUT
 * @path /cfg/support/tickets/{uuid}/
 */
export async function updateCfgSupportTickets(
  uuid: string, data: TicketRequest,
  client?: API
): Promise<Ticket> {
  const api = client || getAPIInstance()

  const response = await api.cfg__support.cfgSupportTicketsUpdate(uuid, data)
  return TicketSchema.parse(response)
}

/**
 * partialUpdateCfgSupportTickets
 *
 * ViewSet for managing support tickets.
 *
 * @method PATCH
 * @path /cfg/support/tickets/{uuid}/
 */
export async function partialUpdateCfgSupportTickets(
  uuid: string,
  client?: API
): Promise<Ticket> {
  const api = client || getAPIInstance()

  const response = await api.cfg__support.cfgSupportTicketsPartialUpdate(uuid)
  return TicketSchema.parse(response)
}

/**
 * deleteCfgSupportTickets
 *
 * ViewSet for managing support tickets.
 *
 * @method DELETE
 * @path /cfg/support/tickets/{uuid}/
 */
export async function deleteCfgSupportTickets(
  uuid: string,
  client?: API
): Promise<void> {
  const api = client || getAPIInstance()

  const response = await api.cfg__support.cfgSupportTicketsDestroy(uuid)
  return response
}

