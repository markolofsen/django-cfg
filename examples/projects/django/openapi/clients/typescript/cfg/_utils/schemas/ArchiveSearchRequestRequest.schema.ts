/**
 * Zod schema for ArchiveSearchRequestRequest
 *
 * This schema provides runtime validation and type inference.
 *  * Archive search request serializer.
 *  */
import { z } from 'zod'

/**
 * Archive search request serializer.
 */
export const ArchiveSearchRequestRequestSchema = z.object({
  query: z.string().min(1).max(500),
  content_types: z.array(z.string()).optional(),
  languages: z.array(z.string().min(1).max(50)).optional(),
  chunk_types: z.array(z.string()).optional(),
  archive_ids: z.array(z.uuid()).optional(),
  limit: z.int().min(1.0).max(50.0).optional(),
  similarity_threshold: z.number().min(0.0).max(1.0).optional(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ArchiveSearchRequestRequest = z.infer<typeof ArchiveSearchRequestRequestSchema>