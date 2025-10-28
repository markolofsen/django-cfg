/**
 * Zod schema for PaginatedCoinListList
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod'
import { CoinListSchema } from './CoinList.schema'

export const PaginatedCoinListListSchema = z.object({
  count: z.int(),
  page: z.int(),
  pages: z.int(),
  page_size: z.int(),
  has_next: z.boolean(),
  has_previous: z.boolean(),
  next_page: z.int().nullable().optional(),
  previous_page: z.int().nullable().optional(),
  results: z.array(CoinListSchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaginatedCoinListList = z.infer<typeof PaginatedCoinListListSchema>