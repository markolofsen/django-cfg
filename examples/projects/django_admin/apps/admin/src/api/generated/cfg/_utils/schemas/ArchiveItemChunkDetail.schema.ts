/**
 * Zod schema for ArchiveItemChunkDetail
 *
 * This schema provides runtime validation and type inference.
 *  * Detailed chunk serializer with full context.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'

/**
 * Detailed chunk serializer with full context.
 */
export const ArchiveItemChunkDetailSchema = z.object({
  id: z.uuid(),
  content: z.string(),
  chunk_index: z.int().min(0.0).max(2147483647.0),
  chunk_type: z.nativeEnum(Enums.ArchiveItemChunkDetailChunkType).optional(),
  token_count: z.int(),
  character_count: z.int(),
  embedding_model: z.string(),
  embedding_cost: z.number(),
  context_summary: z.record(z.string(), z.any()),
  created_at: z.iso.datetime(),
  context_metadata: z.string(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ArchiveItemChunkDetail = z.infer<typeof ArchiveItemChunkDetailSchema>