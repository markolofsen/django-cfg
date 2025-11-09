/**
 * Zod schema for ArchiveSearchResult
 *
 * This schema provides runtime validation and type inference.
 *  * Archive search result serializer.
 *  */
import { z } from 'zod'
import { ArchiveItemChunkSchema } from './ArchiveItemChunk.schema'

/**
 * Archive search result serializer.
 */
export const ArchiveSearchResultSchema = z.object({
  chunk: ArchiveItemChunkSchema,
  similarity_score: z.number(),
  context_summary: z.record(z.string(), z.any()),
  archive_info: z.record(z.string(), z.any()),
  item_info: z.record(z.string(), z.any()),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ArchiveSearchResult = z.infer<typeof ArchiveSearchResultSchema>