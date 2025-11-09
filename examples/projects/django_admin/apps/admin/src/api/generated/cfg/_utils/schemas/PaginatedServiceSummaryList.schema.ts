/**
 * Zod schema for PaginatedServiceSummaryList
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod'
import { ServiceSummarySchema } from './ServiceSummary.schema'

export const PaginatedServiceSummaryListSchema = z.object({
  count: z.int(),
  page: z.int(),
  pages: z.int(),
  page_size: z.int(),
  has_next: z.boolean(),
  has_previous: z.boolean(),
  next_page: z.int().nullable().optional(),
  previous_page: z.int().nullable().optional(),
  results: z.array(ServiceSummarySchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaginatedServiceSummaryList = z.infer<typeof PaginatedServiceSummaryListSchema>