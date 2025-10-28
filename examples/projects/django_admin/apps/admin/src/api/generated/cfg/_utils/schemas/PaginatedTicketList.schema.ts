/**
 * Zod schema for PaginatedTicketList
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod'
import { TicketSchema } from './Ticket.schema'

export const PaginatedTicketListSchema = z.object({
  count: z.int(),
  page: z.int(),
  pages: z.int(),
  page_size: z.int(),
  has_next: z.boolean(),
  has_previous: z.boolean(),
  next_page: z.int().nullable().optional(),
  previous_page: z.int().nullable().optional(),
  results: z.array(TicketSchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaginatedTicketList = z.infer<typeof PaginatedTicketListSchema>