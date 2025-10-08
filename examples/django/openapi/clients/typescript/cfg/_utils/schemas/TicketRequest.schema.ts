/**
 * Zod schema for TicketRequest
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'

export const TicketRequestSchema = z.object({
  user: z.number().int(),
  subject: z.string().min(1).max(255),
  status: z.nativeEnum(Enums.TicketRequestStatus).optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type TicketRequest = z.infer<typeof TicketRequestSchema>