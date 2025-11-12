/**
 * Zod schema for PatchedArchiveItemChunkRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Archive item chunk serializer.
 *  */
import { z } from 'zod'
import * as Enums from '../../enums'

/**
 * Archive item chunk serializer.
 */
export const PatchedArchiveItemChunkRequestSchema = z.object({
  content: z.string().min(1).optional(),
  chunk_index: z.int().min(0.0).max(2147483647.0).optional(),
  chunk_type: z.nativeEnum(Enums.PatchedArchiveItemChunkRequestChunkType).optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type PatchedArchiveItemChunkRequest = z.infer<typeof PatchedArchiveItemChunkRequestSchema>