/**
 * Zod schema for PaginatedOrderListList
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod'
import { OrderListSchema } from './OrderList.schema'

export const PaginatedOrderListListSchema = z.object({
  count: z.number().int(),
  page: z.number().int(),
  pages: z.number().int(),
  page_size: z.number().int(),
  has_next: z.boolean(),
  has_previous: z.boolean(),
  next_page: z.number().int().optional(),
  previous_page: z.number().int().optional(),
  results: z.array(OrderListSchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaginatedOrderListList = z.infer<typeof PaginatedOrderListListSchema>