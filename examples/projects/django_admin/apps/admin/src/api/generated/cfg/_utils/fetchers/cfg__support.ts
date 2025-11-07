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
import { consola } from 'consola'
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

/**
 * API operation
 *
 * @method GET
 * @path /cfg/support/tickets/
 */
export async function getSupportTicketsList(  params?: { page?: number; page_size?: number },  client?: any
): Promise<PaginatedTicketList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_support.ticketsList(params?.page, params?.page_size)
  try {
    return PaginatedTicketListSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'getSupportTicketsList',
      message: `Path: /cfg/support/tickets/\nMethod: GET`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * API operation
 *
 * @method POST
 * @path /cfg/support/tickets/
 */
export async function createSupportTicketsCreate(  data: TicketRequest,  client?: any
): Promise<Ticket> {
  const api = client || getAPIInstance()
  const response = await api.cfg_support.ticketsCreate(data)
  try {
    return TicketSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'createSupportTicketsCreate',
      message: `Path: /cfg/support/tickets/\nMethod: POST`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * API operation
 *
 * @method GET
 * @path /cfg/support/tickets/{ticket_uuid}/messages/
 */
export async function getSupportTicketsMessagesList(  ticket_uuid: string, params?: { page?: number; page_size?: number },  client?: any
): Promise<PaginatedMessageList> {
  const api = client || getAPIInstance()
  const response = await api.cfg_support.ticketsMessagesList(ticket_uuid, params?.page, params?.page_size)
  try {
    return PaginatedMessageListSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'getSupportTicketsMessagesList',
      message: `Path: /cfg/support/tickets/{ticket_uuid}/messages/\nMethod: GET`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * API operation
 *
 * @method POST
 * @path /cfg/support/tickets/{ticket_uuid}/messages/
 */
export async function createSupportTicketsMessagesCreate(  ticket_uuid: string, data: MessageCreateRequest,  client?: any
): Promise<MessageCreate> {
  const api = client || getAPIInstance()
  const response = await api.cfg_support.ticketsMessagesCreate(ticket_uuid, data)
  try {
    return MessageCreateSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'createSupportTicketsMessagesCreate',
      message: `Path: /cfg/support/tickets/{ticket_uuid}/messages/\nMethod: POST`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * API operation
 *
 * @method GET
 * @path /cfg/support/tickets/{ticket_uuid}/messages/{uuid}/
 */
export async function getSupportTicketsMessagesRetrieve(  ticket_uuid: string, uuid: string,  client?: any
): Promise<Message> {
  const api = client || getAPIInstance()
  const response = await api.cfg_support.ticketsMessagesRetrieve(ticket_uuid, uuid)
  try {
    return MessageSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'getSupportTicketsMessagesRetrieve',
      message: `Path: /cfg/support/tickets/{ticket_uuid}/messages/{uuid}/\nMethod: GET`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * API operation
 *
 * @method PUT
 * @path /cfg/support/tickets/{ticket_uuid}/messages/{uuid}/
 */
export async function updateSupportTicketsMessagesUpdate(  ticket_uuid: string, uuid: string, data: MessageRequest,  client?: any
): Promise<Message> {
  const api = client || getAPIInstance()
  const response = await api.cfg_support.ticketsMessagesUpdate(ticket_uuid, uuid, data)
  try {
    return MessageSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'updateSupportTicketsMessagesUpdate',
      message: `Path: /cfg/support/tickets/{ticket_uuid}/messages/{uuid}/\nMethod: PUT`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * API operation
 *
 * @method PATCH
 * @path /cfg/support/tickets/{ticket_uuid}/messages/{uuid}/
 */
export async function partialUpdateSupportTicketsMessagesPartialUpdate(  ticket_uuid: string, uuid: string, data?: PatchedMessageRequest,  client?: any
): Promise<Message> {
  const api = client || getAPIInstance()
  const response = await api.cfg_support.ticketsMessagesPartialUpdate(ticket_uuid, uuid, data)
  try {
    return MessageSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'partialUpdateSupportTicketsMessagesPartialUpdate',
      message: `Path: /cfg/support/tickets/{ticket_uuid}/messages/{uuid}/\nMethod: PATCH`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * API operation
 *
 * @method DELETE
 * @path /cfg/support/tickets/{ticket_uuid}/messages/{uuid}/
 */
export async function deleteSupportTicketsMessagesDestroy(  ticket_uuid: string, uuid: string,  client?: any
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
export async function getSupportTicketsRetrieve(  uuid: string,  client?: any
): Promise<Ticket> {
  const api = client || getAPIInstance()
  const response = await api.cfg_support.ticketsRetrieve(uuid)
  try {
    return TicketSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'getSupportTicketsRetrieve',
      message: `Path: /cfg/support/tickets/{uuid}/\nMethod: GET`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * API operation
 *
 * @method PUT
 * @path /cfg/support/tickets/{uuid}/
 */
export async function updateSupportTicketsUpdate(  uuid: string, data: TicketRequest,  client?: any
): Promise<Ticket> {
  const api = client || getAPIInstance()
  const response = await api.cfg_support.ticketsUpdate(uuid, data)
  try {
    return TicketSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'updateSupportTicketsUpdate',
      message: `Path: /cfg/support/tickets/{uuid}/\nMethod: PUT`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * API operation
 *
 * @method PATCH
 * @path /cfg/support/tickets/{uuid}/
 */
export async function partialUpdateSupportTicketsPartialUpdate(  uuid: string, data?: PatchedTicketRequest,  client?: any
): Promise<Ticket> {
  const api = client || getAPIInstance()
  const response = await api.cfg_support.ticketsPartialUpdate(uuid, data)
  try {
    return TicketSchema.parse(response)
  } catch (error) {
    // Zod validation error - log detailed information
    consola.error('❌ Zod Validation Failed');
    consola.box({
      title: 'partialUpdateSupportTicketsPartialUpdate',
      message: `Path: /cfg/support/tickets/{uuid}/\nMethod: PATCH`,
      style: {
        borderColor: 'red',
        borderStyle: 'rounded'
      }
    });

    if (error instanceof Error && 'issues' in error && Array.isArray((error as any).issues)) {
      consola.error('Validation Issues:');
      (error as any).issues.forEach((issue: any, index: number) => {
        consola.error(`  ${index + 1}. ${issue.path.join('.') || 'root'}`);
        consola.error(`     ├─ Message: ${issue.message}`);
        if (issue.expected) consola.error(`     ├─ Expected: ${issue.expected}`);
        if (issue.received) consola.error(`     └─ Received: ${issue.received}`);
      });
    }

    consola.error('Response data:', response);

    // Re-throw the error
    throw error;
  }
}


/**
 * API operation
 *
 * @method DELETE
 * @path /cfg/support/tickets/{uuid}/
 */
export async function deleteSupportTicketsDestroy(  uuid: string,  client?: any
): Promise<void> {
  const api = client || getAPIInstance()
  const response = await api.cfg_support.ticketsDestroy(uuid)
  return response
}


