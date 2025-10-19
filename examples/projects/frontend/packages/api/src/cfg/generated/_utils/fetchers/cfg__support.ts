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
import { PaginatedMessageListSchema, type PaginatedMessageList } from '../schemas/PaginatedMessageList.schema'
import { PaginatedTicketListSchema, type PaginatedTicketList } from '../schemas/PaginatedTicketList.schema'
import { PatchedMessageRequestSchema, type PatchedMessageRequest } from '../schemas/PatchedMessageRequest.schema'
import { PatchedTicketRequestSchema, type PatchedTicketRequest } from '../schemas/PatchedTicketRequest.schema'
import { TicketSchema, type Ticket } from '../schemas/Ticket.schema'
import { TicketRequestSchema, type TicketRequest } from '../schemas/TicketRequest.schema'
import { getAPIInstance } from '../../api-instance'
import type { API } from '../../index'

/**
 * API operation
 *
 * @method GET
 * @path /cfg/support/tickets/
 */
export async function getSupportTicketsList(  params?: { page?: number; page_size?: number },  client?
): Promise<PaginatedTicketList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_support.ticketsList(params?.page, params?.page_size)
  return PaginatedTicketListSchema.parse(response)
}


/**
 * API operation
 *
 * @method POST
 * @path /cfg/support/tickets/
 */
export async function createSupportTicketsCreate(  data: TicketRequest,  client?
): Promise<Ticket> {
  const api = client || getAPIInstance()
  const response = await api.cfg_support.ticketsCreate(data)
  return TicketSchema.parse(response)
}


/**
 * API operation
 *
 * @method GET
 * @path /cfg/support/tickets/{ticket_uuid}/messages/
 */
export async function getSupportTicketsMessagesList(  ticket_uuid: string, params?: { page?: number; page_size?: number },  client?
): Promise<PaginatedMessageList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_support.ticketsMessagesList(ticket_uuid, params?.page, params?.page_size)
  return PaginatedMessageListSchema.parse(response)
}


/**
 * API operation
 *
 * @method POST
 * @path /cfg/support/tickets/{ticket_uuid}/messages/
 */
export async function createSupportTicketsMessagesCreate(  ticket_uuid: string, data: MessageCreateRequest,  client?
): Promise<MessageCreate> {
  const api = client || getAPIInstance()
  const response = await api.cfg_support.ticketsMessagesCreate(ticket_uuid, data)
  return MessageCreateSchema.parse(response)
}


/**
 * API operation
 *
 * @method GET
 * @path /cfg/support/tickets/{ticket_uuid}/messages/{uuid}/
 */
export async function getSupportTicketsMessagesRetrieve(  ticket_uuid: string, uuid: string,  client?
): Promise<Message> {
  const api = client || getAPIInstance()
  const response = await api.cfg_support.ticketsMessagesRetrieve(ticket_uuid, uuid)
  return MessageSchema.parse(response)
}


/**
 * API operation
 *
 * @method PUT
 * @path /cfg/support/tickets/{ticket_uuid}/messages/{uuid}/
 */
export async function updateSupportTicketsMessagesUpdate(  ticket_uuid: string, uuid: string, data: MessageRequest,  client?
): Promise<Message> {
  const api = client || getAPIInstance()
  const response = await api.cfg_support.ticketsMessagesUpdate(ticket_uuid, uuid, data)
  return MessageSchema.parse(response)
}


/**
 * API operation
 *
 * @method PATCH
 * @path /cfg/support/tickets/{ticket_uuid}/messages/{uuid}/
 */
export async function partialUpdateSupportTicketsMessagesPartialUpdate(  ticket_uuid: string, uuid: string, data?: PatchedMessageRequest,  client?
): Promise<Message> {
  const api = client || getAPIInstance()
  const response = await api.cfg_support.ticketsMessagesPartialUpdate(ticket_uuid, uuid, data)
  return MessageSchema.parse(response)
}


/**
 * API operation
 *
 * @method DELETE
 * @path /cfg/support/tickets/{ticket_uuid}/messages/{uuid}/
 */
export async function deleteSupportTicketsMessagesDestroy(  ticket_uuid: string, uuid: string,  client?
): Promise<void> {
  const api = client || getAPIInstance()
  const response = await api.cfg_support.ticketsMessagesDestroy(ticket_uuid, uuid)
  return response
}


/**
 * API operation
 *
 * @method GET
 * @path /cfg/support/tickets/{uuid}/
 */
export async function getSupportTicketsRetrieve(  uuid: string,  client?
): Promise<Ticket> {
  const api = client || getAPIInstance()
  const response = await api.cfg_support.ticketsRetrieve(uuid)
  return TicketSchema.parse(response)
}


/**
 * API operation
 *
 * @method PUT
 * @path /cfg/support/tickets/{uuid}/
 */
export async function updateSupportTicketsUpdate(  uuid: string, data: TicketRequest,  client?
): Promise<Ticket> {
  const api = client || getAPIInstance()
  const response = await api.cfg_support.ticketsUpdate(uuid, data)
  return TicketSchema.parse(response)
}


/**
 * API operation
 *
 * @method PATCH
 * @path /cfg/support/tickets/{uuid}/
 */
export async function partialUpdateSupportTicketsPartialUpdate(  uuid: string, data?: PatchedTicketRequest,  client?
): Promise<Ticket> {
  const api = client || getAPIInstance()
  const response = await api.cfg_support.ticketsPartialUpdate(uuid, data)
  return TicketSchema.parse(response)
}


/**
 * API operation
 *
 * @method DELETE
 * @path /cfg/support/tickets/{uuid}/
 */
export async function deleteSupportTicketsDestroy(  uuid: string,  client?
): Promise<void> {
  const api = client || getAPIInstance()
  const response = await api.cfg_support.ticketsDestroy(uuid)
  return response
}


