/**
 * Zod schema for PaginatedPublicCategoryList
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod'
import { PublicCategorySchema } from './PublicCategory.schema'

export const PaginatedPublicCategoryListSchema = z.object({
  count: z.int(),
  page: z.int(),
  pages: z.int(),
  page_size: z.int(),
  has_next: z.boolean(),
  has_previous: z.boolean(),
  next_page: z.int().nullable().optional(),
  previous_page: z.int().nullable().optional(),
  results: z.array(PublicCategorySchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaginatedPublicCategoryList = z.infer<typeof PaginatedPublicCategoryListSchema>