/**
 * Zod schema for PaginatedUserBalanceList
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod'
import { UserBalanceSchema } from './UserBalance.schema'

export const PaginatedUserBalanceListSchema = z.object({
  count: z.number().int(),
  page: z.number().int(),
  pages: z.number().int(),
  page_size: z.number().int(),
  has_next: z.boolean(),
  has_previous: z.boolean(),
  next_page: z.number().int().optional(),
  previous_page: z.number().int().optional(),
  results: z.array(UserBalanceSchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaginatedUserBalanceList = z.infer<typeof PaginatedUserBalanceListSchema>