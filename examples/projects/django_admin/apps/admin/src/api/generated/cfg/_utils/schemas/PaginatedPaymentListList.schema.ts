/**
 * Zod schema for PaginatedPaymentListList
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod'
import { PaymentListSchema } from './PaymentList.schema'

export const PaginatedPaymentListListSchema = z.object({
  count: z.int(),
  page: z.int(),
  pages: z.int(),
  page_size: z.int(),
  has_next: z.boolean(),
  has_previous: z.boolean(),
  next_page: z.int().nullable().optional(),
  previous_page: z.int().nullable().optional(),
  results: z.array(PaymentListSchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaginatedPaymentListList = z.infer<typeof PaginatedPaymentListListSchema>