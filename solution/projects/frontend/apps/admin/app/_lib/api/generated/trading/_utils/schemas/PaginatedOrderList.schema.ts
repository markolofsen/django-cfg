/**
 * Zod schema for PaginatedOrderList
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod'
import { OrderSchema } from './Order.schema'

export const PaginatedOrderListSchema = z.object({
  count: z.number().int(),
  page: z.number().int(),
  pages: z.number().int(),
  page_size: z.number().int(),
  has_next: z.boolean(),
  has_previous: z.boolean(),
  next_page: z.number().int().nullable().optional(),
  previous_page: z.number().int().nullable().optional(),
  results: z.array(OrderSchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaginatedOrderList = z.infer<typeof PaginatedOrderListSchema>