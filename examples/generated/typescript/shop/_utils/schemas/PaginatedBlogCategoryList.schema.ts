/**
 * Zod schema for PaginatedBlogCategoryList
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod'
import { BlogCategorySchema } from './BlogCategory.schema'

export const PaginatedBlogCategoryListSchema = z.object({
  count: z.number().int(),
  page: z.number().int(),
  pages: z.number().int(),
  page_size: z.number().int(),
  has_next: z.boolean(),
  has_previous: z.boolean(),
  next_page: z.number().int().optional().nullable(),
  previous_page: z.number().int().optional().nullable(),
  results: z.array(BlogCategorySchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaginatedBlogCategoryList = z.infer<typeof PaginatedBlogCategoryListSchema>