/**
 * Zod schema for ApiKeyStats
 *
 * This schema provides runtime validation and type inference.
 *  * API Key usage statistics.
 *  */
import { z } from 'zod'

/**
 * API Key usage statistics.
 */
export const ApiKeyStatsSchema = z.object({
  total_keys: z.int(),
  active_keys: z.int(),
  expired_keys: z.int(),
  total_requests: z.int(),
  keys_by_type: z.record(z.string(), z.int()),
})

/**
 * Infer TypeScript type from Zod schema
 */
export type ApiKeyStats = z.infer<typeof ApiKeyStatsSchema>