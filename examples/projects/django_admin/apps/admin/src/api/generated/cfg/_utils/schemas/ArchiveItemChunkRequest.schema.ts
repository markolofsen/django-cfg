/**
 * Zod schema for ArchiveItemChunkRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Archive item chunk serializer.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'

/**
 * Archive item chunk serializer.
 */
export const ArchiveItemChunkRequestSchema = z.object({
  content: z.string().min(1),
  chunk_index: z.int().min(0.0).max(2147483647.0),
  chunk_type: z.nativeEnum(Enums.ArchiveItemChunkRequestChunkType).optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ArchiveItemChunkRequest = z.infer<typeof ArchiveItemChunkRequestSchema>