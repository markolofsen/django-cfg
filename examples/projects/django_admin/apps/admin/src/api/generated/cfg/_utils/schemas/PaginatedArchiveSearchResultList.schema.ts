/**
 * Zod schema for PaginatedArchiveSearchResultList
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod'
import { ArchiveSearchResultSchema } from './ArchiveSearchResult.schema'

export const PaginatedArchiveSearchResultListSchema = z.object({
  count: z.int(),
  page: z.int(),
  pages: z.int(),
  page_size: z.int(),
  has_next: z.boolean(),
  has_previous: z.boolean(),
  next_page: z.int().nullable().optional(),
  previous_page: z.int().nullable().optional(),
  results: z.array(ArchiveSearchResultSchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaginatedArchiveSearchResultList = z.infer<typeof PaginatedArchiveSearchResultListSchema>