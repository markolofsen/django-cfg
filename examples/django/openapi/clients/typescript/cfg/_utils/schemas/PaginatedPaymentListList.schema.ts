/**
 * Zod schema for PaginatedPaymentListList
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod'
import { PaymentListSchema } from './PaymentList.schema'

export const PaginatedPaymentListListSchema = z.object({
  count: z.number().int(),
  page: z.number().int(),
  pages: z.number().int(),
  page_size: z.number().int(),
  has_next: z.boolean(),
  has_previous: z.boolean(),
  next_page: z.number().int().optional().nullable(),
  previous_page: z.number().int().optional().nullable(),
  results: z.array(PaymentListSchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaginatedPaymentListList = z.infer<typeof PaginatedPaymentListListSchema>