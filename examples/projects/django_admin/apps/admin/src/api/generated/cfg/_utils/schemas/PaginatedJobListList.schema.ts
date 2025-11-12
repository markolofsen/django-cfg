/**
 * Zod schema for PaginatedJobListList
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod'
import { JobListSchema } from './JobList.schema'

export const PaginatedJobListListSchema = z.object({
  count: z.int(),
  page: z.int(),
  pages: z.int(),
  page_size: z.int(),
  has_next: z.boolean(),
  has_previous: z.boolean(),
  next_page: z.int().nullable().optional(),
  previous_page: z.int().nullable().optional(),
  results: z.array(JobListSchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaginatedJobListList = z.infer<typeof PaginatedJobListListSchema>