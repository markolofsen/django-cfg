/**
 * Zod schema for PaginatedArchiveItemList
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod'
import { ArchiveItemSchema } from './ArchiveItem.schema'

export const PaginatedArchiveItemListSchema = z.object({
  count: z.int(),
  page: z.int(),
  pages: z.int(),
  page_size: z.int(),
  has_next: z.boolean(),
  has_previous: z.boolean(),
  next_page: z.int().nullable().optional(),
  previous_page: z.int().nullable().optional(),
  results: z.array(ArchiveItemSchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaginatedArchiveItemList = z.infer<typeof PaginatedArchiveItemListSchema>