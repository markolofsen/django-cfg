/**
 * Zod schema for PaginatedRecentPaymentList
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod'
import { RecentPaymentSchema } from './RecentPayment.schema'

export const PaginatedRecentPaymentListSchema = z.object({
  count: z.number().int(),
  page: z.number().int(),
  pages: z.number().int(),
  page_size: z.number().int(),
  has_next: z.boolean(),
  has_previous: z.boolean(),
  next_page: z.number().int().optional().nullable(),
  previous_page: z.number().int().optional().nullable(),
  results: z.array(RecentPaymentSchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaginatedRecentPaymentList = z.infer<typeof PaginatedRecentPaymentListSchema>