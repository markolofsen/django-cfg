/**
 * Zod schema for DocumentStats
 *
 * This schema provides runtime validation and type inference.
 *  * Document processing statistics serializer.
 *  */
import { z } from 'zod'

/**
 * Document processing statistics serializer.
 */
export const DocumentStatsSchema = z.object({
  total_documents: z.int(),
  completed_documents: z.int(),
  processing_success_rate: z.number(),
  total_chunks: z.int(),
  total_tokens: z.int(),
  total_cost_usd: z.number(),
  avg_processing_time_seconds: z.number(),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type DocumentStats = z.infer<typeof DocumentStatsSchema>