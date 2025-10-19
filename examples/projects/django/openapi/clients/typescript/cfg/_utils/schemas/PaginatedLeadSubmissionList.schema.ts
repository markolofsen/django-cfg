/**
 * Zod schema for PaginatedLeadSubmissionList
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod'
import { LeadSubmissionSchema } from './LeadSubmission.schema'

export const PaginatedLeadSubmissionListSchema = z.object({
  count: z.int(),
  page: z.int(),
  pages: z.int(),
  page_size: z.int(),
  has_next: z.boolean(),
  has_previous: z.boolean(),
  next_page: z.int().nullable().optional(),
  previous_page: z.int().nullable().optional(),
  results: z.array(LeadSubmissionSchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaginatedLeadSubmissionList = z.infer<typeof PaginatedLeadSubmissionListSchema>