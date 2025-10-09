/**
 * Zod schema for PaginatedAdminPaymentStatsList
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod'
import { AdminPaymentStatsSchema } from './AdminPaymentStats.schema'

export const PaginatedAdminPaymentStatsListSchema = z.object({
  count: z.number().int(),
  page: z.number().int(),
  pages: z.number().int(),
  page_size: z.number().int(),
  has_next: z.boolean(),
  has_previous: z.boolean(),
  next_page: z.number().int().optional(),
  previous_page: z.number().int().optional(),
  results: z.array(AdminPaymentStatsSchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaginatedAdminPaymentStatsList = z.infer<typeof PaginatedAdminPaymentStatsListSchema>