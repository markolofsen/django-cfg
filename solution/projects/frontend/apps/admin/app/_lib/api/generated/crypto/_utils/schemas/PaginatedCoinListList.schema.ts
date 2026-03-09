/**
 * Zod schema for PaginatedCoinListList
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod'
import { CoinListSchema } from './CoinList.schema'

export const PaginatedCoinListListSchema = z.object({
  count: z.number().int(),
  page: z.number().int(),
  pages: z.number().int(),
  page_size: z.number().int(),
  has_next: z.boolean(),
  has_previous: z.boolean(),
  next_page: z.number().int().nullable().optional(),
  previous_page: z.number().int().nullable().optional(),
  results: z.array(CoinListSchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaginatedCoinListList = z.infer<typeof PaginatedCoinListListSchema>