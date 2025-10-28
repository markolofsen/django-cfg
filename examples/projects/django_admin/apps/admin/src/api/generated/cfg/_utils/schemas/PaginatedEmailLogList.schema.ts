/**
 * Zod schema for PaginatedEmailLogList
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod'
import { EmailLogSchema } from './EmailLog.schema'

export const PaginatedEmailLogListSchema = z.object({
  count: z.int(),
  page: z.int(),
  pages: z.int(),
  page_size: z.int(),
  has_next: z.boolean(),
  has_previous: z.boolean(),
  next_page: z.int().nullable().optional(),
  previous_page: z.int().nullable().optional(),
  results: z.array(EmailLogSchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaginatedEmailLogList = z.infer<typeof PaginatedEmailLogListSchema>