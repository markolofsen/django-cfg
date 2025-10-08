/**
 * Zod schema for PaginatedEmailLogList
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod'
import { EmailLogSchema } from './EmailLog.schema'

export const PaginatedEmailLogListSchema = z.object({
  count: z.number().int(),
  page: z.number().int(),
  pages: z.number().int(),
  page_size: z.number().int(),
  has_next: z.boolean(),
  has_previous: z.boolean(),
  next_page: z.number().int().optional().nullable(),
  previous_page: z.number().int().optional().nullable(),
  results: z.array(EmailLogSchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaginatedEmailLogList = z.infer<typeof PaginatedEmailLogListSchema>