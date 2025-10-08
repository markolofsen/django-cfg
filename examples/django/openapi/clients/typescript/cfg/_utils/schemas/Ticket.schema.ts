/**
 * Zod schema for Ticket
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'

export const TicketSchema = z.object({
  uuid: z.string().uuid(),
  user: z.number().int(),
  subject: z.string().max(255),
  status: z.nativeEnum(Enums.TicketStatus).optional(),
  created_at: z.string().datetime(),
  unanswered_messages_count: z.number().int(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type Ticket = z.infer<typeof TicketSchema>