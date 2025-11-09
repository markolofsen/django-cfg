/**
 * Zod schema for ArchiveStatistics
 *
 * This schema provides runtime validation and type inference.
 *  * Archive statistics serializer.
 *  */
import { z } from 'zod'

/**
 * Archive statistics serializer.
 */
export const ArchiveStatisticsSchema = z.object({
  total_archives: z.int(),
  processed_archives: z.int(),
  failed_archives: z.int(),
  total_items: z.int(),
  total_chunks: z.int(),
  total_tokens: z.int(),
  total_cost: z.number(),
  avg_processing_time: z.number(),
  avg_items_per_archive: z.number(),
  avg_chunks_per_archive: z.number(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ArchiveStatistics = z.infer<typeof ArchiveStatisticsSchema>