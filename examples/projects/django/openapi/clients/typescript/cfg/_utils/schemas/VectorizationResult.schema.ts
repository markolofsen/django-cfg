/**
 * Zod schema for VectorizationResult
 *
 * This schema provides runtime validation and type inference.
 *  * Vectorization result serializer.
 *  */
import { z } from 'zod'

/**
 * Vectorization result serializer.
 */
export const VectorizationResultSchema = z.object({
  vectorized_count: z.int(),
  failed_count: z.int(),
  total_tokens: z.int(),
  total_cost: z.number(),
  success_rate: z.number(),
  errors: z.array(z.string()),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type VectorizationResult = z.infer<typeof VectorizationResultSchema>