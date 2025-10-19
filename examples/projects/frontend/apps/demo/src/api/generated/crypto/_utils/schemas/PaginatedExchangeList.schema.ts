/**
 * Zod schema for PaginatedExchangeList
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod'
import { ExchangeSchema } from './Exchange.schema'

export const PaginatedExchangeListSchema = z.object({
  count: z.int(),
  page: z.int(),
  pages: z.int(),
  page_size: z.int(),
  has_next: z.boolean(),
  has_previous: z.boolean(),
  next_page: z.int().nullable().optional(),
  previous_page: z.int().nullable().optional(),
  results: z.array(ExchangeSchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaginatedExchangeList = z.infer<typeof PaginatedExchangeListSchema>