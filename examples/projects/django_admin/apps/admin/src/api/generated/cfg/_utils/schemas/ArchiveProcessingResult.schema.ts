/**
 * Zod schema for ArchiveProcessingResult
 *
 * This schema provides runtime validation and type inference.
 *  * Archive processing result serializer.
 *  */
import { z } from 'zod'

/**
 * Archive processing result serializer.
 */
export const ArchiveProcessingResultSchema = z.object({
  archive_id: z.uuid(),
  status: z.string(),
  processing_time_ms: z.int(),
  items_processed: z.int(),
  chunks_created: z.int(),
  vectorized_chunks: z.int(),
  total_cost_usd: z.number(),
  error_message: z.string(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ArchiveProcessingResult = z.infer<typeof ArchiveProcessingResultSchema>