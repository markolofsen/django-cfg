/**
 * Zod schema for PaginatedArchiveItemChunkList
 *
 * This schema provides runtime validation and type inference.
 *  */
import { z } from 'zod'
import { ArchiveItemChunkSchema } from './ArchiveItemChunk.schema'

export const PaginatedArchiveItemChunkListSchema = z.object({
  count: z.int(),
  page: z.int(),
  pages: z.int(),
  page_size: z.int(),
  has_next: z.boolean(),
  has_previous: z.boolean(),
  next_page: z.int().nullable().optional(),
  previous_page: z.int().nullable().optional(),
  results: z.array(ArchiveItemChunkSchema),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PaginatedArchiveItemChunkList = z.infer<typeof PaginatedArchiveItemChunkListSchema>