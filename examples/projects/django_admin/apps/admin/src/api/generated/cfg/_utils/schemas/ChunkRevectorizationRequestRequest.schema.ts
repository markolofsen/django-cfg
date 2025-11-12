/**
 * Zod schema for ChunkRevectorizationRequestRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Chunk re-vectorization request serializer.
 *  */
import { z } from 'zod'

/**
 * Chunk re-vectorization request serializer.
 */
export const ChunkRevectorizationRequestRequestSchema = z.object({
  chunk_ids: z.array(z.uuid()),
  force: z.boolean().optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ChunkRevectorizationRequestRequest = z.infer<typeof ChunkRevectorizationRequestRequestSchema>