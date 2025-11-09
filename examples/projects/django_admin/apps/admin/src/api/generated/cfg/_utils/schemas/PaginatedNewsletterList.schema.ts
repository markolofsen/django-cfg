/**
 * Zod schema for PaginatedNewsletterList
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod'
import { NewsletterSchema } from './Newsletter.schema'

export const PaginatedNewsletterListSchema = z.object({
  count: z.int(),
  page: z.int(),
  pages: z.int(),
  page_size: z.int(),
  has_next: z.boolean(),
  has_previous: z.boolean(),
  next_page: z.int().nullable().optional(),
  previous_page: z.int().nullable().optional(),
  results: z.array(NewsletterSchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaginatedNewsletterList = z.infer<typeof PaginatedNewsletterListSchema>