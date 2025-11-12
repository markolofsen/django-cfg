/**
 * Zod schema for ArchiveItemChunk
 *
 * This schema provides runtime validation and type inference.
 *  * Archive item chunk serializer.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'

/**
 * Archive item chunk serializer.
 */
export const ArchiveItemChunkSchema = z.object({
  id: z.uuid(),
  content: z.string(),
  chunk_index: z.int().min(0.0).max(2147483647.0),
  chunk_type: z.nativeEnum(Enums.ArchiveItemChunkChunkType).optional(),
  token_count: z.int(),
  character_count: z.int(),
  embedding_model: z.string(),
  embedding_cost: z.number(),
  context_summary: z.record(z.string(), z.record(z.string(), z.any())),
  created_at: z.iso.datetime(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ArchiveItemChunk = z.infer<typeof ArchiveItemChunkSchema>