/**
 * Zod schema for PaginatedNewsletterList
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod'
import { NewsletterSchema } from './Newsletter.schema'

export const PaginatedNewsletterListSchema = z.object({
  count: z.number().int(),
  page: z.number().int(),
  pages: z.number().int(),
  page_size: z.number().int(),
  has_next: z.boolean(),
  has_previous: z.boolean(),
  next_page: z.number().int().optional(),
  previous_page: z.number().int().optional(),
  results: z.array(NewsletterSchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaginatedNewsletterList = z.infer<typeof PaginatedNewsletterListSchema>