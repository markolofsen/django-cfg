/**
 * Zod schema for PatchedTicketRequest
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'

export const PatchedTicketRequestSchema = z.object({
  user: z.int().optional(),
  subject: z.string().min(1).max(255).optional(),
  status: z.nativeEnum(Enums.PatchedTicketRequestStatus).optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PatchedTicketRequest = z.infer<typeof PatchedTicketRequestSchema>