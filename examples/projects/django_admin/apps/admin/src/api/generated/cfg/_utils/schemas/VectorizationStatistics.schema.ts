/**
 * Zod schema for VectorizationStatistics
 *
 * This schema provides runtime validation and type inference.
 *  * Vectorization statistics serializer.
 *  */
import { z } from 'zod'

/**
 * Vectorization statistics serializer.
 */
export const VectorizationStatisticsSchema = z.object({
  total_chunks: z.int(),
  vectorized_chunks: z.int(),
  pending_chunks: z.int(),
  vectorization_rate: z.number(),
  total_tokens: z.int(),
  total_cost: z.number(),
  avg_tokens_per_chunk: z.number(),
  avg_cost_per_chunk: z.number(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type VectorizationStatistics = z.infer<typeof VectorizationStatisticsSchema>